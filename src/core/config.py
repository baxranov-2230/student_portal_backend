import os

from pydantic_settings import BaseSettings , SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


# class Settings(BaseSettings):
#     DB_USER: str
#     DB_HOST: str
#     DB_PASSWORD: str
#     DB_PORT: str
#     DB_NAME: str
#     MODE: str
#
#     ACCESS_SECRET_KEY: str
#     REFRESH_SECRET_KEY : str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int
#     REFRESH_TOKEN_EXPIRE_DAYS: int
#     ALGORITHM: str
#
#     HEMIS_LOGIN_URL :str
#     HEMIS_USER : str
#     HEMIS_USER_GPA : str
#     HEMIS_USER_SUBJECT: str
#
#
#
#
#     @property
#     def connection_string(self):
#         return (
#             f'postgresql+asyncpg://'
#             f'{self.DB_USER}:'
#             f'{self.DB_PASSWORD}@'
#             f'{self.DB_HOST}:{self.DB_PORT}/'
#             f'{self.DB_NAME}'
#         )
#
#
#     model_config = SettingsConfigDict(env_file=".env")
#
# settings = Settings()


class Settings(BaseSettings):
    DB_USER: str = os.getenv('DB_USER')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_PORT: str = os.getenv('DB_PORT')
    DB_NAME: str = os.getenv('DB_NAME')

    SECRET_KEY: str = os.getenv('SECRET_KEY')
    REFRESH_SECRET_KEY: str = os.getenv('REFRESH_SECRET_KEY')
    ALGORITHM: str = os.getenv('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')

    HEMIS_LOGIN_URL :str=os.getenv('HEMIS_LOGIN_URL')
    HEMIS_USER : str=os.getenv('HEMIS_USER')
    HEMIS_USER_GPA : str=os.getenv('HEMIS_USER_GPA')
    HEMIS_USER_SUBJECT: str=os.getenv('HEMIS_USER_SUBJECT')

    @property
    def connection_string(self):
        values = self.model_dump()

        return (f'postgresql+asyncpg://'
                f'{values["DB_USER"]}:'
                f'{values["DB_PASSWORD"]}@'
                f'{values["DB_HOST"]}:{values["DB_PORT"]}/'
                f'{values["DB_NAME"]}')


settings = Settings()