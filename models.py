from typing import Optional

import typer
import rich
from pydantic import BaseModel


class TaskBase(BaseModel):
    post: str
    prompt: Optional[str] = None

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

The 'explanation' should give a reasoning for choosing the ranking.

The result should be provided as a JSON having the following format:
{{
    "weapons_exp": Explanation whether the post contains content related to weapons,
    "weapons_rnk": -1, 0 or 1 ranking of the weapons dimension,

    "violence_exp": Explanation whether the post contains content related to violence,
    "violence_rnk": -1, 0 or 1 ranking of the violence dimension,

    "political_exp": Explanation whether the post contains content related to politics,
    "political_rnk": -1, 0 or 1 ranking of the political content dimension
    
    "summary": summary of the post in max 3 lines
}}

```
{self.post}
```
"""