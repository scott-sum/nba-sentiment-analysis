import nltk
import tweepy
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer

import matplotlib.pyplot as plt
import requests, re, os, string

from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .settings import tw_access_token, tw_secret_access_token, tw_consumer_secret_key, tw_consumer_key

auth = tweepy.OAuthHandler(tw_consumer_key, tw_consumer_secret_key)
auth.set_access_token(tw_access_token, tw_secret_access_token)
api = tweepy.API(auth, wait_on_rate_limit=True)

stop_words = stopwords.words('english')
tw_tokenizer = TweetTokenizer()

def update_graphs(base_dir, filename):
    # print(base_dir)
    # print(os.path.isdir(base_dir))
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
        print("created directory ", base_dir)
    file_path = os.path.join(base_dir, filename)
    print('filepath ', file_path, ' ', os.path.isfile(file_path))
    if os.path.isfile(file_path):
        print('removed existing file')
        os.remove(file_path)

def sentiment_distribution(tweets, mode=1):
    num_pos = 0
    num_neg = 0
    num_neutral = 0
    tweets_info = []
    for tweet in tweets:
        tweet_props = {'created_at': tweet._json['created_at'],
                       'text': tweet._json['text'],
                       'user': tweet._json['user']['name'],
                       'user_img': tweet._json['user']['profile_image_url_https'],
                       'link': f"https://twitter.com/i/web/status/{tweet._json['id']}"}
        tweets_info.append(tweet_props)
        if mode == 2:
            continue
        sentiment_score = SentimentIntensityAnalyzer().polarity_scores(tweet.text)
        if sentiment_score['compound'] >= 0.05:
            num_pos += 1
        elif sentiment_score['compound'] <= -0.05:
            num_neg += 1
        else:
            num_neutral += 1
    if mode == 2:
        return tweets_info
    else:
        return num_pos, num_neg, num_neutral, tweets_info


def preprocess_tweets(tweets, tokenizer):
    tokens = []
    for i in range(len(tweets)):
        tweet = tweets[i]['text']
        remove_nums = re.sub(r'\d+', '', tweet)
        remove_punct = "".join([word.lower() for word in remove_nums if word not in string.punctuation])
        tkns = tokenizer.tokenize(remove_punct)
        processed_tokens = []
        for tkn in tkns:
            if tkn not in stop_words:
                processed_tokens.append(tkn)
        tokens.extend(processed_tokens)
    return tokens


def analysis(team_name, num_tweets, mode=1):
    team_nospace = team_name.replace(" ", "_")
    if mode != 1:
        tweets = tweepy.Cursor(api.search_tweets, q=team_name).items(10)
        return [(tweet['user'], tweet['user_img'], tweet['created_at'], tweet['text'], tweet['link'])
                for tweet in sentiment_distribution(tweets, mode=2)]
    tweets = tweepy.Cursor(api.search_tweets, q=team_name).items(num_tweets)
    positive, negative, neutral, tweet_list = sentiment_distribution(tweets)
    bar_labels = ['Negative', 'Neutral', 'Positive']
    scores_list = [positive, negative, neutral]
    plt.clf()
    plt.bar(bar_labels, scores_list)
    plt.title('Sentiment Scores for Tweets')
    plt.xlabel('Score')
    plt.ylabel('Frequency')
    update_graphs(f'nba_sentiment_analysis/static/graphs/{team_nospace}/', 'bar.png')
    plt.savefig(f'nba_sentiment_analysis/static/graphs/{team_nospace}/bar.png', transparent=True)
    plt.close()

    tokens = preprocess_tweets(tweet_list, tw_tokenizer)
    word_frequencies = nltk.FreqDist(tokens)
    word_cloud = WordCloud(background_color='white').generate_from_frequencies(word_frequencies)
    plt.clf()
    plt.imshow(word_cloud)
    # plt.title("Recent Tweets Wordcloud")
    plt.axis('off')
    plt.tight_layout(pad=0)
    update_graphs(f'nba_sentiment_analysis/static/graphs/{team_nospace}/', 'wordcloud.png')
    plt.savefig(f'nba_sentiment_analysis/static/graphs/{team_nospace}/wordcloud.png', transparent=True, facecolor='w', bbox_inches='tight')
    plt.close()
    return positive, negative, neutral, tweet_list[:10]

#################### NEWS

def get_news(url, num_articles=5):
    response = requests.get(url).json()
    if response is not None:
        articles = response['articles']
        article_info = []
        clean_regex = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        for i in range(num_articles):
            ret = (articles[i]['title'],
                   re.sub(clean_regex, '', articles[i]['description']),
                   articles[i]['url'],
                   articles[i]['urlToImage'],
                   articles[i]['publishedAt'])
            article_info.append(ret)
        return article_info
    return None

