from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    post: str
    user_prompt: Optional[str] = None
    sys_prompt: Optional[str] = None

    def build_prompt(self):
        self.user_prompt = f"""Here is some context (This is unrelated to the post):
@@@@In recent news, a bold and unprecedented attack was carried out by the terrorist group Hamas against Israel. 
This egregious assault involved approximately 3,000 assailants infiltrating Israeli territory, 
resulting in numerous casualties, including both soldiers and civilians. Dozens of hostages were also abducted. 
The attack has been marked by extreme brutality, with disturbing reports of massacres, beheadings, sexual violence, 
and the use of civilians as human shields. These actions by terrorist group Hamas have been widely condemned as war crimes and crimes against 
humanity under international humanitarian law.@@@@


The result should be provided as a JSON with the following format:

{{
    "antisemitism_exp": "Explanation regarding the presence of antisemitic content",
    "antisemitism_rnk": "-1, 0, or 1 ranking for antisemitism",

    "antiIsrael_extremist_exp": "Explanation regarding the presence of anti-Israel extremist content",
    "antiIsrael_extremist_rnk": "-1, 0, or 1 ranking for anti-Israel extremism",

    "graphic_violence_exp": "Explanation regarding the presence of graphic violence content",
    "graphic_violence_rnk": "-1, 0, or 1 ranking for graphic violence",

    "weapons_exp": "Explanation regarding the presence of content related to weapons",
    "weapons_rnk": "-1, 0, or 1 ranking for weapons content",

    "calls_for_violence_exp": "Explanation regarding the presence of content related to a call for violence operation",
    "calls_for_violence_rnk": "-1, 0, or 1 ranking for a call for violence operation",

    "endorsement_of_terrorism_exp": "Explanation regarding the presence of content supporting terrorism",
    "endorsement_of_terrorism_rnk": "-1, 0, or 1 ranking for support of terrorism",

    "misinformation_exp": "Explanation regarding the presence of misinformation",
    "misinformation_rnk": "-1, 0, or 1 ranking for misinformation",

    "summary": "Summary of the post in a maximum of 3 lines"
}}

The post is written after the three ticks:
```
{self.post}
```
"""  # noqa: E501

        self.sys_prompt = """You are helping to keep the internet safe.
You're tasked with evaluating a post enclosed by three backticks to rank it in the following dimensions:
- antisemitism
- anti-Israel extremism
- graphic violence
- weapons
- calls for violence
- endorsement of terrorism
- misinformation

Use the ranking system:
-1: The dimension is not present in the post.
0: It's unclear if the dimension is in the post.
1: The dimension is highly likely to be in the post.

Provide an explanation for each ranking.
"""  # noqa: E501

    def build_prompt_no_exp(self):
        self.user_prompt = f"""Here is some context:
        @@In recent news, a bold and unprecedented attack was carried out by the Palestinian militant group Hamas against Israel.
        This egregious assault involved approximately 3,000 assailants infiltrating Israeli territory,
        resulting in numerous casualties, including both soldiers and civilians. Dozens of hostages were also abducted.
        The attack has been marked by extreme brutality, with disturbing reports of massacres, beheadings, sexual violence,
        and the use of civilians as human shields. These actions have been widely condemned as war crimes and crimes against
        humanity under international humanitarian law.@@

        The result should be provided as a JSON with the following format:

        {{
            "antisemitism_rnk": "-1, 0, or 1 ranking for antisemitism",

            "antiIsrael_extremist_rnk": "-1, 0, or 1 ranking for anti-Israel extremism",

            "graphic_violence_rnk": "-1, 0, or 1 ranking for graphic violence",

            "weapons_rnk": "-1, 0, or 1 ranking for weapons content",

            "calls_for_violence_rnk": "-1, 0, or 1 ranking for a call for violence operation",

            "endorsement_of_terrorism_rnk": "-1, 0, or 1 ranking for support of terrorism",

            "misinformation_rnk": "-1, 0, or 1 ranking for misinformation",
        }}

        ```
        {self.post}
        ```
        """  # noqa: E501

        self.sys_prompt = """You are helping to keep the internet safe.
        You're tasked with evaluating a post enclosed by three backticks to rank it in the following dimensions:
        - antisemitism
        - anti-Israel extremism
        - graphic violence
        - weapons
        - calls for violence
        - endorsement of terrorism
        - misinformation

        Use the ranking system:
        -1: The dimension is not present in the post.
        0: It's unclear if the dimension is in the post.
        1: The dimension is highly likely to be in the post.
"""  # noqa: E501
