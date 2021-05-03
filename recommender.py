from lightfm import LightFM
from lightfm.evaluation import precision_at_k, auc_score
from lightfm.data import Dataset
from lightfm import cross_validation
import numpy as np
import scipy
import operator
import parser
import random


class Recommender:
    item_features = []
    n_users=0
    n_items=0
    interactions: scipy.sparse.coo_matrix
    inv_user_mapping = {}
    inv_item_mapping = {}
    data = Dataset()

    def print_interactions(self,user=None,asset=None):
        cx = self.interactions.tolil()
        if user != None and asset != None:
            cx[user,asset] = 1
        with open("interaction matrix.txt","w") as f:
            shape = cx.get_shape()
            for i in range(shape[0]):
                for j in range(shape[1]):
                    f.write(" ".join(str(cx[i,j])))
                f.write('\n')

    def __init__(self, rData):
        self.data.fit(users=[x[0] for x in rData[0]],items=[x[1] for x in rData[0]])
        tags_list = [x['tags'] for x in rData[1]]
        features = [j for sub in tags_list for j in sub]
        self.data.fit_partial(items=(x['assetId'] for x in rData[1]),item_features=features)
        self.n_users, self.n_items = self.data.interactions_shape()
        (self.interactions, weights) = self.data.build_interactions([(x[0],x[1]) for x in rData[0]])
        self.print_interactions()
        self.item_features = self.data.build_item_features((x['assetId'],x['tags']) for x in rData[1])
        self.model = LightFM(loss="warp",item_alpha=0.01)
        self.model.fit(self.interactions,epochs=50,num_threads=4,item_features=self.item_features)

        self.inv_user_mapping = {v: k for k, v in self.data._user_id_mapping.items()}
        self.inv_item_mapping = {v: k for k, v in self.data._item_id_mapping.items()}
        print("Recommender running")
    def recommend(self,user_in, asset_in=None):
        user = 0
        asset = 0
        try:
            user = int(user_in)
            if user >= self.n_users:
                return "Warning: user non in range"
        except:
            try:
                user = self.data._user_id_mapping[user_in]
                return self.recommend_random()
            except:
                #return "Warning: user id not in the asystem"
                self.new_user(user_in)
        if asset_in != None:
            try:
                asset = int(asset_in)
                if asset >= self.n_items:
                    return "Warning: item non in range"
            except:
                try:
                    asset = self.data._item_id_mapping[asset_in]
                except:
                    return "Warinig: item id not in the system"
        
        recommended = {}
        rItems = 0
        for i in range(self.n_items):
            if i != asset:
                prediction = float(self.model.predict(user,np.array([i,]),item_features=self.item_features))
                if rItems < 10:
                    recommended[self.inv_item_mapping[i]] = prediction
                    rItems+=1
        recommended = dict(sorted(recommended.items(),key=operator.itemgetter(1),reverse=True))
        if asset_in != None:
            (interactions,weights) = self.data.build_interactions([(self.inv_user_mapping[user],self.inv_item_mapping[asset]),])
            self.model.fit_partial(interactions,item_features=self.item_features)
            self.print_interactions(user=user,asset=asset)
        return recommended
    def validate(self):
        (train, test) = cross_validation.random_train_test_split(self.interactions)
        precision = auc_score(self.model,test,train,item_features= self.item_features)
        for i in precision:
            print("{}\n".format(i))
    def update(self, data):
        """
        Update the engine with new users or videos

        Parameters
        --------------------------------
        users = iterable if user ids
        videos = iterable of video ids
        """
        if len(data[0])>0:
            self.data.fit_partial(users=[x[0] for x in data[0]],items=[x[1] for x in data[0]])
        if len(data[1])>0:
            self.data.fit_partial(items=[x['assetId'] for x in data[1]])
        (interactions,weights) = self.data.build_interactions(data[0])
        self.model.fit_partial(interactions)
    def new_user(self,user):
        self.data.fit_partial(users=[user])
        self.inv_user_mapping = {v: k for k, v in self.data._user_id_mapping.items()}
        self.inv_item_mapping = {v: k for k, v in self.data._item_id_mapping.items()}
        #print(len(self.model.user_embeddings))
    def recommend_random(self):
        rList = random.sample(range(self.n_items),10)
        recom = {}
        for i in rList:
            recom[self.inv_item_mapping[i]] = 0
        return recom
#r = Recommender(parser.parser())