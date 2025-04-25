from pydantic_settings import BaseSettings , SettingsConfigDict


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



    
    @property
    def connection_string(self):
        return (
            f'postgresql+asyncpg://'
            f'{self.DB_USER}:'
            f'{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/'
            f'{self.DB_NAME}'
        )


    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()