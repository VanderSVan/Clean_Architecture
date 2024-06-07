import falcon
from pydantic import BaseModel
from spectree import SpecTree


class Server(BaseModel):
    url: str
    description: str


spectree = SpecTree(
    'falcon',
    mode='strict',
    annotations=True,
)


def setup_spectree(app: falcon.App,
                   title: str,
                   path: str,
                   filename: str,
                   servers: list[tuple[str, str]]
                   ) -> None:
    servers = [Server(url=url, description=description) for url, description in servers]
    config: dict = {
        'title': title,
        'path': path,
        'filename': filename,
        'servers': servers,
    }
    for key, value in config.items():
        setattr(spectree.config, key, value)

    spectree.register(app)
