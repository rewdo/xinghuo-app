import os
from datetime import timedelta


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # MySQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'xinghuo')
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # WeChat Mini Program
    WX_APPID = os.getenv('WX_APPID', 'wx5890cbc3c95f6599')
    WX_SECRET = os.getenv('WX_SECRET', '')

    # WeChat Pay
    WX_MCHID = os.getenv('WX_MCHID', '')
    WX_API_KEY = os.getenv('WX_API_KEY', '')
    WX_NOTIFY_URL = os.getenv('WX_NOTIFY_URL', '')
    WX_CERT_PATH = os.getenv('WX_CERT_PATH', '')
    WX_KEY_PATH = os.getenv('WX_KEY_PATH', '')

    # JWT
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 72))
    JWT_EXPIRATION_DELTA = timedelta(hours=JWT_EXPIRATION_HOURS)

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # LBS - default search radius (meters)
    DEFAULT_SEARCH_RADIUS = 3000
    MAX_SEARCH_RADIUS = 10000

    # Platform commission rate (10%)
    PLATFORM_COMMISSION_RATE = 0.10
