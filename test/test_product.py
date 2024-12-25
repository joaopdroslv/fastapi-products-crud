from src.main import app
from src.schemas.product_schema import ProductStatus
from src.controllers.product_controller import product_controller
from src.database import dependencies
from src.database import sqlite
from src.database import mongodb
from test import utils

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from typing import List
from dotenv import load_dotenv
import os


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test/test_database.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
       yield db
    finally:
        db.close() 

app.dependency_overrides[dependencies.get_db] = override_get_db

client = TestClient(app)

load_dotenv()

MONGODB_TEST_DATABASE_NAME=os.getenv('MONGODB_TEST_DATABASE_NAME')


@pytest.fixture(scope='function')
def setup_database():
    # Substitui o ProductLogClient usado pelo controlador de produtos
    product_controller.product_log_client = mongodb.ProductLogClient('test')
    # Captura o mongo client do product log client
    mongo_client = product_controller.product_log_client.mongo_client  

    # Limpeza do banco de dados do MongoDB antes de cada teste
    mongo_client.drop_database(MONGODB_TEST_DATABASE_NAME)

    # Criação e limpeza das tabelas antes de cada teste
    sqlite.Base.metadata.drop_all(bind=engine)
    sqlite.Base.metadata.create_all(bind=engine)

    yield

    # Limpeza após o teste
    sqlite.Base.metadata.drop_all(bind=engine)

    # Limpeza do banco de dados do MongoDB depois de cada teste
    mongo_client.drop_database(MONGODB_TEST_DATABASE_NAME)


def test_create_product_successfully(setup_database):
    """Checks if the product is created correctly."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    assert response.status_code == 201


def test_create_product_validates_content_on_creation(setup_database):
    """Checks whether the data sent when creating the product is validated correctly."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    generated_product = generated_products[0]
    response = client.post('/products', json=generated_product)
    response_data = response.json()
    assert response.status_code == 201
    assert response_data['name'] == generated_product['name']
    assert response_data['description'] == generated_product['description']
    assert response_data['price'] == generated_product['price']
    assert response_data['status'] == generated_product['status']
    assert response_data['stock_quantity'] == generated_product['stock_quantity']


def test_create_invalid_in_stock_product(setup_database):
    """
    Checks whether the creation of the product with status "in_stock" 
    and stock_quantity equal to 0 returns an error.
    """
    generated_products: List[dict] = utils.generate_valid_products(1)
    invalid_product = generated_products[0].copy()
    # Quando o 'status' é 'em_estoque' é esperado o 'stock_quantity' seja > 0
    invalid_product['status'] = ProductStatus.in_stock.value
    invalid_product['stock_quantity'] = 0
    response = client.post('/products', json=invalid_product)
    assert response.status_code == 422


def test_create_product_with_invalid_out_of_stock_status(setup_database):
    """
    Checks whether the creation of a product with status "out of stock" 
    and stock_quantity greater than 0 returns an error.
    """
    generated_products: List[dict] = utils.generate_valid_products(1)
    invalid_product = generated_products[0].copy()
    # Quando o 'status' é 'em_falta' é esperado o 'stock_quantity' seja == 0
    invalid_product['status'] = ProductStatus.out_of_stock.value
    invalid_product['stock_quantity'] = 99
    response = client.post('/products', json=invalid_product)
    assert response.status_code == 422


def test_create_product_with_invalid_price_value(setup_database):
    """Checks whether creating a product with an invalid price returns an error."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    generated_product = generated_products[0]
    generated_product['price'] = 0  # Seta um preço inválido, preço deve ser > 0
    response = client.post('/products', json=generated_product)
    assert response.status_code == 422


def test_list_products_successfully(setup_database):
    """Check if all products are listed correctly."""
    generated_products: List[dict] = utils.generate_valid_products(10)
    for generated_product in generated_products:
        client.post('/products', json=generated_product)
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json()) == len(generated_products)


def test_list_products_validates_content(setup_database):
    """Checks that all products are listed and the data for each product is correct."""
    generated_products: List[dict] = utils.generate_valid_products(10)
    for generated_product in generated_products:
        client.post('/products', json=generated_product)
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json()) == len(generated_products)
    for i, generated_product in enumerate(generated_products):
        resonse_data = response.json()[i]
        assert resonse_data['name'] == generated_product['name']
        assert resonse_data['description'] == generated_product['description']
        assert resonse_data['price'] == generated_product['price']
        assert resonse_data['status'] == generated_product['status']
        assert resonse_data['stock_quantity'] == generated_product['stock_quantity']


def test_view_single_product(setup_database):
    """Checks whether a single product can be displayed correctly."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']
    created_product = response.json().copy()
    response = client.get(f'/products/{created_product_id}')
    assert response.status_code == 200
    assert response.json() == created_product


def test_create_view_log_for_each_product_on_listing(setup_database):
    """Checks if a viewing log is created for each listed product."""
    generated_products: List[dict] = utils.generate_valid_products(10)
    created_products = []
    for generated_product in generated_products:
        response = client.post('/products', json=generated_product)
        created_products.append(response.json())  # Salva cada um dos produtos criados

    # Lista os produtos 10x
    for i in range (10):
        client.get('/products')

    # Para cada produto, verificar se existem 10 logs de visualização
    for created_product in created_products:
        product_id = created_product['id']
        # Busca os logs de visualização do produto
        response = client.get(f'/products/{product_id}/views')
        response_data = response.json()
        assert response.status_code == 200
        assert 'number_of_views' in response_data
        assert 'views' in response_data
        assert response_data['number_of_views'] == 10  # Cada produto foi visualizado 10 vezes
        assert len(response_data['views']) == 10  # Cada produto deve ter 10 logs


def test_create_view_log_when_viewing_single_product(setup_database):
    """Checks if the view log is created when viewing a single product."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Visualiza o produto criado
    response = client.get(f'/products/{created_product_id}')

    # Busca os logs do produto criado e visualizado
    response = client.get(f'/products/{created_product_id}/views')

    response_data = response.json()
    assert response.status_code == 200
    assert 'number_of_views' in response_data
    assert 'views' in response_data
    assert response_data['number_of_views'] == 1  # Produto foi pesquisado apenas uma vez
    assert len(response_data['views']) == 1  # Produto foi pesquisado apenas uma vez


def test_create_multiple_view_logs_for_single_product(setup_database):
    """Checks if multiple view logs are created for a product viewed multiple times."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Visualiza o produto criado
    for i in range(30):
        response = client.get(f'/products/{created_product_id}')

    # Busca os logs do produto criado e visualizado
    response = client.get(f'/products/{created_product_id}/views')

    response_data = response.json()
    assert response.status_code == 200
    assert 'number_of_views' in response_data
    assert 'views' in response_data
    assert response_data['number_of_views'] == 30
    assert len(response_data['views']) == 30


def test_format_of_product_view_log(setup_database):
    """Checks that product view logs are in the correct format."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Visualiza o produto criado
    response = client.get(f'/products/{created_product_id}')

    # Busca os logs do produto criado e visualizado
    response = client.get(f'/products/{created_product_id}/views')

    response_data = response.json()
    assert response.status_code == 200
    assert 'number_of_views' in response_data
    assert 'views' in response_data
    assert response_data['number_of_views'] == 1  # Produto foi pesquisado apenas uma vez
    assert len(response_data['views']) == 1  # Produto foi pesquisado apenas uma vez

    # Verificar o formato dos logs criados
    view_log = response_data['views'][0]
    assert 'viewed_at' in view_log
    assert isinstance(view_log['viewed_at'], str)  # O timestamp deve ser uma string

    # Tenta converter o 'viewed_at' para datetime e verifica se é válido
    from datetime import datetime
    try:
        datetime.strptime(view_log['viewed_at'], "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError as e:
        print(e)
        assert False


def test_get_view_logs_of_nonexistent_product(setup_database):
    """
    Checks whether a NotFound error is returned when trying to 
    access the view logs for a non-existent product.
    """
    response = client.get(f'/products/999/views')
    assert response.status_code == 404
    assert response.json()['message'] == 'Product not found.'


def test_update_product_successfully(setup_database):
    """Checks whether the product can be updated correctly."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto criado
    updated_product = generated_products[0].copy()
    updated_product['name'] = 'test_name'
    updated_product['description'] = 'test_description'
    updated_product['price'] = 999.99
    updated_product['status'] = ProductStatus.in_stock.value
    updated_product['stock_quantity'] = 1
    response = client.put(f'/products/{created_product_id}', json=updated_product)

    response_data = response.json()
    assert response.status_code == 200
    assert response_data['name'] == updated_product['name']
    assert response_data['description'] == updated_product['description']
    assert response_data['price'] == updated_product['price']
    assert response_data['status'] == updated_product['status']
    assert response_data['stock_quantity'] == updated_product['stock_quantity']


def test_update_product_with_partial_data(setup_database):
    """Checks if the product can be updated with partial data."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto criado (com apenas o campo alvo da atualização)
    updated_data = {'stock_quantity': 999}
    response = client.put(f'/products/{created_product_id}', json=updated_data)

    assert response.status_code == 200
    assert response.json()['stock_quantity'] == 999


def test_update_product_with_invalid_in_stock_status(setup_database):
    """
    Checks whether updating a product with status "in_stock" 
    and stock_quantity equal to 0 returns an error.
    """
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto com dados inválidos (o produto completo é enviado, todos os campos)
    invalid_product_to_update = generated_products[0].copy()
    invalid_product_to_update['status'] = ProductStatus.in_stock.value
    invalid_product_to_update['stock_quantity'] = 0
    response = client.put(f'/products/{created_product_id}', json=invalid_product_to_update)
    assert response.status_code == 422


def test_update_product_with_invalid_out_of_stock_status(setup_database):
    """
    Checks whether updating a product with "out_of_stock" status 
    and stock_quantity greater than 0 returns an error.
    """
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto com dados inválidos (o produto completo é enviado, todos os campos)
    invalid_product_to_update = generated_products[0].copy()
    invalid_product_to_update['status'] = ProductStatus.out_of_stock.value
    invalid_product_to_update['stock_quantity'] = 99
    response = client.put(f'/products/{created_product_id}', json=invalid_product_to_update)
    assert response.status_code == 422


def test_update_product_with_invalid_price_value(setup_database):
    """Checks whether updating a product with an invalid price returns an error."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto com dados inválidos (o produto completo é enviado, todos os campos)
    invalid_product_to_update = generated_products[0].copy()
    invalid_product_to_update['price'] = 0.0
    response = client.put(f'/products/{created_product_id}', json=invalid_product_to_update)
    assert response.status_code == 422


def test_update_nonexistent_product(setup_database):
    """Checks if a NotFound error is returned when trying to update a non-existent product."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.put('/products/999', json=generated_products[0])
    assert response.status_code == 404
    assert response.json()['message'] == 'Product not found.'


def test_delete_product_successfully(setup_database):
    """Checks whether a product can be deleted correctly."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']
    response = client.delete(f'/products/{created_product_id}')
    assert response.status_code == 200


def test_delete_nonexistent_product(setup_database):
    """Checks if a NotFound error is returned when trying to delete a non-existent product."""
    response = client.delete('/products/999')
    assert response.status_code == 404
    assert response.json()['message'] == 'Product not found.'
