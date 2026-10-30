# Smart Expense and Budget Manager

## Project Overview

Smart Expense and Budget Manager is a web application designed to help users record expenses, organize spending by category, and manage weekly or monthly budgets. It aims to make personal financial tracking easier through a simple interface and authenticated access to user-specific data.

## Technology Stack

- **Backend:** Python and Django
- **API:** Django REST Framework (planned/used for API endpoints)
- **Frontend:** Django templates, HTML and CSS
- **Database:** SQLite for local development and CI; PostgreSQL through Docker Compose
- **Testing:** pytest
- **CI:** GitHub Actions

## Project Structure

```text
.
├── accounts/        # User accounts and authentication
├── budgets/         # Budget management
├── expenses/        # Expense management
├── reports/         # Reporting functionality
├── smartspend/      # Django project configuration and URLs
├── templates/       # HTML templates and shared UI components
├── tests/           # Automated tests
├── docs/            # Project documentation
├── manage.py        # Django management entry point
├── requirements.txt # Python dependencies
├── Dockerfile       # Docker image configuration
└── docker-compose.yml
```

## Local Setup

1. Install Python 3.12.
2. Clone the repository and enter the project directory.
3. Create and activate a virtual environment:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Open `http://127.0.0.1:8000/` in your browser.

## Running Tests

Run the test suite with:

```bash
pytest
```

To run a specific test file, use:

```bash
pytest -v tests/test_smoke.py
```

## Docker

Docker configuration is provided through `Dockerfile` and `docker-compose.yml`. To start the configured services, run:

```bash
docker compose up --build
```

Check the project's Docker configuration and environment variables before running it.

## Development Workflow

1. Create a feature branch from the latest `main`.
2. Make focused changes and add or update tests.
3. Run the relevant tests locally.
4. Commit and push your branch.
5. Open a pull request against `main`.
6. Request review and ensure CI passes before merging.
