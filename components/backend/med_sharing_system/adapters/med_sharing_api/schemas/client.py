from pydantic import BaseModel as BaseSchema


class ClientId(BaseSchema):
    client_id: str
