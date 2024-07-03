from collections import defaultdict

import falcon
from geventwebsocket import (
    WebSocketApplication as BaseWebSocketApplication,
    WebSocketError
)
from geventwebsocket.handler import WebSocket

from .controllers import WebSocketNotification


class WebSocketApplication(BaseWebSocketApplication):
    clients: dict[str, list[WebSocket]] = defaultdict(list)

    def on_open(self):
        client_id = self.ws.environ['PATH_INFO'].split('/')[-1]
        self.clients[client_id].append(self.ws)
        print(f"Client {client_id} connected")

    def on_close(self, reason):
        client_id = self.ws.environ['PATH_INFO'].split('/')[-1]
        if client_id in self.clients:
            try:
                self.clients[client_id].remove(self.ws)
                print(f"Client {client_id}'s WebSocket removed")
                if not self.clients[client_id]:
                    del self.clients[client_id]
                    print(f"Client {client_id} has no more WebSockets, key removed")
            except ValueError:
                print(f"WebSocket not found in client {client_id}'s list")
        print(f"Client {client_id} disconnected")

    @classmethod
    def on_message(cls, message, *args, **kwargs):
        client_id = kwargs.get('client_id')
        if client_id is None:
            raise falcon.HTTPBadRequest

        client_copies: list[WebSocket | None] = cls.clients.get(client_id, [])
        for ws in client_copies:
            try:
                ws.send(message)
            except WebSocketError:
                client_copies.remove(ws)
        if not client_copies:
            del cls.clients[client_id]


def create_app(api_prefix: str) -> falcon.App:
    app = falcon.App()
    app.add_route(f'{api_prefix}/notify',
                  WebSocketNotification(WebSocketApplication))
    return app
