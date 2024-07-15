from pydantic import BaseModel as BaseSchema, Field


class ClientId(BaseSchema):
    client_id: str = Field(..., example="client_1")
