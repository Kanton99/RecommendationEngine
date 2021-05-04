import json
import os
import sys

def readConfig():
    with open("config.json","r") as c:
        config = json.loads(c.readline())
        return config


def parser():
    config = readConfig()

    videos = []
    videos_ids = []
    users = []
    directory = os.fsdecode(config["data directory location"])

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(config["asset Data File Pattern"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        video = json.loads(jsonObj)
                        if video not in videos:
                            videos.append(video)
                            videos_ids.append(video[config["asset ID key"]])
            except:
                print(filename +": "+sys.exc_info()[0])
        if filename.startswith(config["user Interacion File Patter"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        interaction = json.loads(jsonObj)
                        userId = interaction.get(config["user ID key"])
                        video = interaction.get(config["asset ID key"])
                        if (userId, video) not in users:
                            users.append((userId, video))
            except:
                print(filename +": "+sys.exc_info()[0])
        
    return (users, videos)

def file_parser(file):
    videos = []
    interactions = []
    comps = str(file).split('/')
    if comps[len(comps)-1].startswith("interactions_users"):
        with open(file,"r") as f:
            for jsnObj in f:
                inter = json.loads(jsnObj)
                user = inter['userId']
                asset = inter['assetId']
                if (user,asset) not in interactions:
                    interactions.append((user,asset))

    return (interactions,videos)            


