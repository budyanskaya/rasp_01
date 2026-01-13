import grpc
from concurrent import futures
import time
import logging
from typing import Dict, List
from datetime import datetime

import product_service_pb2 as pb2
import product_service_pb2_grpc as pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InMemoryProductDB:
    def __init__(self):
        self.products: Dict[str, pb2.Product] = {
            "1": pb2.Product(
                id="1",
                name="Кофемашина Barista Elite",
                description="Автоматическая кофемашина с функцией капучино и латте",
                price=450.00,
                category="Бытовая техника",
                stock_quantity=15,
                is_active=True,
                tags=["кофе", "кухня", "премиум"]
            ),
            "2": pb2.Product(
                id="2",
                name="Механическая клавиатура RGB Pro",
                description="Клавиатура с переключателями Cherry MX Blue и подсветкой",
                price=120.50,
                category="Компьютерные аксессуары",
                stock_quantity=40,
                is_active=True,
                tags=["клавиатура", "гейминг", "rgb"]
            ),
            "3": pb2.Product(
                id="3",
                name="Спортивная бутылка для воды 1L",
                description="Термостойкая бутылка из нержавеющей стали с фильтром",
                price=29.99,
                category="Спорт и отдых",
                stock_quantity=200,
                is_active=True,
                tags=["бутылка", "спорт", "экология"]
            ),
            "4": pb2.Product(
                id="4",
                name="USB-флешка 8 ГБ (снята с производства)",
                description="Устаревшая модель флеш-накопителя без поддержки USB 3.0",
                price=8.99,
                category="Архив",
                stock_quantity=0,
                is_active=False,  # Неактивный товар
                tags=["устаревшее", "usb", "архив"]
            )
        }
    
    def get_product(self, product_id: str) -> pb2.Product:
        return self.products.get(product_id)
    
    def get_all_products(self, include_inactive: bool = False) -> List[pb2.Product]:
        if include_inactive:
            return list(self.products.values())
        return [p for p in self.products.values() if p.is_active]

class ProductCatalogServicer(pb2_grpc.ProductCatalogServiceServicer):
    
    def __init__(self):
        self.db = InMemoryProductDB()
        self.request_count = 0
        logger.info("ProductCatalogServicer инициализирован")
    
    def GetProduct(self, request: pb2.GetProductRequest, context):
        self.request_count += 1
        request_id = self.request_count
        start_time = time.time()
        
        logger.info(f"[Request #{request_id}] GetProduct для product_id={request.product_id}")
        
        product = self.db.get_product(request.product_id)
        
        if not product:
            error_msg = f"Товар с ID '{request.product_id}' не найден"
            logger.warning(f"[Request #{request_id}] {error_msg}")
            
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(error_msg)
            return pb2.Product()
        
        if not product.is_active:
            logger.warning(f"[Request #{request_id}] Товар {request.product_id} неактивен")
            context.set_trailing_metadata([('product-status', 'inactive')])
        
        elapsed_time = time.time() - start_time
        logger.info(f"[Request #{request_id}] GetProduct выполнен за {elapsed_time:.4f} секунд")
        
        return product
    
    def StreamProducts(self, request: pb2.StreamProductsRequest, context):
        self.request_count += 1
        request_id = self.request_count
        start_time = time.time()
        
        logger.info(f"[Request #{request_id}] StreamProducts (include_inactive={request.include_inactive})")
        
        products = self.db.get_all_products(request.include_inactive)
        
        if not products:
            logger.warning(f"[Request #{request_id}] Нет товаров для отправки")
            yield pb2.Product(
                id="",
                name="Нет товаров",
                description="В каталоге нет доступных товаров",
                price=0.0,
                category="",
                stock_quantity=0,
                is_active=False
            )
            return
        
        sent_count = 0
        for product in products:
            time.sleep(0.5)
            
            if context.is_active():
                yield product
                sent_count += 1
                logger.debug(f"[Request #{request_id}] Отправлен товар: {product.name}")
            else:
                logger.warning(f"[Request #{request_id}] Клиент отменил запрос")
                break
        
        elapsed_time = time.time() - start_time
        logger.info(f"[Request #{request_id}] StreamProducts отправлено {sent_count} товаров за {elapsed_time:.4f} секунд")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    pb2_grpc.add_ProductCatalogServiceServicer_to_server(
        ProductCatalogServicer(), server
    )
    
    port = '50051'
    server.add_insecure_port(f'[::]:{port}')
    
    logger.info(f"Запуск gRPC сервера на порту {port}...")
    server.start()
    
    logger.info("Доступные методы:")
    logger.info("  GetProduct(product_id) - получение товара по ID")
    logger.info("  StreamProducts() - потоковая передача всех товаров")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Остановка сервера...")
        server.stop(0)

if __name__ == '__main__':
    serve()