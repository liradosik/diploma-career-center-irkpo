# Центр карьеры ИРКПО (Django + PostgreSQL)

Продуктовая версия дипломного проекта «Центр карьеры ИРКПО» с ролями student/curator/admin, электронным портфолио, резюме, вакансиями и курсами.

## Учебная структура (актуально)
- `Specialty` — код специальности, название и буквенный код (например, `44.02.02` + `Н`).
- `StudyGroup` — конкретная учебная группа/подгруппа (например, `Н121/1`), связана со специальностью и куратором.
- `User(role=student)` — закреплён за конкретной `study_group`.
- Куратор видит студентов только тех групп, где он назначен куратором.
- Для студента действует учебный статус: `Обучается` / `Выпускник` / `Неактивен`.
- В `adminpanel` доступны страницы:
  - `accounts/admin/academic-structure/` — общая страница учебной структуры;
  - `accounts/admin/specialties/` — управление специальностями;
  - `accounts/admin/groups/` — управление группами;
  - `accounts/admin/students/import/` — массовый CSV-импорт студентов (`full_name,email,password,group`).

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
После `git pull` обязательно выполнить `python manage.py migrate`.

## Суперпользователь
```bash
docker compose run --rm web python manage.py createsuperuser
```

## Seed-данные
```bash
docker compose run --rm web python manage.py seed_demo_data
docker compose run --rm web python manage.py seed_demo_data --clear
```

## Перевод групп на новый учебный год
```bash
docker compose run --rm web python manage.py promote_groups --dry-run
docker compose run --rm web python manage.py promote_groups --apply
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
