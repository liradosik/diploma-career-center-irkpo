# База данных проекта «Центр карьеры ИРКПО»

## 1) Технология
- СУБД: PostgreSQL.
- ORM: Django ORM (`AUTH_USER_MODEL = accounts.User`).
- Подход: реляционная модель со справочниками и транзакционными сущностями.

## 2) Основные сущности
- `User` — роли (`student`, `curator`, `admin`), базовые и учебные данные.
- `StudentProfile` — расширенный профиль студента.
- `Specialty` — справочник специальностей.
- `StudyGroup` — учебные группы, связь со специальностью и куратором.
- `PortfolioEntry` / `PortfolioAttachment` — портфолио и вложения.
- `ResumeSettings` — настройки резюме и публикации.
- `Vacancy` / `VacancyResponse` — вакансии и отклики.
- `Course` / `CourseRegistration` — мероприятия и регистрации.
- `ActivityLog` — журнал действий.
- `SupportTicket` — обращения в поддержку.

## 3) Связи между таблицами
- OneToOne:
  - `User 1—1 StudentProfile`
  - `User 1—1 ResumeSettings`
- ForeignKey:
  - `User N—1 StudyGroup`
  - `StudyGroup N—1 Specialty`
  - `StudyGroup N—1 User(curator)`
  - `User 1—N PortfolioEntry`
  - `PortfolioEntry 1—N PortfolioAttachment`
  - `User 1—N VacancyResponse`, `Vacancy 1—N VacancyResponse`
  - `User 1—N CourseRegistration`, `Course 1—N CourseRegistration`
  - `User 1—N ActivityLog`
  - `User 1—N SupportTicket`

## 4) Нормализация
База в основном нормализована: справочники (`Specialty`, `StudyGroup`) отделены от операционных данных (`PortfolioEntry`, `VacancyResponse`, `CourseRegistration`).

Компромисс совместимости:
- В `User` оставлены текстовые `group` и `specialty`.
- Каноничная нормализованная связь: `User.study_group -> StudyGroup -> Specialty`.
- `group/specialty` считаются legacy-полями для старого импорта; в будущем их можно убрать после миграции данных.

## 5) Защита от дублей
- `User.email` — unique.
- `StudyGroup.name` — unique.
- `StudentProfile.public_resume_token` — unique.
- `Specialty(code, letter_code)` — UniqueConstraint.
- `VacancyResponse(student, vacancy)` — unique_together.
- `CourseRegistration` — partial unique на `(student, course)` при `status='registered'`.

## 6) Добавленные индексы и назначение
Добавлены индексы под реальные фильтры/дашборды:

- `User`:
  - `role`
  - `academic_status`
  - `study_group`
  - `curator`
  - `is_active`
- `PortfolioEntry`:
  - `(student, status)`
  - `(student, created_at DESC)`
  - `(status, created_at DESC)`
- `ActivityLog`:
  - `(student, created_at DESC)`
  - `(event_type, created_at DESC)`
- `SupportTicket`:
  - `(student, status)`
  - `(status, created_at DESC)`
  - `(category, status)`
- `Vacancy`:
  - `(status, created_at DESC)`
- `Course`:
  - `(status, date)`
  - `(kind, status)`
  - `(format_type, status)`

## 7) Персональные данные
Хранятся: ФИО, email, телефон, фото, учебная группа/специальность, данные портфолио и резюме, обращения в поддержку.

## 8) Хранение файлов
Файлы хранятся через `FileField/ImageField` в media-хранилище, в БД хранится путь/метаданные.

## 9) Хранение паролей
Пароли не хранятся в открытом виде: используется стандартный хеш-подход Django (`AbstractUser`).

## 10) Что сказать на защите
- Ролевая модель и учебная структура вынесены в отдельные сущности.
- Есть ограничения целостности и защита от дублей.
- Индексы добавлены адресно под частые запросы.
- Схема готова к росту данных и расширению функционала.

## 11) Что оставить как развитие
- Постепенный вывод legacy-полей `group/specialty` после миграции старых данных.
- Расширенная аналитика и архивирование длинных журналов активности.
- Переход файлов в внешнее объектное хранилище.
