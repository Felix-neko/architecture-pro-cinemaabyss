FROM kong:3.9

# Копируем шаблон конфигурации и скрипты
COPY kong.yml.template /etc/kong/kong.yml.template
COPY --chmod=0755 kong-entrypoint.sh /usr/local/bin/kong-entrypoint.sh


# Устанавливаем переменные среды KONG_*
ENV KONG_DATABASE=off \
    KONG_DECLARATIVE_CONFIG=/etc/kong/kong.yml \
    KONG_PROXY_ACCESS_LOG=/dev/stdout \
    KONG_ADMIN_ACCESS_LOG=/dev/stdout \
    KONG_PROXY_ERROR_LOG=/dev/stderr \
    KONG_ADMIN_ERROR_LOG=/dev/stderr \
    KONG_ADMIN_LISTEN=0.0.0.0:8001 \
    KONG_ADMIN_GUI_LISTEN=0.0.0.0:8002 \
    KONG_ADMIN_GUI_URL=http://localhost:8002 \
    KONG_ANONYMOUS_REPORTS=false

# Устанавливаем entrypoint
ENTRYPOINT ["bash", "/usr/local/bin/kong-entrypoint.sh"]

# Открываем нужные порты
EXPOSE 8000 8443 8001 8002 8444
