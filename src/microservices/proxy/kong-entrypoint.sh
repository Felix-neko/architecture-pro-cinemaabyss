#!/bin/bash

# Kong entrypoint script для генерации kong.yml
# Этот скрипт выполняется при каждом запуске контейнера Kong

echo "Generating Kong config..."

# Получаем переменные окружения
# Убедимся, что значение числовое
export NEW_MOVIE_SERVICE_PERCENT=$((${MOVIES_MIGRATION_PERCENT:-0}))

# Проверяем процент
if [ "$NEW_MOVIE_SERVICE_PERCENT" -lt 0 ] || [ "$NEW_MOVIE_SERVICE_PERCENT" -gt 100 ]; then
    echo "[Kong Entrypoint] ПРЕДУПРЕЖДЕНИЕ: NEW_MOVIE_SERVICE_PERCENT должен быть от 0 до 100, установлен в 0"
    export NEW_MOVIE_SERVICE_PERCENT=0
fi
export OLD_MOVIE_SERVICE_PERCENT=$((100 - $NEW_MOVIE_SERVICE_PERCENT))

# Устанавливаем значения по умолчанию для URL сервисов
export MONOLITH_SERVICE_URL=${MONOLITH_SERVICE_URL:-localhost:8080}
export MOVIE_SERVICE_URL=${MOVIE_SERVICE_URL:-localhost:8081}
export EVENTS_SERVICE_URL=${EVENTS_SERVICE_URL:-localhost:8082}

echo "[Kong Entrypoint] Настройки сервисов:"
echo "- MONOLITH_SERVICE_URL: $MONOLITH_SERVICE_URL"
echo "- MOVIE_SERVICE_URL: $MOVIE_SERVICE_URL"
echo "- EVENTS_SERVICE_URL: $EVENTS_SERVICE_URL"
echo "- NEW_MOVIE_SERVICE_PERCENT: $NEW_MOVIE_SERVICE_PERCENT%"
echo "- OLD_MOVIE_SERVICE_PERCENT: $OLD_MOVIE_SERVICE_PERCENT%"

# И подставляем нужные переменные окружения в шаблон kong-конфигурации
echo "[Kong Entrypoint] Генерация конфигурации Kong..."
sed -e "s|\${OLD_MOVIE_SERVICE_PERCENT}|$OLD_MOVIE_SERVICE_PERCENT|g" \
    -e "s|\${NEW_MOVIE_SERVICE_PERCENT}|$NEW_MOVIE_SERVICE_PERCENT|g" \
    -e "s|\${MONOLITH_SERVICE_URL}|$MONOLITH_SERVICE_URL|g" \
    -e "s|\${MOVIE_SERVICE_URL}|$MOVIE_SERVICE_URL|g" \
    -e "s|\${EVENTS_SERVICE_URL}|$EVENTS_SERVICE_URL|g" \
    /etc/kong/kong.yml.template > /tmp/kong.yml

# Перемещаем сгенерированный конфиг на место
mv /tmp/kong.yml /etc/kong/kong.yml

# Проверяем корректность конфигурации
echo "[Kong Entrypoint] Проверяем конфигурацию..."
if ! kong config parse /etc/kong/kong.yml; then
    echo "[Kong Entrypoint] ОШИБКА: Невалидная конфигурация Kong"
    exit 1
fi

echo "[Kong Entrypoint] Запускаем Kong..."

# Запускаем Kong с помощью стандартного entrypoint
exec /docker-entrypoint.sh kong start