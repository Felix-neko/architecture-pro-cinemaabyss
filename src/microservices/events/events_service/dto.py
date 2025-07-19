"""
Pydantic-модели:
- событий,
- запросов на создание событий,
- ответов на запросы.
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field


class MovieEvent(BaseModel):
    """
    Событие: действие с метаинформацией о фильме
    """

    movie_id: int = Field(description="Идентификатор фильма", example=1)
    title: str = Field(description="Название фильма", example="Inception")
    action: str = Field(description="Действие с фильмом", example="viewed")
    user_id: Optional[int] = Field(None, description="Идентификатор пользователя (опционально)", example=1)
    rating: Optional[float] = Field(None, description="Рейтинг (опционально)", example=8.5)
    genres: Optional[List[str]] = Field(None, description="Жанры фильма (опционально)", example=["Sci-Fi", "Action"])
    description: Optional[str] = Field(
        None, description="Описание фильма (опционально)", example="A mind-bending thriller"
    )


class UserEvent(BaseModel):
    """
    Событие: создание пользователя
    """

    user_id: int = Field(description="Идентификатор пользователя", example=1)
    username: Optional[str] = Field(None, description="Имя пользователя (опционально)", example="john_doe")
    email: Optional[str] = Field(None, description="Email пользователя (опционально)", example="john.doe@example.com")
    action: str = Field(description="Действие пользователя", example="registered")
    timestamp: str = Field(description="Время события", example="2023-01-15T14:30:00Z")


class PaymentEvent(BaseModel):
    """
    Событие: создание платежа
    """

    payment_id: int = Field(description="Идентификатор платежа", example=1)
    user_id: int = Field(description="Идентификатор пользователя", example=1)
    amount: float = Field(description="Сумма платежа", example=9.99)
    status: str = Field(description="Статус платежа", example="completed")
    timestamp: str = Field(description="Время платежа", example="2023-01-15T14:30:00Z")
    method_type: Optional[str] = Field(None, description="Тип метода оплаты (опционально)", example="credit_card")


# Response DTOs based on OpenAPI EventResponse schema
class MovieEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события фильма
    """

    status: str = Field(description="Статус операции", example="success")
    partition: int = Field(description="Партиция Kafka", example=0)
    offset: int = Field(description="Смещение в партиции Kafka", example=42)
    event: MovieEvent = Field(description="Данные события фильма")


class UserEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события пользователя
    """

    status: str = Field(description="Статус операции", example="success")
    partition: int = Field(description="Партиция Kafka", example=0)
    offset: int = Field(description="Смещение в партиции Kafka", example=42)
    event: UserEvent = Field(description="Данные события пользователя")


class PaymentEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события платежа
    """

    status: str = Field(description="Статус операции", example="success")
    partition: int = Field(description="Партиция Kafka", example=0)
    offset: int = Field(description="Смещение в партиции Kafka", example=42)
    event: PaymentEvent = Field(description="Данные события платежа")


class HealthCheckResponseInfo(BaseModel):
    """
    Ответ на запрос работоспособности сервиса
    """

    status: bool = Field(default=True, description="Работает ли сервис", example=True)
