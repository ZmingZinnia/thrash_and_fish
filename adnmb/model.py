from pydantic import BaseModel

class InfoLevel:
    INFO = 1
    ERROR = 2

class InfoModel(BaseModel):
    level: int
    text: str


class CategoryModel(BaseModel):
    content: str
    url: str


class ThreadModel(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author_email: str
    create_time: str
    url: str

    def to_post(self):
        return PostModel(post_id='unknow', title=self.title,
                    content=self.content, author_id=self.author_id,
                    author_email=self.author_email, create_time=self.create_time)

class PostModel(BaseModel):
    post_id: str
    title: str
    content: str
    author_id: str
    author_email: str
    create_time: str