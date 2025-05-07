from dotenv import load_dotenv
import os
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Get the environment from FLASK_ENV, default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)
 
if __name__ == '__main__':
    app.run(debug=True) 