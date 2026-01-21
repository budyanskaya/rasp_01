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
## 1. Создаем все нужные для работы файлы: product_service.proto, server.py, client.py
> Сначала мы определяем контракт взаимодействия в .proto-файле, а потом уже на его основании пишем реализацию сервера и клиента 
<img width="182" height="191" alt="image" src="https://github.com/user-attachments/assets/454a27c7-048e-4fb2-a816-a0bfdf20e319" />

## 2. Обновляем пакеты и устанавливаем Python
> Обновляю список пакетов и устанавливаю Python3 с необходимыми компонентами для дальнейшей работы
```
sudo apt update
```
```
sudo apt install python3 python3-pip python3-venv -y
```

## 3. Создаём и активируем виртуальное окружение, в котором будем работать
> Перехожу в  заранее созданную рабочую папку rasp1, создаю виртуальное окружение venv и активирую его 
```
cd rasp1
```
```
python3 -m venv venv
```
```
source venv/bin/activate
```
<img width="433" height="62" alt="image" src="https://github.com/user-attachments/assets/9ae49b9e-5aa1-46ff-a41c-297649a9de0d" />

## 4. Устанавливаем зависимости
> Устанавливаем библиотеки, необходимые для разработки gRPC-сервиса, они позволяют генерировать код из .proto-файла и реализовать сервер с клиентом.
```
pip install grpcio grpcio-tools
```
<img width="897" height="192" alt="image" src="https://github.com/user-attachments/assets/5332356f-76e6-491e-9829-a93554c25e1c" />

## 5. Генерируем Python кода из proto-файла
> Генерируем Python-код из файла `product_service.proto`
```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. product_service.proto
```
> После выполнения этой команды у нас появятся файлы:
<img width="185" height="201" alt="image" src="https://github.com/user-attachments/assets/9341fa97-daa9-469b-8d07-693198d28407" />

## 6. Запуск сервера
> Запускаем gRPC-сервер, реализующий сервис «ProductCatalog» с методами `GetProduct` и `StreamProducts`.
```
python3 server.py
```
<img width="570" height="181" alt="image" src="https://github.com/user-attachments/assets/cf2e5ff8-7e4b-4d67-983e-3431b41f77ad" />

## 5. Запуск клиента
> Запускает клиент gRPC-сервиса, который тестирует оба метода — `GetProduct` и `StreamProducts`.
```
python3 client.py
```
<img width="686" height="683" alt="image" src="https://github.com/user-attachments/assets/2adb0485-c4dc-42a3-8930-dc761c0dc19c" />

## Анализ
> В системе реализован пункт для автоматического анализа времени выполнения каждого типа RPC
<img width="753" height="893" alt="Снимок экрана 2026-01-21 035031" src="https://github.com/user-attachments/assets/dbe6beba-6c8b-455f-a353-8ff1402a70d9" />
<img width="590" height="585" alt="Снимок экрана 2026-01-21 035104" src="https://github.com/user-attachments/assets/38b14f62-e94f-40e3-bcf3-59c251078354" />

>**Unary RPC (GetProduct):**
> Время выполнения отдельных вызовов:
> * ID=1: 0.0019 с
> * ID=2: 0.0013 с
> * ID=3: 0.0012 с
> * ID=4: 0.0008 с
> Среднее время для первых трёх (активных) товаров: 0.0018 с
> Последовательный вызов для 3 товаров: ~0.0054 с
>
> **Server Streaming RPC (StreamProducts):**
> Общее время получения 3 активных товаров: 1.7095 с
> Средняя скорость: 1.76 товара/сек
>
> **Анализ времени выполнения каждого типа RPC**
> Unary RPC работает значительно быстрее, так как это простой запрос–ответ без задержек.
> Streaming RPC искусственно замедлен из-за time.sleep(0.5) в сервере (по 0.5 секунды на товар → 3 × 0.5 = 1.5 с минимум), это объясняет высокое общее время.
> Streaming здесь не оптимизирован для скорости, а демонстрирует асинхронную потоковую передачу, а не массовое получение.
>
>**Анализ обработки ошибок (запрос несуществующего товара)**
> Система корректно обрабатывает запросы несуществующих товаров, при любом неизвестном `product_id` клиет показывает gRPC-статус `NOT_FOUND` с  сообщением «Товар с ID … не найден», а клиент отображает ошибку, код, детали и выдает рекомендацию — «Проверьте правильность ID товара». 
<img width="1457" height="242" alt="image" src="https://github.com/user-attachments/assets/b0f27a33-9ada-44e9-a8a0-c5cb26bc149f" />


# Вывод
В ходе работы реализован gRPC-сервис ProductCatalog с методами GetProduct (Unary) и StreamProducts (Server Streaming). Unary RPC работает быстро, Streaming  медленнее из-за искусственной задержки в коде, что соответствует цели демонстрации потоковой передачи. Ошибки при запросе несуществующих товаров обрабатываются корректно, клиент получает статус NOT_FOUND и понятное сообщение. 
