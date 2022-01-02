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


# consumer_key = 'roMEay9khmq49uQA3XUH6amMO'
# consumer_secret = 'hqM9EhFj8R8PHnZSoePWKukqfxCN0q4ssbyXCD07ffuhodA61H'
# access_token = '1375426756358905858-VW8JUPy5DGfPoAKMOblOMH495JAyn5'
# access_token_secret = '8v9cANUCxNMWubiGJBK5s1HHo7Be88RobMIoemjcqS7TF'

# NEWS API
news_api_key = os.environ.get('NEWS_API_KEY')
# API_KEY = 'a119411c756f40c0be74c11bcf2c8521'


SQLALCHEMY_TRACK_MODIFICATIONS = False
TEMPLATES_AUTO_RELOAD = True