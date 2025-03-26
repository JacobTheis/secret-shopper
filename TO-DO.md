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

- [ ] **Configure Settings:**
    - [ ] Move the default `settings.py` into `config/settings/base.py`.
    - [ ] Create `config/settings/__init__.py`.
    - [ ] Create `config/settings/development.py` (inheriting from `base.py`).
    - [ ] Create `config/settings/production.py` (inheriting from `base.py`).
    - [ ] Update `manage.py`, `config/wsgi.py`, and `config/asgi.py` to use the new settings structure (e.g., point to `config.settings.development` by default).
    - [ ] Configure `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT` in `config/settings/base.py`.
    - [ ] Configure `TEMPLATES` setting in `config/settings/base.py` to include the global `templates` directory.

- [ ] **Create Core Apps:**
    - [ ] Navigate to the `apps/` directory.
    - [ ] Create initial apps using `python ../manage.py startapp <app_name>`:
        - [ ] `accounts`
        - [ ] `dashboard`
        - [ ] `personas`
        - [ ] `targets`
        - [ ] `communications`
        - [ ] `shops`
        - [ ] `reports`
    - [ ] Add these apps to `INSTALLED_APPS` in `config/settings/base.py`, prefixing with `apps.` (e.g., `apps.accounts`).

- [ ] **Set Up Dependency Management:**
    - [ ] Create `requirements/base.txt` (add `django`).
    - [ ] Create `requirements/development.txt` (add `-r base.txt`, linters like `flake8`, type checkers like `mypy`).
    - [ ] Create `requirements/production.txt` (add `-r base.txt`, production server like `gunicorn`).
    - [ ] Install development requirements (`pip install -r requirements/development.txt`).

- [ ] **Initialize Version Control:**
    - [ ] Initialize a git repository (`git init`).
    - [ ] Create a `.gitignore` file. Ask me to add the standard Python/Django `.gitignore` content if needed.
    - [ ] Make the initial commit.

- [ ] **Set Up Environment Configuration:**
    - [ ] Create a `.env.example` file outlining necessary environment variables (e.g., `SECRET_KEY`, `DEBUG`, `DATABASE_URL`).
    - [ ] Create a `.env` file (and add it to `.gitignore`).
    - [ ] Integrate `python-dotenv` to load `.env` in settings (install `python-dotenv`, add code to `manage.py` and `wsgi.py`/`asgi.py`).

- [ ] **Integrate Celery:**
    - [ ] Install Celery and a message broker (e.g., Redis: `pip install celery redis`).
    - [ ] Create `config/celery.py` to define the Celery application instance.
    - [ ] Import and load tasks in `config/__init__.py`.
    - [ ] Configure Celery settings (broker URL, result backend, etc.) in `config/settings/base.py`.
    - [ ] Add Celery worker command to project documentation/README.

- [ ] **Initial Database Migration:**
    - [ ] Run `python manage.py makemigrations`.
    - [ ] Run `python manage.py migrate`.
