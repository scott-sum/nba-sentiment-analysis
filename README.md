# NBA Sentiment Analysis

A web application that allows users to conduct sentiment analysis on any NBA team. It works by leveraging the Tweepy API to gather recent tweets, calculate their sentiment, and aggregate the results into a sentiment score. 

These scores are visualized in the form of bar plots and line graphs using Matplotlib. In addition, the most popular words in the tweets are displayed in a word cloud.

Users may be wondering why a NBA team ended up with their sentiment score. Therefore, I have also showed some of the tweets used in the sentiment analysis, as well as some recent news articles about the team. The articles were fetched with the NewsAPI.

Users can also sign up and login to view their profile, which is a collection of their saved teams and their current sentiment analysis results.

Since the sentiment is always changing, I run a daily data update job using Heroku Scheduler which will conduct sentiment analysis for each team, create the visuals, and store them in AWS S3. The sentiment data is placed into a PostgreSQL database.

Technologies Used: Python, Flask, Matplotlib, Scikit-learn, AWS S3, PostgreSQL, Heroku, HTML, CSS

Check out my app here: https://nbasentimentanalysis.herokuapp.com