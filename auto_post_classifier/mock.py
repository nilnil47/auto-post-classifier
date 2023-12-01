import functools
import json
import pathlib

RESPONSE_FILE_PATH: pathlib.Path = pathlib.Path("responses.txt")


def mock_openai_request(mock_response_path: pathlib.Path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Instead of running the function, return the mock value
            with open(mock_openai_request) as f:
                return json.load(f)

        return wrapper

    return decorator
    
