# Our Kidney Story - Django Backend

A production-grade Django backend for the "Our Kidney Story" platform, a community-driven support platform for kidney disease patients and caregivers in India.

## Features

- User authentication with JWT (access + refresh tokens)
- Story sharing system
- Blog system
- Community forum
- Dialysis center locator
- Kidney Care Shelf (E-Commerce)
- Feedback & suggestions system
- Admin panel functions

## Tech Stack

- Django with Django REST Framework
- PostgreSQL for database
- MinIO for file storage
- Docker for containerization

## Project Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/our-kidney-story-backend.git
cd our-kidney-story-backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the Docker containers for PostgreSQL and MinIO:

```bash
docker-compose up -d
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:postgres@localhost:5432/kidney_story
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=kidney-story
MINIO_USE_SSL=False
```

## API Documentation

The API documentation is available at `/api/docs/` when the server is running.

## Seeding Data

To seed the database with initial data, run:

```bash
python manage.py seed_data
```

## Running Tests

```bash
python manage.py test
```

## License

MIT
