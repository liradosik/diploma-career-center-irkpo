# Центр карьеры ИРКПО (Django + PostgreSQL)

Продуктовая версия дипломного проекта «Центр карьеры ИРКПО» с ролями student/curator/admin, электронным портфолио, резюме, вакансиями и курсами.

## Стек
- Python 3.12
- Django 5
- PostgreSQL 16
- Django Templates + CSS
- Docker / docker-compose

## Структура
- `config/` — настройки Django
- `apps/accounts` — пользователи, роли, авторизация
- `apps/portfolio` — записи портфолио и проверки
- `apps/vacancies` — вакансии и отклики
- `apps/courses` — курсы/семинары/практики и записи
- `apps/resumes` — настройки и публичные резюме
- `templates/`, `static/`, `media/`

## Запуск
```bash
cp .env.example .env
docker compose up --build
```

## Миграции
```bash
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
```

## Суперпользователь
```bash
docker compose run --rm web python manage.py createsuperuser
```

## Seed-данные
```bash
docker compose run --rm web python manage.py seed_demo_data
```

## Тестовые аккаунты
- admin@irkpo.local / `Admin12345!`
- curator@irkpo.local / `Curator12345!`
- student1@irkpo.local ... student5@irkpo.local / `Student12345!`

## Сценарий проверки
1. Войти студентом, создать запись портфолио.
2. Войти куратором, открыть очередь проверок.
3. Войти студентом, открыть конструктор и публичное резюме.
4. Открыть вакансии и создать отклик.
5. Открыть курсы и записаться.
6. Открыть `/django-admin/` под admin для управления данными.
