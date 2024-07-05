from collections import OrderedDict

from gevent import pywsgi
from geventwebsocket import Resource
from geventwebsocket.handler import WebSocketHandler

from med_sharing_system.adapters.notification_api import create_app, WebSocketApplication

app = create_app(api_prefix='/api/v1')


def run_notification_worker():
    http_server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    http_server.start()
    print("HTTP server started on 0.0.0.0:8000")

    ws_resource = Resource(OrderedDict([
        (r'/ws/(?P<client_id>\w+)', WebSocketApplication)
    ]))

    ws_server = pywsgi.WSGIServer(('0.0.0.0', 8001), ws_resource,
                                  handler_class=WebSocketHandler)
    print("WebSocket server starting...")
    ws_server.serve_forever()


if __name__ == "__main__":
    run_notification_worker()
