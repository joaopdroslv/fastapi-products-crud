# FastAPI Products CRUD

This project uses FastAPI to implement CRUD operations for product management. It integrates with an SQL database (SQLite with SQLAlchemy) to store product information and a MongoDB client to log product views.

## Technologies Used

1. `FastAPI`: Framework for building fast and efficient APIs.
2. `SQLAlchemy`: ORM for interacting with the relational database (SQLite).
3. `Pydantic`: Data validation and model definition.
4. `SQLite`: Relational database for product persistence.
5. `MongoDB`: NoSQL database for logging product view events.
6. `pytest`: Framework for automated testing.

## Notes

1. The project follows best practices defined in the FastAPI web framework documentation. Available at:

[FastAPI Documentation](https://fastapi.tiangolo.com)

2. It also follows best practices available in the `fastapi-best-practices` repository. Available at:

[fastapi-best-practices GitHub Repository](https://github.com/zhanymkanov/fastapi-best-practices)

## POSTMAN Documentation

A POSTMAN collection has been created to document the project's endpoints. Available at:

[POSTMAN Documentation](https://documenter.getpostman.com/view/40636918/2sAYJ4igQE)

## How to Run the Project

### Step 1: Clone the repository

Clone the repository to your local machine:

```bash
git clone https://github.com/joaopdroslv/fastapi-products-crud
cd fastapi-products-crud
```

### Step 2: Install dependencies

**RECOMMENDATION**: Create a virtual environment first.

Before running the project, install the necessary dependencies. In the project's root directory, run:

```bash
pip install -r requirements.txt
```

### Step 3: Configure environment variables

Create a `.env` file using the `.env.example` file available in the repository as a template.

Ensure all environment variables are correctly set in the `.env` file, or, if preferred, rename `.env.example` to `.env`, as it is pre-configured with the following fields:

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

Fill in the details according to your environment if necessary.

### Step 4: Build and start the Docker containers

After configuring the environment variables, use Docker Compose to build and start the containers:

```bash
docker-compose up --build
```

This command will build the images and start the project's containers (including the FastAPI application and MongoDB).

## How to Run Tests

In this project, tests require the MongoDB container to be running for proper execution.

### Step 1: Start MongoDB separately

To run the tests, MongoDB must be running. You can start it separately with the following command:

```bash
docker-compose up mongodb --build
```

This will start the MongoDB container.

### Step 2: Run the tests

After starting MongoDB, you can run the tests using pytest:

```bash
pytest -vvv
```

This command will execute all tests in the project, displaying detailed information about the execution.
