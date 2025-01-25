from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_HOST: str = 'mysql'
    DATABASE_USER: str = 'root'
    DATABASE_PASSWORD: str = 'db2025'
    DATABASE_NAME: str = 'projektup'

    SECRET_KEY: str = os.urandom(32).hex()
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    KAFKA_BOOTSTRAP_SERVERS: str = 'kafka:9092'
    KAFKA_NOTIFICATION_TOPIC: str = 'notifications'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()