from slackbot.plugin import Plugin, command
try:
    from asteval import Interpreter
except ImportError:
    pass

class Python(Plugin):

    def on_attach(self, config):
        self.env = Interpreter()

    def on_message(self, message):
        # also text starts with '>>>' will be interpreted as python
        if message['text'].startswith('&gt;&gt;&gt;'):
            return self.py(message['text'][12:].strip())

    @command
    def py(self, *args):
        """evaluates python code
        ex) !py 1+1
        """
        line = u' '.join(args)
        print self.env.eval(line)
        return unicode(self.env.eval(line))
