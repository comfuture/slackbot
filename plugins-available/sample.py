from slackbot.plugin inmport Plugin, command

class MyPlugin(Plugin):

    @command
    def ping(self):
        # !ping
        return 'pong'

    @command('mycommand')
    def cmd(self):
        """prints 'this is mycommand'. trigger word is 'mycommand'"""
        return 'this is mycommand'

    @command(aliases=[u'날씨'])
    def weather(self, area=None):
        # !weather
        # !날씨
        # !날씨 서울
        return 'weather of {} is: amolang!'.format(area or 'Seoul')

    def on_message(self, message):
        """text event handler"""
        if 'text' not in message:
            return
        if message['text'].endswith('?'):
            return message['text'].split(' ').pop(0) + '!'
