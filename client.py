client.py 
import grpc
import time
import logging
from typing import Optional
from datetime import datetime


import product_service_pb2 as pb2
import product_service_pb2_grpc as pb2_grpc


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductCatalogClient:
    
    def __init__(self, host: str = 'localhost', port: int = 50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = pb2_grpc.ProductCatalogServiceStub(self.channel)
        logger.info(f"Клиент подключен к {host}:{port}")
    
    def close(self):
        self.channel.close()
        logger.info("Соединение закрыто")
    
    def get_product(self, product_id: str) -> Optional[pb2.Product]:
        logger.info(f"=== Вызов GetProduct для product_id='{product_id}' ===")
        start_time = time.time()
        
        try:
            request = pb2.GetProductRequest(product_id=product_id)
            
            response = self.stub.GetProduct(request, timeout=10)
            
            elapsed_time = time.time() - start_time
            
            if response.id:
                logger.info(f"Товар найден за {elapsed_time:.4f} секунд")
                self._print_product_details(response)
                return response
            else:
                logger.warning(f"Товар с ID '{product_id}' не найден")
                return None
                
        except grpc.RpcError as e:
            elapsed_time = time.time() - start_time
            self._handle_grpc_error(e, "GetProduct", elapsed_time)
            return None
    
    def stream_products(self, include_inactive: bool = False):
        logger.info(f"=== Вызов StreamProducts (include_inactive={include_inactive}) ===")
        start_time = time.time()
        
        try:
            request = pb2.StreamProductsRequest(include_inactive=include_inactive)
            
            products_stream = self.stub.StreamProducts(request, timeout=30)
            
            received_count = 0
            logger.info("Начинаем получение товаров потоком...")
            
            for product in products_stream:
                received_count += 1
                logger.info(f"Получен товар #{received_count}: {product.name}")
                self._print_product_summary(product)
                
                time.sleep(0.2)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Получено {received_count} товаров за {elapsed_time:.4f} секунд")
            logger.info(f"Средняя скорость: {received_count/elapsed_time:.2f} товаров/сек")
            
        except grpc.RpcError as e:
            elapsed_time = time.time() - start_time
            self._handle_grpc_error(e, "StreamProducts", elapsed_time)
    
    def benchmark_rpc_types(self):
        logger.info("\n" + "="*50)
        logger.info("БЕНЧМАРК: Сравнение типов RPC")
        logger.info("="*50)
        
        unary_times = []
        test_ids = ["1", "2", "3", "4"]
        
        for pid in test_ids:
            start = time.time()
            self.get_product(pid)
            unary_times.append(time.time() - start)
        
        avg_unary = sum(unary_times[:-1]) / 3 if len(unary_times) > 3 else 0
        logger.info(f"\n Unary RPC (только успешные):")
        logger.info(f"   Среднее время: {avg_unary:.4f} сек")
        logger.info(f"   Всего запросов: {len(test_ids)}")
        
        logger.info(f"\n Streaming RPC:")
        start = time.time()
        self.stream_products(include_inactive=False)
        stream_time = time.time() - start
        
        logger.info(f"   Общее время: {stream_time:.4f} сек")
        
        logger.info(f"\n СРАВНЕНИЕ:")
        logger.info(f"   Unary для 3 товаров: {avg_unary*3:.4f} сек (последовательно)")
        logger.info(f"   Streaming 3 товаров: {stream_time:.4f} сек")
        
        if avg_unary > 0:
            efficiency = (avg_unary*3 - stream_time) / (avg_unary*3) * 100
            logger.info(f"   Эффективность streaming: {efficiency:.1f}%")
    
    def _print_product_details(self, product: pb2.Product):
        print(f"\n{'='*40}")
        print(f"ТОВАР: {product.name}")
        print(f"{'='*40}")
        print(f"ID: {product.id}")
        print(f"Описание: {product.description}")
        print(f"Цена: ${product.price:.2f}")
        print(f"Категория: {product.category}")
        print(f"На складе: {product.stock_quantity} шт.")
        print(f"Статус: {'Активен' if product.is_active else 'Неактивен'}")
        print(f"Теги: {', '.join(product.tags) if product.tags else 'нет'}")
        print(f"{'='*40}\n")
    
    def _print_product_summary(self, product: pb2.Product):
        status = "✅" if product.is_active else "⏸️"
        print(f"  {status} {product.name} | ${product.price:.2f} | {product.category}")
    
    def _handle_grpc_error(self, error: grpc.RpcError, method: str, elapsed_time: float):
        error_code = error.code()
        error_details = error.details()
        
        logger.error(f"Ошибка в {method} после {elapsed_time:.4f} сек")
        logger.error(f"   Код ошибки: {error_code.name}")
        logger.error(f"   Детали: {error_details}")
        
        if error_code == grpc.StatusCode.NOT_FOUND:
            logger.error("   Действие: Проверьте правильность ID товара")
        elif error_code == grpc.StatusCode.DEADLINE_EXCEEDED:
            logger.error("   Действие: Увеличьте таймаут или проверьте сеть")
        elif error_code == grpc.StatusCode.UNAVAILABLE:
            logger.error("   Действие: Сервер недоступен. Проверьте его статус")


def run_interactive():
    """Интерактивный клиент"""
    client = ProductCatalogClient()
    
    try:
        while True:
            print("\n" + "="*50)
            print("МЕНЮ ProductCatalog Client")
            print("="*50)
            print("1. Получить товар по ID (Unary RPC)")
            print("2. Получить все товары потоком (Streaming RPC)")
            print("3. Сравнить производительность (Benchmark)")
            print("4. Выход")
            print("="*50)
            
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                pid = input("Введите ID товара: ").strip()
                client.get_product(pid)
                
            elif choice == "2":
                inc = input("Включать неактивные товары? (y/n): ").strip().lower()
                client.stream_products(include_inactive=(inc == 'y'))
                
            elif choice == "3":
                client.benchmark_rpc_types()
                
            elif choice == "4":
                print("Выход...")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
                
    except KeyboardInterrupt:
        print("\n Прервано пользователем")
    finally:
        client.close()

if __name__ == '__main__':
    run_interactive()

