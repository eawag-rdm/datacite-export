"""Config file for datacite-export, using environment variables."""
import os
from functools import lru_cache
from typing import Optional

from dotenv import dotenv_values
from pydantic import BaseModel, AnyHttpUrl, ValidationError

import pathlib

def env_example_keys() -> list[str]:
    """Return list with strings of keys in 'env.example'"""
    with open("env.example") as file:
        equals_char = "="
        keys = [(line.rstrip()).split(equals_char)[0] for line in file]
    return keys


class ConfigAppModel(BaseModel):
    """Class with required app environment variables and their types."""

    APP_VERSION: str
    CORS_ORIGIN: AnyHttpUrl
    DEBUG: bool
    ROOT_PATH: Optional[str] = ""


@lru_cache
def get_config_app() -> ConfigAppModel | Exception:
    """Return config for app as object. Validate and cache environment variables.
    If system variable 'IS_DOCKER' is "True" then reads environment variables
    passed from Docker container, else reads local .env

    :return ConfigAppModel with valiated environment variables
        or Exception if validation fails
    """
    try:
        if os.getenv("IS_DOCKER") == "True":
            env_keys = env_example_keys()
            env_dict = {}
            for key in env_keys:
                if val := os.getenv(key):
                    env_dict[key] = val
        else:
            if pathlib.Path(".env").is_file():
                env_dict = dotenv_values(".env", verbose=True)
            else:
                env_dict = dotenv_values("env.example", verbose=True)

        _config = ConfigAppModel(**env_dict)
        return _config

    except ValidationError as e:
        raise Exception(f"Failed to validate environment variables, error(s): {e}")


config_app = get_config_app()


def get_log_level(debug: bool) -> str:
    """Return string used for log level of app.

    :param debug: Bool that indicates if debug mode is being used
    :return string: "DEBUG" or "WARNING"
    """
    if debug:
        return "DEBUG"
    return "WARNING"


log_level = get_log_level(config_app.DEBUG)
