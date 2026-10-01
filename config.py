import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError(
        'SECRET_KEY environment variable is not set. '
        'Please create a .env file with SECRET_KEY=your_random_string '
        'or export it in your shell. '
        'You can generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
    )

MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'tourist_db')

DEBUG = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')