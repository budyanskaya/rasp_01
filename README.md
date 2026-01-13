# Практическое задание №1. Реализация gRPC-сервиса
## Разработайте gRPC-сервис "ProductCatalog" для получения информации о товарах.
### Требуется реализовать:
* Proto-контракт с двумя методами: GetProduct (Unary RPC) и StreamProducts (Server Streaming RPC)
* Серверную часть с базой данных в памяти (минимум 3 товара)
* Клиентскую часть с вызовами обоих методов
### Проанализировать:
* Время выполнения каждого типа RPC
* Обработку ошибок (запрос несуществующего товара)
### Формат сдачи: product_service.proto, server.py, client.py
## Ход работы
### Сначала создаем все нужные для работы файлы: product_service.proto, server.py, client.py
<img width="182" height="131" alt="image" src="https://github.com/user-attachments/assets/c217e646-a272-4193-9899-674f1cb537e6" />

### Далее устанавливаем зависимости
```
pip install grpcio grpcio-tools
```
### Генерируем Python кода из proto-файла
```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product_service.proto
```
После выполнения этой команды у нас появятся файлы:
### Запуск сервера
```
python3 server.py
```
### Запуск клиента
```
python3 client.py
```

