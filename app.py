from flask import Flask, render_template, request
from flask_pymongo import PyMongo, DESCENDING
import requests

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/youtube"
mongo = PyMongo(app)

YT_API_KEY = 'AIzaSyAL9kglPFbrlBkdBktibNoW3rSAelwFmCs'
YT_API_URL = 'https://www.googleapis.com/youtube/v3/videos'


@app.route('/')
def index():
    mx_most_viewed = mongo.db.MXvideos.find({'views': {'$gt': 1000000}}, limit=3).sort('views', DESCENDING)
    return render_template('index.html', videos=mx_most_viewed)


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search-bar')
    search_type = request.form.get('search-type')

    videos = mongo.db.MXvideos.find({f'{search_type}': {'$regex': f'{search_query}', '$options': 'i'}})

    return render_template('search.html', videos=videos)


@app.route('/video/<string:video_id>')
def video(video_id):
    video = mongo.db.MXvideos.find({'video_id': video_id})

    return render_template('video.html', video=video)


@app.route('/insert', methods=['POST'])
def insert():
    video_url = request.form.get('video-url')

    response = requests.get(YT_API_URL, params={'part': 'snippet, statistics', 'id': video_url, 'key': YT_API_KEY})

    video_data = response.json()['items'][0]
    snippet = video_data['snippet']
    statistics = video_data['statistics']
    tags = ''

    for tag in video_data['snippet']['tags']:
        tags += f'"{tag}"|'

    document = {
        'video_id': video_data['id'],
        'date': snippet['publishedAt'],
        'title': snippet['title'],
        'channel_title': snippet['channelTitle'],
        'category_id': snippet['categoryId'],
        'tags': tags,
        'views': statistics['viewCount'],
        'likes': statistics['likeCount'],
        'dislikes': statistics['dislikeCount'],
        'comment_count': statistics['commentCount'],
        'thumbnail_link': snippet['thumbnails']['default']['url'],
        'description': snippet['description'],
        'user_inserted': 'true'
    }

    return render_template('insert.html')



