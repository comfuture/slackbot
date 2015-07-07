# -*- coding: utf-8 -*-
import requests
from slackbot.plugin import Plugin

API_ENDPOINT = 'http://api.simsimi.com/request.p'
SANDBOX_ENDPOINT = 'http://sandbox.api.simsimi.com/request.p'

class SimSimi(Plugin):

    def on_attach(self, config):
        self.key = config.get('SIMSIMI_KEY')
        if not self.key:
            # error message to owner
            pass

    def on_message(self, message):
        try:
            s = message['text']
            if u'이쁜이' in s or u'이쁘니' in s or \
                s.startswith(u'이쁜아') or s.startswith(u'이쁘나'):
                resp = requests.get('http://sandbox.api.simsimi.com/request.p',
                    params=dict(
                        key=KEY,
                        lc='ko',
                        text=s.replace(u'이쁜', u'심심'),
                        ft='1.0'
                    ))
                result = resp.json()
                if result['result'] == 100:
                    yield result['response']
                else:
                    yield u'흥 칫 뿡 [{}]'.format(result['msg'])
        except:
            pass
