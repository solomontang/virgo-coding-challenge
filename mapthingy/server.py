import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import httpclient
import os
import json
from urlparse import urlparse

ROOT = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(ROOT, 'templates')
STATIC_DIR = os.path.join(ROOT, 'static')
GOOGLE_MAPS_KEY = 'AIzaSyBZDgontArVnzdUGccBScTPYMQ7pzZnzas'
FREEGEOIP_URL_PATTERN = "http://freegeoip.net/json/%(host)s"


class APIHandler(tornado.websocket.WebSocketHandler):
    @classmethod
    def is_hostname(cls, s):
        """
        Should return True if the value is a string ending
        in a period, followed by a number of letters.
        """

        
        try:
          name = s.split('.')[-2:]
          float(name[1])
        except ValueError:
          return True
        else:
          return False


    def process_message(self, message):
        msg = json.loads(message)
        if msg['msg'] == 'getPosition':
            self.get_position(msg['payload'])

    def open(self):
        print("Client connected")

    def on_message(self, message):
        self.process_message(message)

    def on_close(self):
        print("WebSocket closed")

    def handle_request(self, res):
      if res.error:
        print('bad request')
      else:
        self.write_message({
              'msg': 'position',
              'payload': res.body.decode('utf-8')
          })

    def get_position(self, host_or_ip):
      client = httpclient.AsyncHTTPClient()
      client.fetch(FREEGEOIP_URL_PATTERN % {'host': host_or_ip}, self.handle_request)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", google_maps_key=GOOGLE_MAPS_KEY)

def make_app():
    settings = {
        'debug': True,
        'template_path': TEMPLATE_DIR
    }
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/wsapi/", APIHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, { 'path': STATIC_DIR })
        ], **settings
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
