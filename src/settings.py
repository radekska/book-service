from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    database_echo_log: bool
    authjwt_header_name: str
    authjwt_header_type: str
    authjwt_secret_key: str
    authjwt_access_token_expires: int

    class Config:
        env_file = "src/.env"
        env_file_encoding = "utf-8"


settings = Settings()
