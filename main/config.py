import os

SERVICE_NAME = 'diplom'
SERVICE_VERSION = '1.0.0'
SERVICE_ID = '12345'

HOST = '127.0.0.1'
PORT = 8000
DEBUG = False

DATABASE_NAME = os.getenv('DATABASE_NAME', 'diplom')
DATABASE_IP = os.getenv('DATABASE_IP', 'localhost')
DATABASE_PORT = os.getenv('DATABASE_PORT', 5432)
DATABASE_USER = os.getenv('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'root')
