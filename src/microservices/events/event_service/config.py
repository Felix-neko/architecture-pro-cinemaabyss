from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8001
    kafka_url: str = "localhost:9092"

    movies_event_topic: str = "movie-events"
    users_event_topic: str = "user-events"
    payments_event_topic: str = "payment-events"

    movies_consumer_group: str = "movie-events-cgid"
    users_consumer_group: str = "user-event-cgid"
    payments_consumer_group: str = "payment-events-cgid"


settings = Settings()
