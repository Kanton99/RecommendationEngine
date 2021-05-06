import json
import os
import sys
from lightfm.datasets import fetch_movielens

def readConfig():
    with open("config.json","r") as c:
        config = json.load(c)
        return config

def parser():
    config = readConfig()
    if config["use_movielens"]:
        return fetch_movielens()
    items = []
    users = []
    directory = os.fsdecode(config["data_directory_location"])

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith(config["item_data_file_pattern"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        item = json.loads(jsonObj)
                        if item not in items:
                            items.append(item)
                            item['tags'] = item[config['item_tags']]
            except:
                print(filename +": "+sys.exc_info()[0])
        if filename.startswith(config["user_interaction_file_pattern"]):
            try:
                with open(os.path.join(directory,filename), 'r') as f:
                    for jsonObj in f:
                        interaction = json.loads(jsonObj)
                        userId = interaction.get(config["user_id_key"])
                        item = interaction.get(config["item_id_key"])
                        if (userId, item) not in users:
                            users.append((userId, item))
            except:
                print(filename +": "+sys.exc_info()[0])
        
    return (users, items)

def file_parser(file):
    items = []
    interactions = []
    comps = str(file).split('/')
    if comps[len(comps)-1].startswith("interactions_users"):
        with open(file,"r") as f:
            for jsnObj in f:
                inter = json.loads(jsnObj)
                user = inter['userId']
                item = inter['itemId']
                if (user,item) not in interactions:
                    interactions.append((user,item))

    return (interactions,items)            


