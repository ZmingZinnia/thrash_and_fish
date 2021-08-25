from pydantic import BaseModel

class InfoLevel:
    INFO = 1
    ERROR = 2

class InfoModel(BaseModel):
    level: int
    text: str


class CategoryModel(BaseModel):
    name: str
    id: str


class ThreadModel(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author: str
    create_time: str

class PostModel(BaseModel):
    post_id: str
    title: str
    content: str
    author_id: str
    author: str
    create_time: str