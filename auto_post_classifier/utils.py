import uuid
import os


def generate_uuid():
    return "generated" + str(uuid.uuid4())

def get_var_from_env(var_name : str):
    try:
        return os.environ[var_name]
    except KeyError:
        return None