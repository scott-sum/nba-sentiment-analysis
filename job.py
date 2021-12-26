from wsgi import app
from apscheduler.schedulers.background import BackgroundScheduler
from nba_sentiment_analysis import job

sched = BackgroundScheduler()

@sched.scheduled_job('interval', hours=1)
def update():
	job(app)

sched.start()