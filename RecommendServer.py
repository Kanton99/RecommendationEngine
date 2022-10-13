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
class Recommend(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', help='Id dello user',required=True)
        parser.add_argument('itemId',help='id del video che sta guardando')
        args = parser.parse_args()
        itemId = args['itemId']
        usr = args['userId']
        recomendations = recommender.recommend(usr,itemId)
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

class Validate(Resource):
    def get(self):
        return recommender.validate()

api.add_resource(Validate,"/validate")
api.add_resource(Recommend, '/recommend')
api.add_resource(Base,'/')
api.add_resource(Watch,'/watcher')

if __name__ == '__main__':
    rData = parser()
    recommender = Recommender(rData)
    watchdg = listener.Listener(0,"Listener-Thread",recommender)
    try:
        watchdg.start()
        watch_running = watchdg.is_alive()
    except KeyboardInterrupt:
        watchdg.join()
    app.run(debug=True,use_reloader=False)