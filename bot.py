import sys
import yaml
from argparse import ArgumentParser
from slackbot import SlackBot

if __name__ == '__main__':
    # XXX: read config from passed argument
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='path of config file',
        metavar='path', default='config.yaml')
    args = parser.parse_args()

    if not args.config:
        parser.print_help()
        sys.exit(0)

    try:
        with open(args.config) as f:
            config = yaml.load(f)
    except IOError:
        print 'No such file or broken file.'
        sys.exit(0)
    except yaml.YAMLError:
        print 'Error in config file.'
        sys.exit(0)
    bot = SlackBot(config)
    bot.start()
