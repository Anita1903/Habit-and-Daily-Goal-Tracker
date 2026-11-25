# HabitFlow — Full-Stack Habit & Daily Goal Tracker

A responsive habit tracking web application built for the CodeNova Full Stack Development Task 1.

## Features
- Dashboard with total habits, today's completions and completion percentage
- Create, edit and delete habits
- Daily check-in / uncheck with instant UI refresh
- Current streak calculation for each habit
- Seven-day check-in activity chart
- SQLite persistence; data remains after server restart
- REST API with validation and error responses
- Responsive desktop and mobile layout

## Technology stack
- Frontend: HTML5, CSS3, Vanilla JavaScript (Fetch API)
- Backend: Python, Flask (REST API)
- Database: SQLite

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended):
   - Windows: `py -m venv venv` then `venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000`

The database `habits.db` is created automatically on first run with sample habits.

## REST API
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/habits` | List habits and today's status |
| POST | `/api/habits` | Create a habit |
| PUT | `/api/habits/<id>` | Update a habit |
| DELETE | `/api/habits/<id>` | Delete a habit |
| POST | `/api/habits/<id>/checkin` | Toggle daily check-in |
| GET | `/api/stats` | Dashboard and weekly statistics |

## Database model
- `habits`: id, name, category, created_at
- `checkins`: id, habit_id, check_date; unique constraint prevents duplicate check-ins for a habit on a date

## Before submission
- Run the project and test adding, editing, checking and deleting habits.
- Add your own screenshots to a `screenshots/` folder and embed them here.
- Push this folder to a public GitHub repository.
- Include your own name and internship details in your submission if required.

## Note
This is a student project starter implementation. Review and understand the code, test it in your environment, and make any changes required by your internship evaluator before submitting.
