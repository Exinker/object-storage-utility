from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Config(BaseSettings):

    access_key: str = Field(..., alias='S3_ACCESS_KEY')
    secret_key: SecretStr = Field(..., alias='S3_ACCESS_SECRET')
    region_name: str = Field('us-east-1', alias='S3_REGION')
    endpoint_url: str = Field('http://localhost:9000', alias='S3_ENDPOINT')
    certificate_verify: bool = Field(True, alias='S3_CERTIFICATE_VERIFY')

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


S3_CONFIG = S3Config()
