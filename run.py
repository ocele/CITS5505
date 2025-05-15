# run.py
from app import create_app, db # importing the create_app function and db instance
# importing the User model for shell context
from app.models import User 
from dotenv import load_dotenv
import os

app = create_app()

# load .env file
load_dotenv()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
     app.run(debug=True) # start the Flask app in debug mode

if not os.getenv('USDA_API_KEY'):
    raise RuntimeError("Missing USDA_API_KEY in environment")