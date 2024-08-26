from dotenv import load_dotenv
import os

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Centralize Dynamic CRUD API")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
APP_DOCS_URL = os.getenv("APP_DOCS_URL", "/")
APP_REDOC_URL = os.getenv("APP_REDOC_URL", "/redoc")
APP_SWAGGER_UI_OAUTH2_REDIRECT_URL = os.getenv(
    "APP_SWAGGER_UI_OAUTH2_REDIRECT_URL", "/docs/oauth2-redirect"
)
APP_HOST = os.getenv("APP_HOST", "localhost")
APP_PORT = os.getenv("APP_PORT", "8080")
SECRET_KEY = os.getenv("SECRET_KEY", "MySuperSecretKey")

PASSWORD_SALT = os.getenv("PASSWORD_SALT", "db_manager")

# DB_USER = os.environ.get("DB_USERNAME", "postgres")
# DB_PASS = os.environ.get("DB_PASSWORD", "postgres")
DB_ENGINE = os.environ.get("DB_ENGINE", "postgresql+psycopg2")
DB_APPLICATION_NAME = os.environ.get("DB_APPLICATION_NAME", None)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")

AUTHORIZATION_STATUS = os.environ.get("AUTHORIZATION_STATUS", "INACTIVE").lower()
# DB_CONNECT_URL = f'{DB_ENGINE}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

APP_SETTINGS = dict(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url=APP_DOCS_URL,
    redoc_url=APP_REDOC_URL,
    swagger_ui_oauth2_redirect_url=APP_SWAGGER_UI_OAUTH2_REDIRECT_URL,
)

LOG_FILE_ROTATION_INTERVAL = os.getenv("LOG_FILE_ROTATION_INTERVAL", "D")


JWT_SETTINGS = {
    "access_token_lifetime": int(os.getenv("ACCESS_TOKEN_LIFETIME", "24")),  # hours
    "refresh_token_lifetime": int(os.getenv("REFRESH_TOKEN_LIFETIME", "168")),  # hours
}

# API Documentation
DOCS_DESCRIPTION = "`Centralize Dynamic API for Database` is a powerful and flexible API that serves \
                    as a centralized gateway for accessing and managing dynamic database resources.  \
                    It abstracts the complexity of database operations, providing a simplified and  \
                    unified interface for `CRUD operations`.\
                    With its dynamic nature, the API enables efficient and secure access to diverse \
                    database resources in a centralized manner."
