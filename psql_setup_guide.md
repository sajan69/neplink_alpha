
# PostgreSQL Setup and Implementation Guide for Django on Windows

## 1. Install PostgreSQL

1. Download PostgreSQL from the official website: https://www.postgresql.org/download/windows/
2. Run the installer and follow the installation wizard.
3. Remember the password you set for the 'postgres' superuser during installation.

## 2. Set Up the Database

1. Open Command Prompt (Win + R, type "cmd", press Enter)
2. Connect to PostgreSQL as superuser:
   ```
   psql -U postgres
   ```
3. Create a new database:
   ```sql
   CREATE DATABASE neplink;
   ```
4. Create a new user:
   ```sql
   CREATE USER neplink_user WITH PASSWORD 'your_password';
   ```
5. Grant privileges to the new user:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE neplink TO neplink_user;
   ```
6. Connect to the new database:
   ```sql
   \c neplink
   ```
7. Create extensions (if needed):
   ```sql
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
8. Exit psql:
   ```
   \q
   ```

## 3. Set Up Permissions

1. Reconnect to PostgreSQL and your database:
   ```
   psql -U postgres
   \c neplink
   ```
2. Grant all privileges on the database:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE neplink TO neplink_user;
   ```
3. Grant schema privileges:
   ```sql
   GRANT USAGE, CREATE ON SCHEMA public TO neplink_user;
   ```
4. Grant table privileges:
   ```sql
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neplink_user;
   ```
5. Grant sequence privileges:
   ```sql
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO neplink_user;
   ```
6. Set default privileges:
   ```sql
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO neplink_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO neplink_user;
   ```
7. Set database ownership:
   ```sql
   ALTER DATABASE neplink OWNER TO neplink_user;
   ```
8. Exit psql:
   ```
   \q
   ```

## 4. Update Django Project

1. Install psycopg2 (PostgreSQL adapter for Python):
   ```
   pip install psycopg2-binary
   ```

2. Update your project's `.env` file:
   ```
   DB_NAME=neplink
   DB_USER=neplink_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. Update `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('DB_NAME'),
           'USER': config('DB_USER'),
           'PASSWORD': config('DB_PASSWORD'),
           'HOST': config('DB_HOST', default='localhost'),
           'PORT': config('DB_PORT', default='5432'),
       }
   }
   ```

## 5. Apply Migrations

1. Make migrations:
   ```
   python manage.py makemigrations
   ```

2. Apply migrations:
   ```
   python manage.py migrate
   ```

## 6. Create Superuser

Create a superuser for Django admin:
```
python manage.py createsuperuser
```

## 7. Update Requirements

If using a requirements file, update it:
```
pip freeze > requirements.txt
```

## Troubleshooting

If you encounter a "permission denied for schema public" error:

1. Connect to the database as the postgres user.
2. Manually create the django_migrations table:
   ```sql
   CREATE TABLE django_migrations (
       id SERIAL PRIMARY KEY,
       app VARCHAR(255) NOT NULL,
       name VARCHAR(255) NOT NULL,
       applied TIMESTAMP NOT NULL
   );
   ```
3. Grant permissions on this table:
   ```sql
   GRANT ALL PRIVILEGES ON TABLE django_migrations TO neplink_user;
   ```

## Notes

- Replace 'neplink', 'neplink_user', and 'your_password' with your actual database name, username, and password throughout this guide.
- Always use strong, unique passwords for database users.
- Keep your `.env` file secure and never commit it to version control.

