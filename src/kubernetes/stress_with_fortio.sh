#!/bin/bash

# Устанавливаем Fortio (инструмент для нагрузочного тестирования) в пространство имен cinemaabyss
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/httpbin/sample-client/fortio-deploy.yaml -n cinemaabyss

# Получаем имя пода с Fortio и сохраняем его в переменную FORTIO_POD
export FORTIO_POD=$(kubectl get pod -n cinemaabyss | grep fortio | awk '{print $1}')

# Запускаем нагрузочное тестирование сервиса movies-service с параметрами:
# -c 50: 50 одновременных соединений
# -qps 0: без ограничения количества запросов в секунду
# -n 500: всего 500 запросов
# -loglevel Warning: выводить только предупреждения и ошибки
kubectl exec -n cinemaabyss $FORTIO_POD -c fortio -- fortio load -c 50 -qps 0 -n 500 -loglevel Warning http://movies-service:8081/api/movies

echo "-------------"
# Получаем статистику по ожидающим (pending) запросам к movies-service из sidecar-прокси Istio
# Это помогает проверить работу Circuit Breaker'а
kubectl exec -n cinemaabyss $FORTIO_POD -c istio-proxy -- pilot-agent request GET stats | grep movies-service | grep pending