# -*- coding: utf-8 -*-
import os
import sys
import inspect
import types
import collections
import time
import csv
import logging
from import_file import import_file
from glob import glob
from Queue import PriorityQueue
from threading import Thread
from slackclient import SlackClient
from .plugin import Plugin, command

csv.register_dialect('cmdparser', delimiter=' ', quoting=csv.QUOTE_MINIMAL)
csv.register_dialect('pipe', delimiter='|', quoting=csv.QUOTE_MINIMAL)

def parse_command(s):
    s = s.encode('utf-8')
    st = [syntax for syntax in csv.reader([s], dialect='pipe').next() if syntax]
    for sentence in st:
        parsed = csv.reader([sentence], dialect='cmdparser').next()
        args = [arg.decode('utf-8') for arg in parsed if arg]
        if args:
            cmd = args.pop(0)
            yield (cmd, args)

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

class SlackBot(object):

    def __init__(self, config):
        self.log = logging.getLogger('slackbot')
        self.config = config
        self.client = SlackClient(config.get('TOKEN'))
        self.plugins = {}
        self.register_plugin(SystemPlugin())
        self.reload_plugins()

    def start(self):
        poller = Thread(target=self.main_loop, args=())
        try:
            poller.start()
            poller.join()
        except (KeyboardInterrupt, SystemExit):
            pass

    def main_loop(self):
        print 'bot started...'
        self.client.rtm_connect()
        counter = 0
        while True:
            for message in self.client.rtm_read():
                self.process_message(message)
                time.sleep(.1)
            counter += 1
            if counter >= 10:
                self.client.server.ping()
                counter = 0
            time.sleep(1)

    def process_message(self, message):
        if 'type' not in message:
            return
        prefix = self.config.get('COMMAND_PREFIX', '!')
        self.log.debug(message)
        # process command
        def find_plugin(cmd):
            for obj in self.plugins.values():
                if isinstance(obj, cmd.plugin):
                    return obj
        if message['type'] == 'message' and 'text' in message:
            if message['text'].startswith(prefix):
                for cmd, args in parse_command(message['text']):
                    if cmd[len(prefix):] in Plugin._commands:
                        commands = Plugin._commands[cmd]
                        for command in commands:
                            obj = find_plugin(command)
                            if obj:
                                result = command.func(obj, *args)
                                self.send(message['channel'], result) # XXX

        for _, plugin in self.plugins.items():
            evt = 'on_{0}'.format(message['type'])
            # process events
            if evt in plugin.handlers.keys():
                handler = getattr(plugin, evt)
                try:
                    result = handler(message)
                except:
                    continue
                if not result:
                    continue
                elif isinstance(result, (types.GeneratorType, collections.Iterator)):
                    for n, msg in enumerate(result):
                        self.send(message['channel'], msg)
                        time.sleep(max(n, 10) * .1) # XXX: blocking here..
                else:
                    self.send(message['channel'], result)

    def send(self, channel, text):
        channel = self.client.server.channels.find(channel)
        if channel:
            channel.send_message(text)

    def reload_plugins(self):
        """reload existing plugins"""

        # XXX: problem in import_file()d module. maybe caused by symlink?
        # M = lambda name: sys.modules.get(name)
        # modules = [m for m in list(set([M(plugin.__module__) \
        #         for plugin in self.plugins.values()])) if m != __name__]
        # print modules
        # map(self.register_plugin_module, [reload(module) for module in modules])

        # load new modules
        # TODO: omit duplicates
        for pyfile in glob('%s/*.py' % self.config.get('PLUGIN_DIR')):
            self.register_plugin_file(pyfile)

    def register_plugin(self, plugin):
        assert isinstance(plugin, Plugin)
        plugin.attach(self) # XXX: its dangerous
        ident = '{0}.{1}'.format(plugin.__class__.__module__,
            plugin.__class__.__name__)
        self.plugins[ident] = plugin
        try:
            if hasattr(plugin, 'on_attach'):
                plugin.on_attach(self.config)
        except:
            pass

    def register_plugin_file(self, path):
        module = import_file(path)
        self.register_plugin_module(module)

    def register_plugin_module(self, module):
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, Plugin):
                self.register_plugin(obj())


class SystemPlugin(Plugin):
    """default handler for mantain plugins and commands"""
    def on_attach(self, config):
        pass

    @command
    def help(self, plugin=None):
        """prints this help"""
        return u'help text comes here...'

    @command
    def cmd(self, name=None):
        """list available commands.
        for detailed instruction, type !cmd {command}
        """
        return u' '.join(Plugin._commands.keys())

    @command
    def plugin(self, cmd='list', *args):
        print 'self:', self
        if cmd == 'list':
            return 'print plugin list'
        elif cmd == 'reload':
            self.bot.reload_plugins()
            return 'reload all plugins'
