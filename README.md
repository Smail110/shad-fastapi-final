# Book Marketplace API

Учебное web-приложение на **FastAPI** для размещения объявлений о продаже книг.

Проект основан на ветке `fourth_lection` из учебного репозитория и доработан в рамках самостоятельной работы:
- добавлена модель **Seller**
- книги связаны с продавцами
- реализована **JWT-авторизация**
- защищены нужные эндпоинты
- написаны тесты на все эндпоинты

---

## Функциональность

### Книги
- создание книги
- получение списка книг
- получение одной книги по `id`
- полное обновление книги
- частичное обновление книги
- удаление книги

### Продавцы
- регистрация продавца
- получение списка продавцов
- получение продавца по `id`
- обновление данных продавца
- удаление продавца

### Авторизация
- получение JWT-токена по `e_mail + password`
- защита эндпоинтов токеном

---

## Стек технологий

- Python 3
- FastAPI
- SQLAlchemy
- PostgreSQL
- asyncpg
- Pydantic
- JWT
- pytest
- httpx

---

## Структура проекта

```text
src/
├── configurations/
├── models/
├── routers/
├── schemas/
├── services/
├── tests/
├── auth.py
└── main.py
```

---

## Модели

### Seller
Обязательные поля:
- `id`
- `first_name`
- `last_name`
- `e_mail`
- `password`

### Book
Основные поля:
- `id`
- `title`
- `author`
- `year`
- `pages`
- `seller_id`

### Связь между моделями
- один продавец может иметь несколько книг
- одна книга принадлежит только одному продавцу

---

## Эндпоинты

### Продавцы

#### Регистрация продавца
`POST /api/v1/seller/`

#### Получение списка продавцов
`GET /api/v1/seller/`

#### Получение одного продавца
`GET /api/v1/seller/{seller_id}`

#### Обновление продавца
`PUT /api/v1/seller/{seller_id}`

#### Удаление продавца
`DELETE /api/v1/seller/{seller_id}`

---

### Книги

#### Создание книги
`POST /api/v1/books/`

#### Получение списка книг
`GET /api/v1/books/`

#### Получение одной книги
`GET /api/v1/books/{book_id}`

#### Полное обновление книги
`PUT /api/v1/books/{book_id}`

#### Частичное обновление книги
`PATCH /api/v1/books/{book_id}`

#### Удаление книги
`DELETE /api/v1/books/{book_id}`

---

### Авторизация

#### Получение JWT-токена
`POST /api/v1/token/`

Тело запроса:

```json
{
  "e_mail": "ivan@example.com",
  "password": "123456"
}
```

Пример ответа:

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

---

## Защищённые эндпоинты

JWT-токен требуется для следующих ручек:

- `GET /api/v1/seller/{seller_id}`
- `POST /api/v1/books/`
- `PUT /api/v1/books/{book_id}`

Токен передаётся в заголовке:

```http
Authorization: Bearer <token>
```

---

## Безопасность

- поле `password` **не возвращается** в ответах seller-эндпоинтов
- доступ к части ручек ограничен JWT-токеном

---

## Запуск проекта

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Smail110/shad-fastapi-final.git
cd shad-fastapi-final
```

### 2. Создать виртуальное окружение

#### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Настройка `.env`

Создать файл `.env` в корне проекта:

```env
DB_USERNAME=postgres_user
DB_PASSWORD=postgres_pass
DB_HOST=127.0.0.1
DB_PORT=5445
DB_NAME=fastapi_project_db
DB_TEST_NAME=fastapi_project_test_db

JWT_SECRET_KEY=super_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Запуск PostgreSQL через Docker

```bash
docker compose up -d
```

Если тестовая база не создана, её нужно создать отдельно.

---

## Запуск приложения

```bash
uvicorn src.main:app --reload
```

Приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

---

## Тестирование

В проекте написаны тесты на все эндпоинты.

### Запуск всех тестов

```bash
pytest src/tests -v
```

### Результат

```text
19 passed
```

---

## Что покрывают тесты

### Продавцы
- создание продавца
- получение списка продавцов
- получение продавца без токена
- получение продавца с токеном
- обновление продавца
- удаление продавца вместе с его книгами

### Книги
- создание книги без токена
- создание книги с токеном
- валидация года книги
- получение списка книг
- получение одной книги
- получение книги по неверному `id`
- обновление книги без токена
- обновление книги с токеном
- частичное обновление книги
- удаление книги
- удаление книги по неверному `id`

### JWT
- получение токена
- ошибка при неверном пароле

---

## Примеры запросов

### Регистрация продавца

```http
POST /api/v1/seller/
Content-Type: application/json
```

```json
{
  "first_name": "Ivan",
  "last_name": "Petrov",
  "e_mail": "ivan@example.com",
  "password": "123456"
}
```

### Создание книги

```http
POST /api/v1/books/
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "title": "Clean Architecture",
  "author": "Robert Martin",
  "count_pages": 300,
  "year": 2025,
  "seller_id": 1
}
```

---

## Итог

В рамках работы были реализованы:
- модель `Seller`
- связь `Seller -> Book`
- поле `seller_id` в модели `Book`
- seller CRUD
- JWT-авторизация
- защита нужных эндпоинтов
- тесты на все эндпоинты
