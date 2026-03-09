from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Config(BaseSettings):
    epc_api_key: str
    companies_house_api_key: str
    openai_api_key: str
    google_api_key: str

    model_config = ConfigDict(env_file=".env")


def get_config() -> Config:
    return Config()
