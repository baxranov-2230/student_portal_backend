from pydantic_settings import BaseSettings , SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    DB_USER: str 
    DB_HOST: str 
    DB_PASSWORD: str 
    DB_PORT: str 
    DB_NAME: str 
    MODE: str

    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY : str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    ALGORITHM: str

    HEMIS_LOGIN_URL :str
    HEMIS_USER : str
    HEMIS_USER_GPA : str
    HEMIS_USER_SUBJECT: str
    # HEMIS_USER_ATTENDANCE: str

    @property
    def connection_string(self):
        values = self.model_dump()
        return (f'postgresql+asyncpg://'
                f'{values["DB_USER"]}:'
                f'{values["DB_PASSWORD"]}@'
                f'{values["DB_HOST"]}:{values["DB_PORT"]}/'
                f'{values["DB_NAME"]}')


settings = Settings()