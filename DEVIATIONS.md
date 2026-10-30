# Deviation Log

This document records deviations from the original project plan and requirements.

| ID | Original Plan / Requirement | Deviation | Reason / Notes |
|---|---|---|---|
| DEV-01 | Use Jenkins for continuous integration | GitHub Actions is used instead of Jenkins | CI workflow is managed in the GitHub repository. |
| DEV-02 | Follow the original six-sprint plan (Sprints 1–6) | The work is organized into two five-day sprints | The team is using a shorter delivery schedule. |
| DEV-03 | Use the specified original technology stack | Django and Django REST Framework are used | This is the team's selected backend stack. |
| DEV-04 | Use the originally planned UI approach | Django templates are used alongside a REST API | This supports server-rendered pages and API endpoints. |
| DEV-05 | Use only the fields listed in the original SAD for the User model | The User model includes a `username` field | This field supports user identification and authentication. |
| DEV-06 | Use the originally planned database configuration in all environments | SQLite is used for local development and CI, while PostgreSQL is configured through Docker Compose | This allows a lightweight local setup and a PostgreSQL containerized environment. |

## Maintenance

Add a new row whenever the team makes an agreed deviation from the original plan or requirements. Record the change and its reason so the project history remains transparent.
