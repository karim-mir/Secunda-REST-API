FROM python:3.11-slim

# Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry и зависимости
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Копируем код проекта
COPY . .

# Создаем миграции и применяем их
RUN python manage.py makemigrations
RUN python manage.py migrate

# Создаем суперпользователя для админки
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Создаем тестовые данные
RUN python manage.py seed_data

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]