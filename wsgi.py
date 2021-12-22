from nba_sentiment_analysis import create_app
from nba_sentiment_analysis.extensions import db

app = create_app()
db.create_all(app)
