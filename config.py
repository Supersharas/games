import os

class Config(object):
	DEBUG = True
	SECRET_KEY = os.environ.get('SECRET_KEY')  or b'_5#y2L"F4Q8z\n\xec]/'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
	SQLALCHEMY_TRACK_MODIFICATIONS = False