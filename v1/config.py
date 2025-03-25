from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_user: str = "default"
    redis_password: str = ""
    code_length: int = 8
    admin_token: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
