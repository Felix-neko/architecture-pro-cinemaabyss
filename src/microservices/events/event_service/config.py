from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8001
    kafka_url: str = "localhost:9092"
    movies_event_topic: str = "movies_events"
    users_event_topic: str = "users_events"
    payments_event_topic: str = "payments_events"
    movies_consumer_group: str = "movies_event_group"
    users_consumer_group: str = "users_event_group"
    payments_consumer_group: str = "payments_event_group"


settings = Settings()