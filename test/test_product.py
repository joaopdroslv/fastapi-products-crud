from src.main import app
from src.database import dependencies
from src.database import sqlite
from src.schemas.product_schema import ProductStatus

from test import utils

import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from typing import List


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


@pytest.fixture(scope='function')
def mock_product_log_client():
    """Mocka a interação com o MongoDB para testes."""
    mock_client = MagicMock()
    mock_client.log_product_view = MagicMock()  # Mocka a função de log
    mock_client.get_product_view_logs = MagicMock(return_value=[
        {"viewed_at": "2024-12-20T00:00:00Z"},
        {"viewed_at": "2024-12-20T01:00:00Z"},
        {"viewed_at": "2024-12-20T01:00:00Z"},
        {"viewed_at": "2024-12-20T01:00:00Z"},
    ])  # Mocka a função de busca dos logs com 4 logs falsos
    return mock_client


@pytest.fixture(scope='function')
def setup_database(mock_product_log_client):
    # Substitui o ProductLogClient usado pelo controlador de produtos
    from src.controllers.product_controller import product_controller
    product_controller.product_log_client = mock_product_log_client

    # Criação e limpeza das tabelas antes de cada teste
    sqlite.Base.metadata.drop_all(bind=engine)
    sqlite.Base.metadata.create_all(bind=engine)
    yield
    # Limpeza após o teste
    sqlite.Base.metadata.drop_all(bind=engine)


def test_create_product(setup_database):
    """Ensuring the product will be created."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    assert response.status_code == 201


def test_create_product_with_content_validation(setup_database):
    """Ensuring the product will be created."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    generated_product = generated_products[0]
    response = client.post('/products', json=generated_product)
    reponse_data = response.json()
    assert response.status_code == 201
    assert reponse_data['name'] == generated_product['name']
    assert reponse_data['description'] == generated_product['description']
    assert reponse_data['price'] == generated_product['price']
    assert reponse_data['status'] == generated_product['status']
    assert reponse_data['stock_quantity'] == generated_product['stock_quantity']


def test_create_invalid_in_stock_product(setup_database):
    """Ensuring the product will not be created with invalid data."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    invalid_product = generated_products[0].copy()
    # Quando o 'status' é 'em_estoque' é esperado o 'stock_quantity' seja > 0
    invalid_product['status'] = ProductStatus.in_stock.value
    invalid_product['stock_quantity'] = 0
    response = client.post('/products', json=invalid_product)
    assert response.status_code == 422


def test_create_invalid_out_of_stock_product(setup_database):
    """Ensuring the product will not be created with invalid data."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    invalid_product = generated_products[0].copy()
    # Quando o 'status' é 'em_falta' é esperado o 'stock_quantity' seja == 0
    invalid_product['status'] = ProductStatus.out_of_stock.value
    invalid_product['stock_quantity'] = 99
    response = client.post('/products', json=invalid_product)
    assert response.status_code == 422


def test_create_product_with_invalid_price(setup_database):
    """Ensuring the product will not be created with invalid data."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    generated_product = generated_products[0]
    generated_product['price'] = 0  # Seta um preço inválido, preço deve ser > 0
    response = client.post('/products', json=generated_product)
    assert response.status_code == 422


def test_list_products(setup_database):
    """Ensuring all products will be listed."""
    generated_products: List[dict] = utils.generate_valid_products(10)
    for generated_product in generated_products:
        client.post('/products', json=generated_product)
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json()) == len(generated_products)


def test_list_products_with_content_validation(setup_database):
    """Ensuring all products will be listed."""
    generated_products: List[dict] = utils.generate_valid_products(10)
    for generated_product in generated_products:
        client.post('/products', json=generated_product)
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json()) == len(generated_products)
    for i, generated_product in enumerate(generated_products):
        assert response.json()[i]['name'] == generated_product['name']
        assert response.json()[i]['description'] == generated_product['description']
        assert response.json()[i]['price'] == generated_product['price']
        assert response.json()[i]['status'] == generated_product['status']
        assert response.json()[i]['stock_quantity'] == generated_product['stock_quantity']


def test_list_product(setup_database):
    """Ensuring the product will be listed."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']
    created_product = response.json().copy()
    response = client.get(f'/products/{created_product_id}')
    assert response.status_code == 200
    assert response.json() == created_product


def test_product_log_is_being_called(setup_database, mock_product_log_client):
    """Ensuring the product log function is beeing called."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Visualiza o produto criado
    response = client.get(f'/products/{created_product_id}')

    # Verifica se a função de log foi chamada
    mock_product_log_client.log_product_view.assert_called_once_with(created_product_id)

    assert response.status_code == 200


def test_get_product_logs(setup_database, mock_product_log_client):
    """Ensuring the product view logs are being return in the correct format."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post('/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Busca os logs do produto criado, considerando que já foi buscado algumas vezes
    response = client.get(f'/products/{created_product_id}/views')

    # Verifica se a função de log foi chamada
    mock_product_log_client.get_product_view_logs.assert_called_once_with(created_product_id)

    response_data = response.json()
    assert response.status_code == 200
    assert 'views' in response_data  # Listagem das visualizações
    assert 'number_of_views' in response_data  # Quantidade de visualizações
    assert response_data['number_of_views'] == 4  # Quantidade de logs mockados


def test_update_product(setup_database):
    """Ensuring the product will be updated."""
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


def test_update_product_with_fewer_fields(setup_database):
    """Ensuring the product will be updated with fewer fields."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto criado (com apenas o campo alvo da atualização)
    updated_product = {'stock_quantity': 999}
    response = client.put(f'/products/{created_product_id}', json=updated_product)

    assert response.status_code == 200
    assert response.json()['stock_quantity'] == 999


def test_update_a_nonexistent_product(setup_database):
    """Ensuring NotFound exception when trying to update a non-existing product."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.put('/products/999', json=generated_products[0])
    assert response.status_code == 404
    assert response.json()['message'] == 'Product not found.'


def test_update_invalid_in_stock_product(setup_database):
    """Ensuring the product will not be updated with invalid data."""
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


def test_update_invalid_out_of_stock_product(setup_database):
    """Ensuring the product will not be updated with invalid data."""
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


def test_update_product_with_invalid_price(setup_database):
    """Ensuring the product will not be updated with invalid data."""
    # Cria um produto
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']

    # Atualiza o produto com dados inválidos (o produto completo é enviado, todos os campos)
    invalid_product_to_update = generated_products[0].copy()
    invalid_product_to_update['price'] = 0.0
    response = client.put(f'/products/{created_product_id}', json=invalid_product_to_update)

    assert response.status_code == 422


def test_delete_product(setup_database):
    """Ensuring the product will be deleted."""
    generated_products: List[dict] = utils.generate_valid_products(1)
    response = client.post(f'/products', json=generated_products[0])
    created_product_id = response.json()['id']
    response = client.delete(f'/products/{created_product_id}')
    assert response.status_code == 200
    response = client.get(f'/products/{created_product_id}')
    assert response.status_code == 404  # NotFound esperado após a deleção


def test_delete_a_nonexistent_product(setup_database):
    """Ensuring NotFound exception when trying to delete a non-existing product."""
    response = client.delete('/products/999')
    assert response.status_code == 404
    assert response.json()['message'] == 'Product not found.'
