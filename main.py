import os
from app import flask_app

def run_flask():
    # Set FLASK_ENV to development
    os.environ['FLASK_ENV'] = 'development'
    flask_app.run(port=5000, host="localhost", debug=True)

if __name__ == "__main__":
    # Running flask app instance on port 5000
    run_flask()
