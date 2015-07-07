# -*- coding: utf-8 -*-
import time
import inspect
from collections import defaultdict
from functools import wraps


class PluginBase(type):
    """meta class of plugin"""
    _commands = defaultdict(list)

    class Command:
        def __init__(self, func, name=None, aliases=[], bubble=False):
            self.plugin = None
            self.func = func
            self.name = name or self.func.__name__
            self.description = self.func.__doc__
            self.spec = inspect.getargspec(self.func)
            self.aliases = aliases
            self.bubble = bubble

        def __repr__(self):
            return u'<Command {}>'.format(self.name).encode('utf-8')

    def __init__(cls, name, bases, attrs):
        super(PluginBase, cls).__init__(name, bases, attrs)

        for attr, obj in attrs.items():
            if not isinstance(obj, cls.Command):
                continue
            obj.plugin = cls
            cls._commands[obj.name].append(obj)
            for alias in obj.aliases:
                if alias == obj.name:
                    continue
                cls._commands[alias].append(obj)
            setattr(cls, attr, obj.func)


class Plugin(object):
    __metaclass__ = PluginBase

    def attach(self, bot):
        """do not override this"""
        self.bot = bot
        self.is_attached = True

    @property
    def handlers(self):
        return {item: getattr(self, item) for item in dir(self) \
                if item.startswith('on_')}

    @property
    def commands(self):
        return {name: cmd for name, cmds in PluginBase._commands.items()\
                if isinstance(self, cmd.plugin)}

    def send(self, channel, sentence, delay=0):
        self.bot.send(channel, sentence)

# method decorator for register command of Plugin class
def command(*args, **kwargs):
    func = None
    if len(args) == 1 and callable(args[0]):
        func = args[0]
    def decorator(*args, **kwargs):
        def wrapper(f):
            return PluginBase.Command(f, *args, **kwargs)
        return wrapper
    return PluginBase.Command(func) if func else\
           decorator(*args, **kwargs)
