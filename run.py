# run.py
from app import create_app, db # importing the create_app function and db instance
# importing the User model for shell context
from app.models import User 

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User} # 加入你想在 shell 中方便使用的对象

if __name__ == '__main__':
     app.run(debug=True) # start the Flask app in debug mode