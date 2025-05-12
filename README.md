# CITS5505 Group Project

# DailyBite
## Group Members

| GitHub Username      | Student Name     | Student ID |
|----------------------|------------------|------------|
| ocele                | Jiahe Fan        | 24014534   |
| vandvennie           | Veronica Lyu     | 24516605   |
| Zongzi-Zoe-Shuhan    | Shuhan Wang      | 24057211   |
| MuzzleThing          | Haoran Yu        | 24180266   |

## Project Overview

DailyBite is a web application to help users record and track their daily meals and nutrition intake. Users can:

- Add custom meals and automatically calculate calories, protein, carbs, and fats  
- View charts and dashboards showing daily, weekly, and monthly nutrition trends and rankings  
- Share their nutrition data and charts with friends  
- Manage favorite meals for quicker entry  

## Design & Tech Stack

**Requirement and Prototype**  
https://o67l5u.axshare.com

**Frontend**  
- HTML5 & CSS3 & Bootstrap  
- JavaScript, jQuery & AJAX  

**Backend**  
- Python 3.8+ & Flask  
- SQLite via SQLAlchemy ORM  

**Architecture**  
- **Model-View-Controller**  
  - **Model:** SQLAlchemy models  
  - **View:** Jinja2 templates + static assets  
  - **Controller:** Flask routes & business logic  

**Key Modules**  
- **Dashboard:** nutrition charts & leaderboards  
- **AddMeal:** create/edit meals with real-time nutrient calculation  
- **Share:** generate shareable links and display charts  
- **Settings:** user preferences and custom meal management  


## Local Setup

### Requirements

- Python 3.8+  
- SQLite (bundled with Python standard library)  

### Install Dependencies

```bash
git clone https://github.com/ocele/CITS5505.git
cd CITS5505
python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
````

### Configure the Database

```bash
# Create the SQLite database and seed initial data
python seed.py
```

### Run the Application

```bash
export FLASK_APP=run.py
export FLASK_ENV=development   # optional: enables debug mode
flask run --host=0.0.0.0 --port=5000
```

Open your browser at [http://localhost:5000](http://localhost:5000)

## Testing

This project uses **pytest**. All test files are under the `tests/` directory.

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Generate coverage report
pytest --cov=app --cov-report=html
```