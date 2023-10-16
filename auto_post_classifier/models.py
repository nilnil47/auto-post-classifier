from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    post: str
    user_prompt: Optional[str] = None
    sys_prompt: Optional[str] = None


    def build_prompt(self):
        self.user_prompt = f""" 
        here is some context:
        ###
        In recent news, a brazen attack by the Palestinian militant group Hamas on Israel has sparked a major escalation in the Israeli-Palestinian conflict. This unprecedented attack involved around 1,000 assailants infiltrating Israeli territory, resulting in hundreds of casualties, including both soldiers and civilians, as well as the abduction of dozens of hostages. The attack has been characterized by its extreme brutality, with shocking reports of massacres, beheadings, sexual violence, and the use of civilians as human shields. These acts have been widely condemned as war crimes and crimes against humanity under international humanitarian law.
        ###
        
The result should be provided as a JSON having the following format:
{{

    "antisemitism_exp": "Explanation whether the post contains content related to antisemitism",
    "antisemitism_rnk": "-1, 0, or 1 ranking of the antisemitism dimension",

    "graphic_violence_exp": "Explanation whether the post contains content related to graphic violence",
    "graphic_violence_rnk": "-1, 0, or 1 ranking of the graphic violence dimension",

    "weapons_exp": "Explanation whether the post contains content related to weapons",
    "weapons_rnk": "-1, 0, or 1 ranking of the weapons dimension",

    "call_for_violence_operation_exp": "Explanation whether the post contains content related to a call for violence operation",
    "call_for_violence_operation_rnk": "-1, 0, or 1 ranking of the call for violence operation dimension",

    "political_content_exp": "Explanation whether the post contains political content",
    "political_content_rnk": "-1, 0, or 1 ranking of the political content dimension",

    "supporting_in_terror_exp": "Explanation whether the post contains content supporting terrorism",
    "supporting_in_terror_rnk": "-1, 0, or 1 ranking of the supporting in terror dimension",

    "misinformation_exp": "Explanation whether the post contains misinformation",
    "misinformation_rnk": "-1, 0, or 1 ranking of the misinformation dimension",

    "summary": "Summary of the post in max 3 lines"
}}

where * is replace with each dimensions
```
{self.post}
```
"""

        self.sys_prompt = """You are helping to keep the internet safe. 
Provided with a post enclosed by three backticks you need to return a
ranking of the post in the following dimensions:
- antisemitism
- graphic violence 
- weapons
- call for violence operation
- political content
- supporting in terror
- misinformation

For each dimension, use the following ranking:
-1 - means that the dimension is not contained in the post
0 - means that it is not clear whether the dimension is contained in the post
1 - means that the dimension is contained in the post with very high likelihood

The 'explanation' should give a reasoning for choosing the ranking.
"""