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
    top = {}
    ml = False
    config = {}
    def __init__(self, rData):
        self.config = parser.readConfig()
        self.ml = self.config['use_movielens']


        if self.ml:
            self.interactions = rData['train']
            self.item_features = rData['item_features']
            self.model = LightFM(loss="warp")
            self.model.fit(self.interactions,epochs=30)
            (self.n_users,self.n_items) = self.interactions.shape
            self.inv_user_mapping = {k: k for k in range(self.n_users)}
            #self.inv_item_mapping = {v: k for k, v in (rData['item_labels'])}
            for i in range(self.n_items):
                self.inv_item_mapping[i] = rData['item_labels'][i]
        else:
            self.data.fit(users=[x[0] for x in rData[0]],items=[x[1] for x in rData[0]])
            item_tag_list = [x[self.config['item_tags']] for x in rData[1]]
            iFeatures = [j for sub in item_tag_list for j in sub]
            user_tag_list = [x[self.config['user_tags']] for x in rData[2]]
            uFeatures = [j for sub in user_tag_list for j in sub]
            if len(iFeatures)>0:
                self.data.fit_partial(items=(x[self.config['item_id_key']] for x in rData[1]),item_features=iFeatures)
            if len(uFeatures)>0:
                self.data.fit_partial(users=(x[self.config['user_id_key']] for x in rData[2]),user_features=uFeatures)
            self.n_users, self.n_items = self.data.interactions_shape()
            (self.interactions, weights) = self.data.build_interactions([(x[0],x[1]) for x in rData[0]])
            self.item_features = self.data.build_item_features((x[self.config['item_id_key']],x[self.config['item_tags']]) for x in rData[1])
            self.user_features = self.data.build_user_features((x[self.config['user_id_key']],x[self.config['user_tags']]) for x in rData[2])
            self.model = LightFM(loss="warp",item_alpha=0.01)
            self.model.fit(self.interactions,epochs=1000,num_threads=4,item_features=self.item_features,user_features=self.user_features)
            self.inv_user_mapping = {v: k for k, v in (self.data.mapping()[0].items())}
            self.inv_item_mapping = {v: k for k, v in (self.data.mapping()[2].items())}
        
        self.top = self.recommend_top()

        
        print("Recommender running")
    
    def recommend(self,user_in, item_in=None):
        user = 0
        item = 0
        try:
            user = int(user_in)
            if user >= self.n_users:
                return self.top
        except:
            try:
                user = self.data._user_id_mapping[user_in]
            except:
                #return "Warning: user id not in the asystem"
                #self.update(([user_in,item_in],[]))
                if(False or item_in != None):
                    self.update(([(user_in,item_in)],[]))
                else:
                    return self.top
        if item_in != None and not self.ml:
            try:
                item = int(item_in)
                if item >= self.n_items:
                    return "Warning: item non in range"
            except:
                try:
                    item = self.data._item_id_mapping[item_in]
                except:
                    return "Warinig: item id not in the system"

            (interactions,weights) = self.data.build_interactions([(self.inv_user_mapping[user],self.inv_item_mapping[item])])
            self.model.fit_partial(interactions,item_features=self.item_features) #da sistemare per efficienza
        
        recommended = {}
        for i in range(self.n_items):
            if i != item:
                prediction = float(self.model.predict(user,np.array([i,]),item_features=self.item_features))
                recommended[self.inv_item_mapping[i]] = prediction
        recommended = dict(sorted(recommended.items(),key=operator.itemgetter(1),reverse=True)[:10])

        return recommended
    
    def validate(self):
        (train, test) = cross_validation.random_train_test_split(self.interactions)
        precision = auc_score(self.model,test,train,item_features= self.item_features)
        return {"mean":float(precision.mean())}
    
    def update(self, data):
        """
        Update the engine with new users or videos

        Parameters
        --------------------------------
        data = tuple of the form (iterable of interactions, iterable of videos)
        """
        if len(data[0])>0:
            self.data.fit_partial(users=[x[0] for x in data[0]],items=[x[1] for x in data[0]])
        if len(data[1])>0:
            self.data.fit_partial(items=[x[self.config['item_id_key']] for x in data[1]])
        
        self.inv_user_mapping = {v: k for k, v in self.data.mapping()[0].items()}
        self.inv_item_mapping = {v: k for k, v in self.data.mapping()[2].items()}
        (interactions,weights) = self.data.build_interactions(data[0])
        self.model.fit_partial(interactions)
    
    def recommend_top(self):
        (users,items) = self.interactions.shape
        arrMat = self.interactions.toarray()
        #print(arrMat)
        topV = {v:(0,0) for v in self.inv_item_mapping.values()}
        iMap = {v: k for k, v in self.inv_item_mapping.items()}
        #print(iMap)
        for u in range(users):
            row = arrMat[u]
            for i in range(items):
                if row[i] != 0:
                    topV[self.inv_item_mapping[i]] = (topV[self.inv_item_mapping[i]][0]+row[i],topV[self.inv_item_mapping[i]][1]+1)

        #top = {k:v[0]/v[1] if v[1] !=0 else v[0] for k, v in topV.items()}
        top = {k:v[0]/items for k, v in topV.items()}
        #top.sort(reverse=True)
        top = dict(sorted(top.items(),key=operator.itemgetter(1),reverse=True)[:10])
        return top
