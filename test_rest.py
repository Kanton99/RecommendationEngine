import json
import threading
from parser import parser

from flask import Flask, request
from flask_restful import Api, Resource, reqparse

import listener
from recommender import Recommender

app = Flask(__name__)
api = Api(app)
watch_running = False
users = []
videos = []
class Recommend(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', help='Id dello user',required=True)
        parser.add_argument('assetId',help='id del video che sta guardando')
        args = parser.parse_args()
        assetId = args['assetId']
        usr = args['userId']
        recomendations = recommender.recommend(usr,assetId)
        return recomendations
class Base(Resource):
    def get(self):
        return "The server is running"     

class Watch(Resource):
    def get(self):
        if watch_running:
            return "wathcer is running"
        else:
            return "watcher is not running"

api.add_resource(Recommend, '/recommend')
api.add_resource(Base,'/')
api.add_resource(Watch,'/watcher')

if __name__ == '__main__':
    rData = parser()

    for i in rData[0]:
        if i[0] not in users:
            users.append(i[0])
        if i[1] not in videos:
            videos.append(i[1])

    for i in rData[1]:
        if i['assetId'] not in videos:
            videos.append(i['assetId'])

    recommender = Recommender(rData)
    watchdg = listener.Listener(0,"Listener-Thread",recommender)
    try:
        watchdg.start()
        watch_running = watchdg.is_alive()
    except KeyboardInterrupt:
        watchdg.join()
    
    app.run(debug=True,use_reloader=True)