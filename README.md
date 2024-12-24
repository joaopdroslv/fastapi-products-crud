# FastAPI Products CRUD

Este `FastAPI Products CRUD` é um projeto FastAPI responsável por gerenciar as operações CRUD relacionadas a produtos. Ele integra com um banco de dados SQL (usando SQLAlchemy) para o gerenciamento de produtos e um cliente MongoDB para registrar as visualizações dos produtos.

### Observações

O projeto foi desenvolvido levando em consideração as boas práticas definidas na documentação do FastAPI web framework. Disponível em:

[FastAPI Documentation](https://fastapi.tiangolo.com)

E também as boas práticas disponíveis no repositório `fastapi-best-practices`. Disponível em:

[fastapi-best-practices GitHub Repository](https://github.com/zhanymkanov/fastapi-best-practices)

# Documentação POSTMAN

Uma collection POSTMAN foi criada para documentar os endpoints do projeto. Disponível em:

[POSTMAN Documentation](https://documenter.getpostman.com/view/40636918/2sAYJ4igQE)

## Como Rodar o Projeto

### Passo 1: Clone o repositório

Clone o repositório para sua máquina local:

```bash
git clone https://github.com/joaopdroslv/fastapi-products-crud
cd fastapi-products-crud
```

### Passo 2: Instalar as dependências

RECOMENDAÇÃO: Crie um ambiente virtual para isso.

Antes de rodar o projeto, instale as dependências necessárias. No diretório raiz do projeto, execute:

```bash
pip install -r requirements.txt
```

### Passo 3: Configuração das variáveis de ambiente

Crie um arquivo `.env` usando como base o arquivo `.env.example` disponível no repositório.

Verifique se todas as variáveis de ambiente estão corretamente preenchidas no arquivo `.env` criado por você ou se preferir, mantenha o `.env.example` disponível no repositório, basta renomea-lo para `.env`, já que ele está pré configurado com os seguintes campos:

```
APP_PORT=
SQLITE_URL=
MONGODB_PORT=
MONGODB_PRODUCTION_HOST=
MONGODB_PRODUCTION_DATABASE_NAME=
MONGODB_PRODUCTION_URL=
MONGODB_TEST_HOST=
MONGODB_TEST_DATABASE_NAME=
MONGODB_TEST_URL=
```

Preencha de acordo com seu ambiente se desejar

### Passo 4: Construa e inicie os containers docker

Depois de configurar as variáveis de ambiente, use o Docker Compose para construir e iniciar os containers:

```bash
docker-compose up --build
```

Esse comando irá construir as imagens e iniciar os containers do projeto (incluindo a aplicação FastAPI e o MongoDB).

## Como Rodar os Testes

No contexto deste projeto, os testes dependem do container mongodb em execução para serem executados corretamente.

### Passo 1: Iniciar o MongoDB separadamente

Para rodar os testes, é necessário ter o MongoDB em execução. Você pode iniciar o MongoDB separadamente com o seguinte comando:

```bash
docker-compose up mongodb --build
```

Isso irá iniciar o container do MongoDB.

### Passo 2: Rodar os testes

Após iniciar o MongoDB, você pode rodar os testes utilizando o pytest:

```bash
pytest -vv
```

Esse comando irá executar todos os testes do projeto, mostrando detalhes sobre a execução.
