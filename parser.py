import json
import os
import sys

class FileData:
    #region configs 
    movieLens = False
    dataDirectory = ""

    itemData = ""
    userData = ""
    interactionData = ""

    userIdKey = ""
    itemIdKey = ""

    itemTags = ""
    userTags = ""
    #endregion
    
    #region interaction data
    items = []
    users = []
    interactions = []
    #endregion

    def __new__(cls, *ars, **kwargs):
        return super().__new__(cls)

    def __init__(self):
        self.readConfig()
        self.parser()
        pass

    def readConfig(self):
        config = ""
        with open("config.json","r") as c:
            config = json.load(c)
            #return config
        
        self.movieLens = config["use_movielens"]
        self.dataDirectory = config["data_directory_location"]

        self.itemData = config["item_data_file_pattern"]
        self.userData = config["user_data_file_pattern"]
        self.interactionData = config["user_interaction_file_pattern"]

        self.userIdKey = config["user_id_key"]
        self.itemIdKey = config["item_id_key"]

        self.itemTags = config["item_tags"]
        self.userTags = config["user_tags"]

    def parser(self):
        for file in os.listdir(self.dataDirectory):
            filename = os.fsdecode(file)
            if filename == (self.itemData):
                try:
                    with open(os.path.join(self.dataDirectory,filename), 'r') as f:
                        for jsonObj in f:
                            item = json.loads(jsonObj)
                            if item not in self.items:
                                self.items.append(item)
                                item['tags'] = item[self.itemTags]
                except:
                    print(filename +": "+sys.exc_info()[0])
            if filename == (self.interactionData):
                try:
                    with open(os.path.join(self.dataDirectory,filename), 'r') as f:
                        for jsonObj in f:
                            interaction = json.loads(jsonObj)
                            userId = interaction.get(self.userIdKey)
                            item = interaction.get(self.itemIdKey)
                            if userId not in self.users:
                                self.users.append(userId)
                            if item not in self.items:
                                self.items.append(item)
                            if (userId, item) not in self.interactions:
                                self.interactions.append((userId, item))
                except:
                    print(filename +": "+sys.exc_info()[0])
            if len(self.userData)>0 and filename.startswith(self.interactionData):
                try:
                    with open(os.path.join(self.dataDirectory,filename), 'r') as f:
                        for jsonObj in f:
                            user = json.loads(jsonObj)
                            userId = interaction.get(self.userIdKey)
                            uTags = interaction.get(self.userTags)
                            if (userId, item) not in self.interactions:
                                self.users.append((userId, item))
                except:
                    print(filename +": "+sys.exc_info()[0])

    def getRecommData(self):
        return (self.interactions, self.items, self.users)

    def file_parser(self,file):
        comps = str(file).split('/')
        if comps[len(comps)-1].startswith(self.interactionData):
            with open(file,"r") as f:
                for jsnObj in f:
                    inter = json.loads(jsnObj)
                    user = inter[self.userIdKey]
                    item = inter[self.itemIdKey]
                    if (user,item) not in self.interactions:
                        self.interactions.append((user,item))

        return (self.interactions,self.items)            

    def writeInteraction(self,user,item):
    
        # with open(os.path.join(self.dataDirectory,self.interactionData),"r") as file:
        #     data = json.load(file)
        # data.append({self.file:user,self.itemIdKey:item})
        
        # with open(os.path.join(self.dataDirectory,self.interactionData),"a") as file:
        #     json.dump(data,file)
        with open(os.path.join(self.dataDirectory,self.interactionData),"a") as file:
            data = {self.userIdKey:user,self.itemIdKey:item}
            json_obj = json.dumps(data,indent=4)
            file.write(json_obj)
