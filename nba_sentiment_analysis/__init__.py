from flask import Flask
from .extensions import db, login_manager
from .routes import auth as auth_blueprint
from .routes import main as main_blueprint
from .models import User, Score
from .functions import analysis, update_graphs
from .commands import create_tables
from apscheduler.schedulers.background import BackgroundScheduler
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import atexit
from datetime import datetime
from .s3 import *

teams = ["atlanta hawks","boston celtics","brooklyn nets","charlotte hornets","chicago bulls","cleveland cavaliers",
         "dallas mavericks","denver nuggets","detroit pistons","golden state warriors","houston rockets",
         "indiana pacers","los angeles clippers","los angeles lakers","memphis grizzlies","miami heat","milwaukee bucks",
         "minnesota timberwolves","new orleans pelicans","new york knicks","oklahoma city thunder","orlando magic",
         "philadelphia 76ers","phoenix suns","portland trail blazers","sacramento kings","san antonio spurs",
         "toronto raptors","utah jazz","washington wizards"]

def job(app):
    with app.app_context():
        for team in teams:
            team_nospace = team.replace(" ", "_")
            team_analysis = functions.analysis(team, 100)
            team_score = team_analysis[0] - team_analysis[1]
            db.session.add(Score(date=datetime.now(), team_name=team, score=team_score))
            db.session.commit()

            scores = Score.query.filter_by(team_name=team).order_by(Score.date).all()
            x_date = []
            y_score = []
            for score in scores:
                x_date.append(score.date)
                y_score.append(score.score)
            plt.clf()
            plt.title(f"Sentiment for { team.title() } over time")
            plt.xlabel("Time")
            plt.ylabel("Sentiment Score")
            plt.plot(x_date, y_score)
            plt.gcf().autofmt_xdate()
            update_graphs(f'nba_sentiment_analysis/static/graphs/{team_nospace}/', 'sentiment_vs_time.png')
            file_path = f'nba_sentiment_analysis/static/graphs/{team_nospace}/sentiment_vs_time.png'
            plt.savefig(file_path, transparent=True)
            plt.close()
            upload_to_s3(BUCKET_NAME, file_path, team_nospace)
            



def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')

    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
    scheduler.add_job(lambda: job(app), trigger='interval', hours=5)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    app.cli.add_command(create_tables)

    return app
