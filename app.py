from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo, DESCENDING
import requests
import re

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
    print(videos)
    if videos.count() == 0:
        return render_template('error.html', message='No se encuentran videos con esas caracteristicas')

    return render_template('ListVideos.html', videos=videos)


@app.route('/video/<string:video_id>')
def video(video_id):
    video = mongo.db.MXvideos.find({'video_id': video_id})

    return render_template('index.html', video=video)


@app.route('/insert', methods=['POST'])
def insert():
    video_url = request.form.get('video-url')
    match = re.search('^https://www.youtube.com/watch?', video_url)

    if not match:
        return render_template('error.html', message='La URL del video no es correcta.')

    video_id = video_url[32:]

    response = requests.get(YT_API_URL, params={'part': 'snippet, statistics', 'id': video_id, 'key': YT_API_KEY})

    if response.json()['pageInfo']['totalResults'] == 0:
        return render_template('error.html', message="No se encontró un vídeo con la URL.")

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

    res = mongo.db.MXvideos.insert_one(document)
    print(res.inserted_id)

    if not res.inserted_id:
        return render_template('error.html', message='No se pudo agregar el video a la base de datos.')

    return redirect(url_for('index'))


@app.route('/delete/<string:video_id2>', methods=['GET', 'POST'])
def delete(video_id2):
    # video_id = request.form.get('video-id')
    print("video id delete" + video_id2)

    res = mongo.db.MXvideos.delete_one({'video_id': video_id2})

    if res.deleted_count == 0:
        return render_template('error.html', message='El video no fue eliminado')

    return redirect(url_for('index'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    video_id = request.form.get('video-id')
    update_type = request.form.get('update-type')
    update_value = request.form.get('update-value')

    res = mongo.db.MXvideos.update_one({'video_id': video_id}, {"$set": {f'{update_type}': f'{update_value}'}})

    if res.modified_count == 0:
        return render_template('error.html', message='Los datos no se actualizaron')
    return render_template('Update.html', video=video_id)


@app.route('/video-data/<string:video_id>')
def videoData(video_id):
    videoID = video_id
    print(videoID)
    videos = mongo.db.MXvideos.find({'video_id': videoID})


    for items in videos:
        print(items)

    return render_template('Update.html', videos=videoID)
