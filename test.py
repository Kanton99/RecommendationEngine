from lightfm import LightFM
from lightfm.evaluation import precision_at_k
from lightfm.data import Dataset
from lightfm import cross_validation
import numpy as np
import scipy
import operator
import parser


class Recommender:
    users = []
    assets = []
    iters = []
    item_features = []
    n_users=0
    n_items=0
    interactions: scipy.sparse.coo_matrix
    data = Dataset()
    def __init__(self, rData):
        self.data.fit([x[0] for x in rData[0]],[x['assetId']for x in rData[1]],user_features=None,item_features=['type','description','topics','skills'])
        
        self.n_users, self.n_items = self.data.interactions_shape()
        for user in rData[0]:
            if user[0] not in self.users:
                self.users.append(user[0])
        self.iters = rData[0]
        try:
            self.assets = [(x['assetId'],x['title'])for x in rData[1]]
        except Exception as e:
            pass
        (self.interactions, weights) = self.data.build_interactions(rData[0])
        #print(interactions)
        #print(repr(weights)+"\n")
        self.item_features = self.data.build_item_features((x['assetId'],['type','description','topics','skills'])for x in rData[1])
        self.model = LightFM(loss="bpr")
        self.model.fit(self.interactions,sample_weight=weights,item_features=self.item_features,epochs=50,num_threads=4)

    def recommend(self,user, asset):
        asset = int(asset)
        recommended = {}
        try:
            #recommended = self.model.predict(user,asset,item_features=self.item_features)
            for i in range(self.n_items):
                if i != asset:
                    prediction = float(self.model.predict(user,np.array([i,])))
                    if prediction > 0:
                        recommended["{} {}".format(i,self.assets[i][1])] = prediction
        except Exception as e:
            print(e)
            pass
        new_inter = (self.users[user],self.assets[asset][0])
        if new_inter not in self.iters:
            self.iters.append(new_inter)
            (interactions,weights) = self.data.build_interactions([new_inter])
            self.model.fit_partial(interactions,item_features=self.item_features)
        recommended = dict(sorted(recommended.items(),key=operator.itemgetter(1),reverse=True))
        return recommended
    def validate(self):
        (train, test) = cross_validation.random_train_test_split(self.interactions)
        precision = precision_at_k(self.model,test,train,item_features=self.item_features,k=3)
        for i in precision:
            print("{}\n".format(i))

data = parser.parser()
recommender = Recommender(data)
print(recommender.recommend(0,0))