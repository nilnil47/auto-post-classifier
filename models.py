from pydantic import BaseModel


class TaskBase(BaseModel):
    post: str
    prompt: str | None = None

    def build_prompt(self):
        self.prompt = f""" Provided with a post enclosed by three backticks you need to return a
ranking of the post in the following dimensions:
- weapons
- violence
- political content

For each dimension, use the following ranking:
-1 - means that the dimension is not contained in the post
0 - means that it is not clear whether the dimension is contained in the post
1 - means that the dimension is contained in the post with very high likelyhood

The result should be provided as a JSON having the following format:
```
{{
    'weapons': {{
        'explanation': Explanation whether the post contains content related to weapons,
        'ranking': -1, 0 or 1 ranking of the weapons dimension
    }},
    'violence': {{
        "explanation": Explanation whether the post contains content related to violence,
        'ranking': -1, 0 or 1 ranking of the violence dimension
    }},
    'political content': {{
        'explanation': Explanation whether the post contains content related to politics,
        'ranking': -1, 0 or 1 ranking of the political content dimension
    }}
}}

```
{self.post}
```
"""