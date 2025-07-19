# Kong Canary Deployment для Сервисов Фильмов (DB-less режим)

Этот проект демонстрирует настройку канареечного развертывания (canary deployment) с использованием Kong API Gateway OSS v3.9 в DB-less режиме (без базы данных).

## 🎯 Возможности

- **Канареечное развертывание** между старым и новым сервисами фильмов
- **Weighted upstreams** для контроля процентного распределения трафика
- **DB-less режим** - простая настройка без базы данных
- **Декларативная конфигурация** через YAML файл
- **Мониторинг и логирование** запросов для анализа
- **Health checks** для контроля состояния сервисов
- **Kong Manager OSS** для визуального управления
- **Автоматизированные скрипты** для управления развертыванием

## 🚀 Быстрый старт

### 1. Настройка переменных окружения

Файл `.env` содержит значения по умолчанию для канареечного развертывания:

```bash
# Значения по умолчанию в .env файле
MIGRATE_TO_MOVIES=false          # Канареечное развертывание отключено
NEW_MOVIES_SERVICE_PERCENT=0      # 0% трафика на новый сервис
```

### 2. Автоматическая генерация kong.yml

Kong контейнер **автоматически генерирует** `kong.yml` из `kong.yml.template` при каждом запуске, используя переменные окружения.

### 3. Запуск системы

```bash
# Сделать entrypoint скрипт исполняемым
chmod +x kong-entrypoint.sh

# Запустить все сервисы (kong.yml будет сгенерирован автоматически)
docker-compose up -d

# Проверить статус
docker-compose ps

# Просмотр логов Kong (включая генерацию конфигурации)
docker-compose logs -f kong
```

### 3. Проверка работы

После запуска доступны следующие URL:

- **Kong Proxy (canary routing)**: http://localhost:8000/kong_requests_movies/
- **Kong Manager OSS**: http://localhost:8002
- **Kong Admin API**: http://localhost:8001
- **Old Movie Service (direct)**: http://localhost:8201
- **New Movie Service (direct)**: http://localhost:8202

**Быстрая проверка:**
```bash
# Проверка прямого доступа к сервисам
curl http://localhost:8201  # Старый сервис (должен показать v1.0)
curl http://localhost:8202  # Новый сервис (должен показать v2.0)

# Проверка маршрутизации через Kong (пока весь трафик на старый сервис)
curl http://localhost:8000/kong_requests_movies/
```

## 🔄 Управление канареечным развертыванием

### Способ 1: Изменение переменных окружения (рекомендуемый)

Kong **автоматически** генерирует новую конфигурацию при каждом запуске/перезапуске.

```bash
# Изменить переменные и перезапустить Kong
export MIGRATE_TO_MOVIES=true
export NEW_MOVIES_SERVICE_PERCENT=30
docker-compose restart kong

# Или в одну команду
MIGRATE_TO_MOVIES=true NEW_MOVIES_SERVICE_PERCENT=50 docker-compose restart kong

# Или изменить .env файл и перезапустить
echo "MIGRATE_TO_MOVIES=true" > .env
echo "NEW_MOVIES_SERVICE_PERCENT=75" >> .env
docker-compose restart kong
```

### Способ 2: Через скрипт управления (для быстрых изменений без перезапуска)

Сделайте скрипт исполняемым:
```bash
chmod +x canary-control.sh
```

Команды управления:
```bash
# Проверить текущее состояние
./canary-control.sh status

# Установить 30% трафика на новый сервис
./canary-control.sh set 30

# Постепенное развертывание до 100% с шагом 10% каждые 60 секунд
./canary-control.sh gradual 100 10 60

# Быстрый откат к старому сервису
./canary-control.sh rollback

# Полное переключение на новый сервис
./canary-control.sh complete

# Проверка здоровья сервисов
./canary-control.sh health
```

**Важно:** Изменения через canary-control.sh будут потеряны при перезапуске Kong. Для постоянных изменений используйте Способ 1.

### Способ 3: Через Kong Admin API напрямую

```bash
# Посмотреть текущие веса
curl -s http://localhost:8001/upstreams/movie-upstream/targets | jq .

# Установить 25% трафика на новый сервис (вес 25 для нового, 75 для старого)
# Найти ID целей
OLD_TARGET_ID=$(curl -s http://localhost:8001/upstreams/movie-upstream/targets | jq -r '.data[] | select(.target | contains("old-movie-service")) | .id')
NEW_TARGET_ID=$(curl -s http://localhost:8001/upstreams/movie-upstream/targets | jq -r '.data[] | select(.target | contains("new-movie-service")) | .id')

# Обновить веса
curl -X PATCH http://localhost:8001/upstreams/movie-upstream/targets/$OLD_TARGET_ID -d "weight=75"
curl -X PATCH http://localhost:8001/upstreams/movie-upstream/targets/$NEW_TARGET_ID -d "weight=25"
```

## 📊 Мониторинг

### Логи запросов

Kong логирует все запросы канареечного развертывания:
```bash
# Просмотр логов внутри контейнера Kong
docker exec kong tail -f /tmp/kong-movie-canary-requests.log
```

### Kong Manager OSS

Откройте http://localhost:8002 для визуального управления:
- Просмотр сервисов и маршрутов
- Управление плагинами
- Мониторинг состояния

### Заголовки ответов

Каждый ответ содержит отладочную информацию:
```
X-Served-By: kong-gateway
X-API-Version: v1
X-Canary-Enabled: true
X-Request-ID: uuid-запроса
```

## 🧪 Тестирование

### Быстрое тестирование различных сценариев

**Сценарий 1: Тестирование с 25% канареечного трафика**
```bash
# Автоматическая генерация при перезапуске
MIGRATE_TO_MOVIES=true NEW_MOVIES_SERVICE_PERCENT=25 docker-compose restart kong

# Альтернативно: временное изменение через Admin API (без перезапуска)
./canary-control.sh set 25

# Отправить несколько запросов для проверки распределения
for i in {1..20}; do
  curl -s http://localhost:8000/kong_requests_movies/ | grep -o "v1.0\|v2.0"
done
```

**Сценарий 2: Изменение через .env файл и автоматическую регенерацию**
```bash
# Отредактировать .env файл
echo "MIGRATE_TO_MOVIES=true" > .env
echo "NEW_MOVIES_SERVICE_PERCENT=50" >> .env

# Kong автоматически сгенерирует новую конфигурацию при перезапуске
docker-compose restart kong

# Проверить распределение 50/50
for i in {1..10}; do
  echo "Request $i: $(curl -s http://localhost:8000/kong_requests_movies/ | grep -o "СТАРЫЙ\|НОВЫЙ")"
done
```

**Сценарий 3: Пошаговое увеличение канареечного трафика**
```bash
# 10% канареечного трафика
MIGRATE_TO_MOVIES=true NEW_MOVIES_SERVICE_PERCENT=10 docker-compose restart kong
sleep 30

# 25% канареечного трафика  
NEW_MOVIES_SERVICE_PERCENT=25 docker-compose restart kong
sleep 30

# 50% канареечного трафика
NEW_MOVIES_SERVICE_PERCENT=50 docker-compose restart kong
sleep 30

# 100% канареечного трафика (полное переключение)
NEW_MOVIES_SERVICE_PERCENT=100 docker-compose restart kong
```

### Проверка распределения трафика

```bash
# Отправить 100 запросов для статистического анализа
for i in {1..100}; do
  curl -s http://localhost:8000/kong_requests_movies/ | grep -o "v1.0\|v2.0" >> results.txt
done

# Проанализировать результаты
echo "Старый сервис (v1.0): $(grep -c "v1.0" results.txt) запросов"
echo "Новый сервис (v2.0): $(grep -c "v2.0" results.txt) запросов"
rm results.txt
```

### Просмотр логов генерации конфигурации

```bash
# Посмотреть как Kong генерирует конфигурацию при запуске
docker-compose logs kong | grep "Kong Entrypoint"

# Пример вывода:
# [Kong Entrypoint] Канареечное развертывание ВКЛЮЧЕНО: 70% старый, 30% новый
# [Kong Entrypoint] kong.yml успешно сгенерирован
```

## 🔧 Конфигурация Kong

### Структура файлов

```
.
├── docker-compose.yml              # Основная конфигурация Docker
├── .env                           # Переменные окружения
├── kong.yml.template              # Шаблон конфигурации Kong с плейсхолдерами
├── kong-entrypoint.sh             # Скрипт автоматической генерации kong.yml при запуске Kong
├── generate-kong-config.sh        # Скрипт ручной генерации kong.yml из шаблона (опционально)
├── canary-control.sh              # Скрипт управления канареечным развертыванием
├── old_movies_response.html       # Ответ старого сервиса
├── new_movies_response.html       # Ответ нового сервиса
└── README.md                      # Эта документация
```

**Примечание:** `kong.yml` НЕ нужно создавать вручную - он автоматически генерируется из `kong.yml.template` при каждом запуске Kong контейнера.

### Плагины Kong

Используемые плагины:
- **pre-function**: Логика канареечного развертывания
- **response-transformer**: Добавление отладочных заголовков
- **file-log**: Логирование запросов
- **correlation-id**: Трейсинг запросов
- **rate-limiting**: Защита от перегрузки
- **proxy-cache**: Кеширование ответов

## 🐛 Устранение неисправностей

### Kong не запускается

```bash
# Проверить логи Kong
docker-compose logs kong

# Проверить правильность kong.yml
docker exec kong kong config parse /etc/kong/kong.yml

# Пересоздать контейнеры
docker-compose down
docker-compose up -d
```

### Канареечное развертывание не работает

```bash
# Проверить текущие веса в upstream
curl -s http://localhost:8001/upstreams/movie-upstream/targets | jq .

# Проверить конфигурацию Kong
curl -s http://localhost:8001/services | jq .
curl -s http://localhost:8001/routes | jq .

# Перезапустить Kong с обновленной конфигурацией
docker-compose restart kong
```

### Сервисы недоступны

```bash
# Проверить состояние контейнеров
docker-compose ps

# Проверить сетевую связность
docker exec kong ping old-movie-service
docker exec kong ping new-movie-service

# Проверить health checks
./canary-control.sh health
```

## 📈 Сценарии использования

### 1. Безопасное развертывание новой версии

```bash
# Начать с 5% трафика
./canary-control.sh set 5

# Мониторить метрики 10 минут
sleep 600

# Если все хорошо, увеличить до 25%
./canary-control.sh set 25

# Продолжить постепенное увеличение
./canary-control.sh gradual 100 25 300
```

### 2. A/B тестирование функций

```bash
# Разделить трафик 50/50 для A/B теста
./canary-control.sh set 50

# Собрать метрики в течение дня
# Проанализировать результаты

# Переключиться на лучшую версию
./canary-control.sh complete  # или rollback
```

### 3. Экстренный откат

```bash
# При обнаружении проблем немедленно откатиться
./canary-control.sh rollback

# Проверить, что весь трафик идет на стабильную версию
./canary-control.sh status
```

## 🔒 Безопасность

- Kong Manager OSS доступен без аутентификации в dev режиме
- Используйте HTTPS для внешних подключений в продакшене
- Настройте аутентификацию для Kong Admin API в продакшене
- Регулярно обновляйте Kong до последних версий

## 🤝 Интеграция

Этот setup можно интегрировать с:
- **CI/CD пайплайнами** (Jenkins, GitLab CI, GitHub Actions)
- **Системами мониторинга** (Prometheus, Grafana)
- **Уведомлениями** (Slack, Discord, email)
- **Service mesh** (Istio, Linkerd)
- **Kubernetes** (Kong Ingress Controller)

## 📝 Дополнительные ресурсы

- [Kong Gateway Documentation](https://docs.konghq.com/gateway/)
- [Kong Manager OSS](https://docs.konghq.com/gateway/latest/kong-manager-oss/)
- [Kong DB-less Mode](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [Canary Deployment Best Practices](https://martinfowler.com/bliki/CanaryRelease.html)

---

**Примечание**: Этот пример использует Kong OSS в DB-less режиме для простоты. Для продакшена с высокими требованиями к отказоустойчивости рассмотрите Kong с базой данных или Kong Enterprise.