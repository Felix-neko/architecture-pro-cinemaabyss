#!/bin/bash

# Kong entrypoint script с автоматической генерацией kong.yml из шаблона
# Этот скрипт выполняется при каждом запуске контейнера Kong

set -e

echo "[Kong Entrypoint] Начинаем инициализацию Kong..."

# Получаем переменные окружения
MIGRATE_TO_MOVIES="${MIGRATE_TO_MOVIES:-false}"
NEW_MOVIE_SERVICE_PERCENT="${NEW_MOVIE_SERVICE_PERCENT:-0}"

echo "[Kong Entrypoint] Переменные окружения:"
echo "  MIGRATE_TO_MOVIES=${MIGRATE_TO_MOVIES}"
echo "  NEW_MOVIE_SERVICE_PERCENT=${NEW_MOVIE_SERVICE_PERCENT}"

# Проверяем процент
if [ "$NEW_MOVIE_SERVICE_PERCENT" -lt 0 ] || [ "$NEW_MOVIE_SERVICE_PERCENT" -gt 100 ]; then
    echo "[Kong Entrypoint] ПРЕДУПРЕЖДЕНИЕ: NEW_MOVIE_SERVICE_PERCENT должен быть от 0 до 100, установлен в 0"
    NEW_MOVIE_SERVICE_PERCENT=0
fi

# Вычисляем веса
if [ "$MIGRATE_TO_MOVIES" = "true" ]; then
    NEW_SERVICE_WEIGHT="$NEW_MOVIE_SERVICE_PERCENT"
    OLD_SERVICE_WEIGHT=$((100 - NEW_MOVIE_SERVICE_PERCENT))
    echo "[Kong Entrypoint] Канареечное развертывание ВКЛЮЧЕНО: ${OLD_SERVICE_WEIGHT}% старый, ${NEW_SERVICE_WEIGHT}% новый"
else
    NEW_SERVICE_WEIGHT=0
    OLD_SERVICE_WEIGHT=100
    echo "[Kong Entrypoint] Канареечное развертывание ОТКЛЮЧЕНО: 100% старый сервис"
fi

# Проверяем наличие шаблона
if [ ! -f "/etc/kong/kong.yml.template" ]; then
    echo "[Kong Entrypoint] ОШИБКА: файл kong.yml.template не найден в /etc/kong/"
    exit 1
fi

echo "[Kong Entrypoint] Генерируем kong.yml из шаблона..."

# Генерируем kong.yml из шаблона
sed -e "s/OLD_SERVICE_WEIGHT_PLACEHOLDER/${OLD_SERVICE_WEIGHT}/g" \
    -e "s/NEW_SERVICE_WEIGHT_PLACEHOLDER/${NEW_SERVICE_WEIGHT}/g" \
    -e "s/MIGRATE_TO_MOVIES_PLACEHOLDER/${MIGRATE_TO_MOVIES}/g" \
    -e "s/NEW_MOVIE_SERVICE_PERCENT_PLACEHOLDER/${NEW_MOVIE_SERVICE_PERCENT}/g" \
    /etc/kong/kong.yml.template > /etc/kong/kong.yml

echo "[Kong Entrypoint] kong.yml успешно сгенерирован"

# Показываем информацию о весах
echo "[Kong Entrypoint] Текущие веса в kong.yml:"
echo "  old-movie-service: ${OLD_SERVICE_WEIGHT}"
echo "  new-movie-service: ${NEW_SERVICE_WEIGHT}"

# Проверяем корректность сгенерированного файла
echo "[Kong Entrypoint] Проверяем корректность kong.yml..."
if kong config parse /etc/kong/kong.yml; then
    echo "[Kong Entrypoint] kong.yml прошел валидацию успешно"
else
    echo "[Kong Entrypoint] ОШИБКА: kong.yml содержит ошибки конфигурации"
    exit 1
fi

echo "[Kong Entrypoint] Запускаем Kong..."

# Запускаем Kong с оригинальными аргументами
exec kong docker-start "$@"