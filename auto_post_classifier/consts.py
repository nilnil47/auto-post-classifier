from pathlib import Path

RESPONSE_PERSISTER_KEYS: list = [
    "antisemitism_exp",
    "antisemitism_rnk",
    "antiIsrael_extremist_exp",
    "antiIsrael_extremist_rnk",
    "graphic_violence_exp",
    "graphic_violence_rnk",
    "weapons_exp",
    "weapons_rnk",
    "calls_for_violence_exp",
    "calls_for_violence_rnk",
    "endorsement_of_terrorism_exp",
    "endorsement_of_terrorism_rnk",
    "misinformation_exp",
    "misinformation_rnk",
    "summary",
    "text",
    "uuid",
    "score",
    "error",
]

WEIGHTS: dict = {
    "antisemitism": 0.15,
    "graphic_violence": 0.15,
    "weapons": 0.10,
    "endorsement_of_terrorism": 0.10,
    "antiIsrael_extremist": 0.15,
    "calls_for_violence": 0.20,
    "misinformation": 0.20,
}

DEFULAT_ENV = {"RESPONSES_DIR": "../responses", "MOCK_FILE": None}


DEFAULT_INVALID_JSON_RESPONSES = "invalid_json_reponses"
DEFAULT_PROMPTS_PATH = "prompts"

GPT_PARSING_ERROR_FILE = "gpt_prasing_error"
GPT_NO_UUID_ERROR_FILE = "gpt_no_uuid_error"