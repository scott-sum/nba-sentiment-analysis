from flask import Flask, render_template, flash, request, redirect, url_for, Blueprint
from . import functions
from flask_login import login_required, current_user
from .settings import news_api_key
from .models import Score, SavedTeam, User
from .extensions import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .s3 import *

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template('home.html')


@main.route("/analysis", methods=['GET', 'POST'])
def analysis():
    team_chosen = request.form.get('team')
    team_nospace = team_chosen.replace(" ", "_")
    tweets = functions.analysis(team_chosen, 100, mode=2)
    url = ('https://newsapi.org/v2/everything?'
           f'q="{team_chosen}"&'
           f'from={datetime.today() - timedelta(7)}&'
           'sortBy=popularity&'
           f'apiKey={news_api_key}')
    news_articles = functions.get_news(url, 5)

    download_from_s3(BUCKET_NAME, f'{team_nospace}/wordcloud.png', f'/static/graphs/{team_nospace}/wordcloud.png')
    download_from_s3(BUCKET_NAME, f'{team_nospace}/sentiment_vs_time.png', f'/static/graphs/{team_nospace}/sentiment_vs_time.png')
    download_from_s3(BUCKET_NAME, f'{team_nospace}/bar.png', f'/static/graphs/{team_nospace}/bar.png')

    return render_template('results.html', team=team_chosen, tweets=tweets, news=news_articles,
                           bar_url=f'/static/graphs/{team_nospace}/bar.png',
                           wc_url=f'/static/graphs/{team_nospace}/wordcloud.png',
                           time_url=f'/static/graphs/{team_nospace}/sentiment_vs_time.png')


# can only see if more than two entries in same team
# with base path, get the userid, team (from the filename), and show figure
@main.route('/profile', methods=['GET'])
@login_required
def profile():
    saved_teams = SavedTeam.query.filter_by(user_id=current_user.id).order_by(SavedTeam.team_name).all()
    urls = []
    team_names = [team.team_name for team in saved_teams]
    score_stats = []
    for team in saved_teams:
        team_nospace = team.team_name.replace(" ", "_")
        bar_url = f'/static/graphs/{team_nospace}/bar.png'
        wc_url = f'/static/graphs/{team_nospace}/wordcloud.png'
        time_url = f'/static/graphs/{team_nospace}/sentiment_vs_time.png'

        download_from_s3(BUCKET_NAME, f'{team_nospace}/bar.png', bar_url)
        download_from_s3(BUCKET_NAME, f'{team_nospace}/wordcloud.png', wc_url)
        download_from_s3(BUCKET_NAME, f'{team_nospace}/sentiment_vs_time.png', time_url)

        urls.append([bar_url, wc_url, time_url])

        # get average, min, max sentiment score for team
        count = 0
        sum_scores = 0
        curmin = float('inf')
        curmax = float('-inf')
        scores_last_wk = Score.query.filter(Score.date >= (datetime.today() - timedelta(7)),
                                            Score.team_name == team.team_name).all()

        for score in scores_last_wk:
            count += 1
            sum_scores += score.score
            if score.score < curmin:
                curmin = score.score
            if score.score > curmax:
                curmax = score.score
        average_score = sum_scores / count
        score_stats.append([round(average_score), round(curmin), round(curmax)])

    return render_template('profile.html', urls=urls, name=current_user.name, teams=team_names, stats=score_stats)


@main.route('/profile', methods=['POST'])
@login_required
def save_team():
    team_to_save = request.form.get('team')
    print("got team")
    if SavedTeam.query.filter(SavedTeam.user_id == current_user.id, SavedTeam.team_name == team_to_save).first() is None:
        db.session.add(SavedTeam(user_id=current_user.id, team_name=team_to_save))
        db.session.commit()
    else:
        flash("This team has already been saved")
    return redirect(url_for('main.profile'))


@main.route('/remove_team/<team_to_remove>')
@login_required
def remove_team(team_to_remove):
    remove = SavedTeam.query.filter(SavedTeam.user_id == current_user.id, SavedTeam.team_name == team_to_remove).first()
    db.session.delete(remove)
    db.session.commit()
    return redirect(url_for('main.profile'))


###### AUTHENTICATION ##################################################################################################

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))






