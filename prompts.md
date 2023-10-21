## generate json template for our promts

create a json template describe as the following:

dimensions:

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
1 - means that the dimension is contained in the post with very high likelyhood

The 'explanation' should give a reasoning for choosing the ranking.

The result should be provided as a JSON having the following format:

```
{{
    "*_exp": "Explanation whether the post contains content related to *",
    "*_rnk": "-1, 0 or 1 ranking of the * dimension",

    "summary": summary of the post in max 3 lines
}}

```

where \* is replace with each dimensions
