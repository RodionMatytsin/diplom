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

SECRET_KEY = 'kAlu7NqZwoWx7MaRwoXv9Qc4woZnAp=='

API_MEDIA = os.getenv('API_MEDIA', f'/api/attachments/')
# 1 * 1024 * 1024 * 1024 -- 1Gb
MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE', 1 * 1024 * 1024 * 1024)

PHOTO_FORMAT = ['image/jpeg', 'image/png', 'image/webp']
VIDEO_FORMAT = ['video/quicktime', 'video/mp4']
MAIN_PATH = os.path.dirname(os.path.realpath(__file__))[:-5]
MEDIA_FOLDER = os.path.join(MAIN_PATH, 'media_heap')
PROD = True
FFMPEG = '/home/dev/bin/'
