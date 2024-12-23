from enum import Enum


class ProductStatus(str, Enum):
    EM_ESTOQUE = 'Disponível em estoque'
    EM_REPOSICAO = 'Atualmente em reposição'
    EM_FALTA = 'Está em falta'
