import logging
from contextlib import asynccontextmanager
from typing import Optional
import json
import asyncio

import uvicorn
from fastapi import FastAPI, APIRouter, HTTPException, status as status_codes, Body
from aiokafka.consumer import AIOKafkaConsumer
from aiokafka.producer import AIOKafkaProducer

from events_service.config import settings
from events_service.dto import (
    PaymentEvent,
    MovieEvent,
    UserEvent,
    MovieEventRegisterResponseInfo,
    UserEventRegisterResponseInfo,
    PaymentEventRegisterResponseInfo,
    HealthCheckResponseInfo,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class NotImplementedHttpError(HTTPException):
    def __init__(self, detail: str = "This feature is not yet implemented"):
        super().__init__(status_code=status_codes.HTTP_501_NOT_IMPLEMENTED, detail=detail)


class EventServiceAPI(FastAPI):
    """
    Роутер для сервиса создания Kakfa-событий
    """

    def __init__(self, kafka_url: str = settings.kafka_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._kafka_url = kafka_url
        self._kafka_producer: Optional[AIOKafkaProducer] = None
        self._kafka_movies_consumer: Optional[AIOKafkaConsumer] = None
        self._kafka_users_consumer: Optional[AIOKafkaConsumer] = None
        self._kafka_payments_consumer: Optional[AIOKafkaConsumer] = None
        self._kafka_initialized: bool = False
        self._kafka_err_msg: Optional[str] = None

        @self.get("/api/events/health", tags=["health"])
        async def health_check() -> HealthCheckResponseInfo:
            """Проверка состояния сервиса"""
            return await self.health_check()

        @self.post("/api/events/movie", status_code=status_codes.HTTP_201_CREATED, tags=["events"])
        async def register_movie_event(event: MovieEvent = Body(embed=False)) -> MovieEventRegisterResponseInfo:
            """Регистрация события фильма"""
            return await self.register_movie_event(event)

        @self.post("/api/events/user", status_code=status_codes.HTTP_201_CREATED, tags=["events"])
        async def register_user_event(event: UserEvent = Body(embed=False)) -> UserEventRegisterResponseInfo:
            """Регистрация события пользователя"""
            return await self.register_user_event(event)

        @self.post("/api/events/payment", status_code=status_codes.HTTP_201_CREATED, tags=["events"])
        async def register_payment_event(event: PaymentEvent = Body(embed=False)) -> PaymentEventRegisterResponseInfo:
            """Регистрация события платежа"""
            return await self.register_payment_event(event)

    async def health_check(self) -> HealthCheckResponseInfo:
        return HealthCheckResponseInfo(status=self._kafka_initialized)

    async def register_movie_event(self, event: MovieEvent) -> MovieEventRegisterResponseInfo:
        """Публикация события фильма в Kafka"""
        if not self._kafka_initialized or not self._kafka_producer:
            raise HTTPException(
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE, detail="Kafka producer not initialized"
            )

        try:
            # Сериализуем событие в JSON
            event_json = json.dumps(event.model_dump(), ensure_ascii=False)

            # Отправляем в Kafka топик
            result = await self._kafka_producer.send_and_wait(settings.movies_event_topic, event_json.encode("utf-8"))

            logging.info(f"Movie event published to Kafka: {event.title}")
            return MovieEventRegisterResponseInfo(
                status="success", partition=result.partition, offset=result.offset, event=event
            )

        except Exception as e:
            logging.error(f"Failed to publish movie event: {e}")
            raise HTTPException(
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to publish event: {str(e)}"
            )

    async def register_payment_event(self, event: PaymentEvent) -> PaymentEventRegisterResponseInfo:
        """Публикация события платежа в Kafka"""
        if not self._kafka_initialized or not self._kafka_producer:
            raise HTTPException(
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE, detail="Kafka producer not initialized"
            )

        try:
            # Сериализуем событие в JSON
            event_json = json.dumps(event.model_dump(), ensure_ascii=False)

            # Отправляем в Kafka топик
            result = await self._kafka_producer.send_and_wait(settings.payments_event_topic, event_json.encode("utf-8"))

            logging.info(f"Payment event published to Kafka: {event.payment_id}")
            return PaymentEventRegisterResponseInfo(
                status="success", partition=result.partition, offset=result.offset, event=event
            )

        except Exception as e:
            logging.error(f"Failed to publish payment event: {e}")
            raise HTTPException(
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to publish event: {str(e)}"
            )

    async def register_user_event(self, event: UserEvent) -> UserEventRegisterResponseInfo:
        """Публикация события пользователя в Kafka"""
        if not self._kafka_initialized or not self._kafka_producer:
            raise HTTPException(
                status_code=status_codes.HTTP_503_SERVICE_UNAVAILABLE, detail="Kafka producer not initialized"
            )

        try:
            # Сериализуем событие в JSON
            event_json = json.dumps(event.model_dump(), ensure_ascii=False)

            # Отправляем в Kafka топик
            result = await self._kafka_producer.send_and_wait(settings.users_event_topic, event_json.encode("utf-8"))

            logging.info(f"User event published to Kafka: {event.user_id}")
            return UserEventRegisterResponseInfo(
                status="success", partition=result.partition, offset=result.offset, event=event
            )

        except Exception as e:
            logging.error(f"Failed to publish user event: {e}")
            raise HTTPException(
                status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to publish event: {str(e)}"
            )

    async def process_payment_event(self, payment_event: PaymentEvent):
        """Process payment event and log it"""
        logging.info(f"Processing payment event: {payment_event}")

    async def process_user_event(self, user_event: UserEvent):
        """Process user event and log it"""
        logging.info(f"Processing user event: {user_event}")

    async def process_movie_event(self, movie_event: MovieEvent):
        """Process movie event and log it"""
        logging.info(f"Processing movie event: {movie_event}")

    async def _consume_movie_events(self):
        """Background task to consume movie events"""
        try:
            async for message in self._kafka_movies_consumer:
                try:
                    event_data = json.loads(message.value.decode("utf-8"))
                    movie_event = MovieEvent(**event_data)
                    await self.process_movie_event(movie_event)
                except Exception as e:
                    logging.error(f"Error processing movie event: {e}")
        except Exception as e:
            logging.error(f"Error in movie events consumer: {e}")

    async def _consume_user_events(self):
        """Background task to consume user events"""
        try:
            async for message in self._kafka_users_consumer:
                try:
                    event_data = json.loads(message.value.decode("utf-8"))
                    user_event = UserEvent(**event_data)
                    await self.process_user_event(user_event)
                except Exception as e:
                    logging.error(f"Error processing user event: {e}")
        except Exception as e:
            logging.error(f"Error in user events consumer: {e}")

    async def _consume_payment_events(self):
        """Background task to consume payment events"""
        try:
            async for message in self._kafka_payments_consumer:
                try:
                    event_data = json.loads(message.value.decode("utf-8"))
                    payment_event = PaymentEvent(**event_data)
                    await self.process_payment_event(payment_event)
                except Exception as e:
                    logging.error(f"Error processing payment event: {e}")
        except Exception as e:
            logging.error(f"Error in payment events consumer: {e}")

    async def _check_kafka_ready(self, max_retries: int = 20, initial_delay: float = 10.0) -> bool:
        """
        Проверяет доступность Kafka-брокера с экспоненциальной задержкой между попытками.

        Args:
            max_retries: Максимальное количество попыток подключения
            initial_delay: Начальная задержка в секундах перед следующей попыткой

        Returns:
            bool: True если Kafka доступен, иначе False
        """

        delay = initial_delay
        for attempt in range(max_retries):
            try:
                # Пробуем создать временного продюсера для проверки подключения
                temp_producer = AIOKafkaProducer(bootstrap_servers=self._kafka_url)
                await temp_producer.start()
                await temp_producer.stop()
                logging.info("Successfully connected to Kafka broker")
                return True
            except Exception as e:
                if attempt == max_retries - 1:  # Последняя попытка
                    logging.error(f"Failed to connect to Kafka after {max_retries} attempts: {e}")
                    return False

                # Экспоненциальная задержка с джиттером для избежания "толпы"
                jitter = 1 + (0.1 * (1 - 2 * (hash(f"{id(self)}{attempt}") % 2) / 10.0))
                sleep_time = min(delay * jitter, 30)  # Максимальная задержка 30 секунд

                logging.warning(
                    f"Attempt {attempt + 1}/{max_retries} - Could not connect to Kafka at {self._kafka_url}. "
                    f"Retrying in {sleep_time:.2f} seconds... Error: {str(e)}"
                )

                await asyncio.sleep(sleep_time)
                delay *= 2  # Увеличиваем задержку в 2 раза для следующей попытки

        return False

    async def _initialize(self):
        """
        Инициализация kafka
        """
        try:
            logging.info("Initializing Kafka...")

            # Проверяем доступность Kafka брокера
            if not await self._check_kafka_ready():
                self._kafka_err_msg = "Failed to connect to Kafka broker after multiple attempts"
                logging.error(self._kafka_err_msg)
                raise ConnectionError(self._kafka_err_msg)

            self._kafka_producer = AIOKafkaProducer(bootstrap_servers=self._kafka_url)
            await self._kafka_producer.start()

            self._kafka_movies_consumer = AIOKafkaConsumer(
                settings.movies_event_topic,
                bootstrap_servers=self._kafka_url,
                group_id=settings.movies_consumer_group,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
            )
            await self._kafka_movies_consumer.start()

            self._kafka_users_consumer = AIOKafkaConsumer(
                settings.users_event_topic,
                bootstrap_servers=self._kafka_url,
                group_id=settings.users_consumer_group,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
            )
            await self._kafka_users_consumer.start()

            self._kafka_payments_consumer = AIOKafkaConsumer(
                settings.payments_event_topic,
                bootstrap_servers=self._kafka_url,
                group_id=settings.payments_consumer_group,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
            )
            await self._kafka_payments_consumer.start()

            self._kafka_initialized = True
            logging.info("Kafka initialized successfully")

            # Start background consumer tasks
            asyncio.create_task(self._consume_movie_events())
            asyncio.create_task(self._consume_user_events())
            asyncio.create_task(self._consume_payment_events())
            logging.info("Background consumer tasks started")

        except Exception as e:
            logging.error(e)
            self._kafka_err_msg = str(e)
            raise e


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize router and Kafka on startup
    await app._initialize()
    yield
    # Cleanup on shutdown
    if app._kafka_producer:
        await app._kafka_producer.stop()
    if app._kafka_movies_consumer:
        await app._kafka_movies_consumer.stop()
    if app._kafka_users_consumer:
        await app._kafka_users_consumer.stop()
    if app._kafka_payments_consumer:
        await app._kafka_payments_consumer.stop()


app = EventServiceAPI(
    title="Event Service",
    description="Сервис kafka-событий",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "events", "description": "Эндпоинты для регистрации событий"},
        {"name": "health", "description": "Проверки работоспособности"},
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port, log_level="info")
