import os


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///checkin.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    DEV_RESET_KEY = "gator123"
    SECRET_KEY = 'af321118882c810342bacf89'
    JWT_SECRET_KEY = "your-secret-key"

