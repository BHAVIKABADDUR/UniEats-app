# UniEats

A web-based cafeteria management system with personalized food recommendations.

## Features

- User authentication (login/register)
- Menu browsing with categories
- Shopping cart functionality
- Order history
- Personalized food recommendations
- Profile management
- Responsive design

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python db_setup.py
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

- `app.py`: Main Flask application
- `db_setup.py`: Database initialization script
- `templates/`: HTML templates
- `static/`: Static files (CSS, images)
- `instance/`: Database file (created after running db_setup.py)

## Technologies Used

- Flask: Web framework
- SQLite: Database
- Bootstrap: Frontend framework
- scikit-learn: Recommendation system
- Flask-Bcrypt: Password hashing 