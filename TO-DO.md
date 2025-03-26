# TO-DO Checklist: Initial Project Setup

- [x] **Initialize Django Project:**
    - [x] Create the main project directory (`re-secret-shop`).
    - [x] Set up a virtual environment (e.g., `python -m venv venv`).
    - [x] Activate the virtual environment.
    - [x] Install Django (`pip install django`).
    - [x] Start the Django project (`django-admin startproject config .`).
    - [x] Verify the basic Django project runs (`python manage.py runserver`).

- [x] **Establish Project Structure:**
    - [x] Create the `apps/` directory.
    - [x] Create the `static/` directory and subdirectories (`css/`, `js/`, `images/`, `vendors/`).
    - [x] Create the `templates/` directory and subdirectories (`base.html`, `partials/`, `emails/`, `errors/`).
    - [x] Create the `media/` directory.
    - [x] Create the `utils/` directory.
        - [x] Create `utils/__init__.py`.
        - [x] Create `utils/ai_integration/` directory and `utils/ai_integration/__init__.py`.
        - [x] Create `utils/email/` directory and `utils/email/__init__.py`.
        - [x] Create `utils/validators.py`.
    - [x] Create the `requirements/` directory.

- [x] **Configure Settings:**
    - [x] Move the default `settings.py` into `config/settings/base.py`.
    - [x] Create `config/settings/__init__.py`.
    - [x] Create `config/settings/development.py` (inheriting from `base.py`).
    - [x] Create `config/settings/production.py` (inheriting from `base.py`).
    - [x] Update `manage.py`, `config/wsgi.py`, and `config/asgi.py` to use the new settings structure (e.g., point to `config.settings.development` by default).
    - [x] Configure `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT` in `config/settings/base.py`.
    - [x] Configure `TEMPLATES` setting in `config/settings/base.py` to include the global `templates` directory.

- [x] **Create Core Apps:**
    - [x] Navigate to the `apps/` directory.
    - [x] Create initial apps using `python manage.py startapp <app_name> apps/<app_name>`:
        - [x] `accounts`
        - [x] `dashboard`
        - [x] `personas`
        - [x] `targets`
        - [x] `communications`
        - [x] `shops`
        - [x] `reports`
    - [x] Add the app configurations (e.g., `apps.accounts.apps.AccountsConfig`) to `INSTALLED_APPS` in `config/settings/base.py` *after* creating the apps.

- [x] **Set Up Dependency Management:**
    - [x] Create `requirements/base.txt` (add `django`).
    - [x] Create `requirements/development.txt` (add `-r base.txt`, linters like `flake8`, type checkers like `mypy`).
    - [x] Create `requirements/production.txt` (add `-r base.txt`, production server like `gunicorn`).
    - [x] Install development requirements (`pip install -r requirements/development.txt`).

- [x] **Initialize Version Control:**
    - [x] Initialize a git repository (`git init`).
    - [x] Create a `.gitignore` file. Ask me to add the standard Python/Django `.gitignore` content if needed.
    - [x] Make the initial commit.

- [x] **Set Up Environment Configuration:**
    - [x] Create a `.env.example` file outlining necessary environment variables (e.g., `SECRET_KEY`, `DEBUG`, `DATABASE_URL`).
    - [x] Create a `.env` file (and add it to `.gitignore`).
    - [x] Integrate `python-dotenv` to load `.env` in settings (install `python-dotenv`, add code to `manage.py` and `wsgi.py`/`asgi.py`).

- [x] **Integrate Celery:**
    - [x] Install Celery and a message broker (e.g., Redis: `pip install celery redis`).
    - [x] Create `config/celery.py` to define the Celery application instance.
    - [x] Import and load tasks in `config/__init__.py`.
    - [x] Configure Celery settings (broker URL, result backend, etc.) in `config/settings/base.py`.
    - [x] Add Celery worker command to project documentation/README.

- [x] **Initial Database Migration:**
    - [x] Run `python manage.py makemigrations`.
    - [x] Run `python manage.py migrate`.
