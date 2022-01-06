import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
	SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
SECRET_KEY = os.environ.get('SECRET_KEY')


# Twitter API credentials
tw_consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
tw_consumer_secret_key = os.environ.get('TWITTER_CONSUMER_SECRET_KEY')
tw_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
tw_secret_access_token = os.environ.get('TWITTER_SECRET_ACCESS_TOKEN')



# NEWS API
news_api_key = os.environ.get('NEWS_API_KEY')


SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True