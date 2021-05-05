import json
import os
import sys

def readConfig():
    with open("config.json","r") as c:
        config = json.load(c)
        return config


def parser():
    config = readConfig()

    assets = []
    users = []
    directory = os.fsdecode(config["data directory location"])

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(config["asset Data File Pattern"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        asset = json.loads(jsonObj)
                        if asset not in assets:
                            assets.append(asset)
                            asset['tags'] = asset[config['asset tags']]
            except:
                print(filename +": "+sys.exc_info()[0])
        if filename.startswith(config["user Interacion File Patter"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        interaction = json.loads(jsonObj)
                        userId = interaction.get(config["user ID key"])
                        asset = interaction.get(config["asset ID key"])
                        if (userId, asset) not in users:
                            users.append((userId, asset))
            except:
                print(filename +": "+sys.exc_info()[0])
        
    return (users, assets)

def file_parser(file):
    assets = []
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

    return (interactions,assets)            


