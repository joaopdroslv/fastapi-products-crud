from typing import List

from faker import Faker

data_faker = Faker()

expected_status = [
    "em_estoque",
    "em_reposicao",
]  # Status necessários para gerar produtos válidos


def generate_valid_products(n: int = 10) -> List:
    """
    Função que gera uma lista de produtos falsos com dados aleatórios.

    :param n: Número de produtos a serem gerados. O padrão é 10.
    :return: Lista de dicionários representando produtos.
    """
    return [
        {
            "name": data_faker.word()[:128],  # Limita a quantidade de carcteres
            "description": data_faker.sentence()[
                :255
            ],  # Limita a quantidade de carcteres
            "price": round(
                data_faker.pyfloat(min_value=10, max_value=5000, right_digits=2), 2
            ),
            "status": data_faker.random_element(expected_status),
            "stock_quantity": data_faker.random_int(min=1, max=200),
        }
        for _ in range(n)
    ]
