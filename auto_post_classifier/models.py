from pydantic import BaseModel


class Post(BaseModel):
    text: str
    content_url: str
