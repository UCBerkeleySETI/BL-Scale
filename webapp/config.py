"""App configuration."""
from os import environ
import redis


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')

    # Flask-Session
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(environ.get('SESSION_REDIS'))
