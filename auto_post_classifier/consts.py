RESPONSE_PERSISTER_KEYS: list = [
    "antisemitism_exp",
    "antisemitism_rnk",
    "antiIsrael_extremist_exp",
    "antiIsrael_extremist_rnk",
    "antiZionism_extremist_exp",
    "antiZionism_extremist_rnk",
    "graphic_violence_exp",
    "graphic_violence_rnk",
    "pro_palestine_exp",
    "pro_palestine_rnk",
    "holocaust_exp",
    "holocaust_rnk",
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
    "graphic_violence": 0.10,
    "antiZionism_extremist": 0.10,
    "pro_palestine": 0.05,
    "endorsement_of_terrorism": 0.10,
    "antiIsrael_extremist": 0.10,
    "holocaust": 0.25,
    "misinformation": 0.15,
}

DEFULAT_ENV = {"RESPONSES_DIR": "../responses", "MOCK_FILE": None}


DEFAULT_INVALID_JSON_RESPONSES = "invalid_json_reponses"
DEFAULT_PROMPTS_PATH = "prompts"

GPT_PARSING_ERROR_FILE = "gpt_prasing_error"
GPT_NO_UUID_ERROR_FILE = "gpt_no_uuid_error"
