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

    movie_id: int = Field(description="Идентификатор фильма", examples=[1])
    title: str = Field(description="Название фильма", examples=["Inception"])
    action: str = Field(description="Действие с фильмом", examples=["viewed"])
    user_id: Optional[int] = Field(None, description="Идентификатор пользователя (опционально)", examples=[1])
    rating: Optional[float] = Field(None, description="Рейтинг (опционально)", examples=[8.5])
    genres: Optional[List[str]] = Field(None, description="Жанры фильма (опционально)", examples=[["Sci-Fi", "Action"]])
    description: Optional[str] = Field(
        None, description="Описание фильма (опционально)", examples=["A mind-bending thriller"]
    )


class UserEvent(BaseModel):
    """
    Событие: создание пользователя
    """

    user_id: int = Field(description="Идентификатор пользователя", examples=[1])
    username: Optional[str] = Field(None, description="Имя пользователя (опционально)", examples=["john_doe"])
    email: Optional[str] = Field(None, description="Email пользователя (опционально)", examples=["john.doe@example.com"])
    action: str = Field(description="Действие пользователя", examples=["registered"])
    timestamp: str = Field(description="Время события", examples=["2023-01-15T14:30:00Z"])


class PaymentEvent(BaseModel):
    """
    Событие: создание платежа
    """

    payment_id: int = Field(description="Идентификатор платежа", examples=[1])
    user_id: int = Field(description="Идентификатор пользователя", examples=[1])
    amount: float = Field(description="Сумма платежа", examples=[9.99])
    status: str = Field(description="Статус платежа", examples=["completed"])
    timestamp: str = Field(description="Время платежа", examples=["2023-01-15T14:30:00Z"])
    method_type: Optional[str] = Field(None, description="Тип метода оплаты (опционально)", examples=["credit_card"])


# Response DTOs based on OpenAPI EventResponse schema
class MovieEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события фильма
    """

    status: str = Field(description="Статус операции", examples=["success"])
    partition: int = Field(description="Партиция Kafka", examples=[0])
    offset: int = Field(description="Смещение в партиции Kafka", examples=[42])
    event: MovieEvent = Field(description="Данные события фильма")


class UserEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события пользователя
    """

    status: str = Field(description="Статус операции", examples=["success"])
    partition: int = Field(description="Партиция Kafka", examples=[0])
    offset: int = Field(description="Смещение в партиции Kafka", examples=[42])
    event: UserEvent = Field(description="Данные события пользователя")


class PaymentEventRegisterResponseInfo(BaseModel):
    """
    Ответ на регистрацию события платежа
    """

    status: str = Field(description="Статус операции", examples=["success"])
    partition: int = Field(description="Партиция Kafka", examples=[0])
    offset: int = Field(description="Смещение в партиции Kafka", examples=[42])
    event: PaymentEvent = Field(description="Данные события платежа")


class HealthCheckResponseInfo(BaseModel):
    """
    Ответ на запрос работоспособности сервиса
    """

    status: bool = Field(default=True, description="Работает ли сервис", examples=[True])
