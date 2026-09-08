# Tournament Manager

Backend-приложение для создания и проведения турниров.


## Что умеет

- Авторизация пользователя (JWT)
- Создание сетки турнира до 64 команд
- Обработка результатов матчей и продвижение победителей
- Определение победителя турнира

## Стек технологий

- Python 3.13, FastAPI, SQLAlchemy, Pydantic, alembic
- PostgreSQL
- PyJWT (аутентификация)
- Docker / Docker Compose
## Запуск проекта (Docker)

Создай .env файл на основе .env.example и выполни в корне проекта:

```bash
  docker-compose up -d --build
```
API будет доступна по адресу http://localhost:8000

Документация Swagger http://localhost:8000/docs

## Запуск тестов

Чтобы создать тестовую базу данных необходимо после запуска выполнить:

```bash
  docker exec -it tournament_db psql -U postgres -c "CREATE DATABASE test_db_name;"
```
* test_db_name - имя тестовой базы данных

Далее выполнить:

```bash
  docker exec -it tournament_app bash
```
```bash
  pytest
```
## Планы по развитию

- Автоматическое создание тестовой БД
- Переход на асинхронность
- Логирование запросов