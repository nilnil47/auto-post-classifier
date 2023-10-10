from pydantic import BaseModel


class TaskBase(BaseModel):
    post: str
    prompt: str | None = None

    def build_prompt(self):
        self.prompt = f""" make a summery of the following post:
```
{self.post}
```
The result should be provided in a json format
"""
