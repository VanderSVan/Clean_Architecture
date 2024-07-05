import falcon
from geventwebsocket import WebSocketApplication

from med_sharing_system.application import dtos


class WebSocketNotification:
    def __init__(self, websocket_app: WebSocketApplication):
        self.websocket_app = websocket_app

    def on_post(self, req, resp):
        message = dtos.Message(**req.media)
        if message:
            self.websocket_app.on_message(message=message.body,
                                          client_id=message.target)
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_BAD_REQUEST
