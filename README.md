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
<img width="461" height="287" alt="image" src="https://github.com/user-attachments/assets/a01f503e-f96f-453d-9822-9817f62b30c3" />

### Генерируем Python кода из proto-файла
```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product_service.proto
```
После выполнения этой команды у нас появятся файлы:
<img width="168" height="167" alt="image" src="https://github.com/user-attachments/assets/a9f8e282-8eb3-4f6b-862f-46ea301035c2" />

### Запуск сервера
```
python3 server.py
```
<img width="520" height="387" alt="image" src="https://github.com/user-attachments/assets/9417f51b-4604-4ed1-8923-2a2c782491fb" />

### Запуск клиента
```
python3 client.py
```
<img width="513" height="370" alt="image" src="https://github.com/user-attachments/assets/31789f2c-0970-418c-8763-d451f19bb1f5" />

### Анализ
Анализ показал, что Unary RPC выполняется очень быстро (~0.001 с), тогда как Streaming RPC искусственно замедлен (time.sleep(0.5) между отправками) для демонстрации потоковой передачи — 4 товара получены за ~2.23 с. Это наглядно иллюстрирует разницу в моделях взаимодействия: Unary эффективен для единичных запросов, Streaming — для постепенной передачи множества элементов.

Обработка ошибок реализована корректно: при запросе несуществующего товара сервер возвращает статус NOT_FOUND, который клиент распознаёт и информативно отображает.

Работа подтверждает корректность применения gRPC для построения высокопроизводительных и типобезопасных сервисов.


