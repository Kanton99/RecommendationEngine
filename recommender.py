from lightfm import LightFM
from lightfm.evaluation import precision_at_k, auc_score
from lightfm.data import Dataset
from lightfm import cross_validation
from lightfm.datasets import fetch_movielens
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
    fileData = 0
    def __init__(self, fileData: parser.FileData):
        self.fileData = fileData
        self.ml = fileData.movieLens


        if self.ml:
            mlData = fetch_movielens()
            self.interactions = mlData['train']
            self.item_features = mlData['item_features']
            self.model = LightFM(loss="warp")
            self.model.fit(self.interactions,epochs=30)
            (self.n_users,self.n_items) = self.interactions.shape
            self.inv_user_mapping = {k: k for k in range(self.n_users)}
            #self.inv_item_mapping = {v: k for k, v in (rData['item_labels'])}
            for i in range(self.n_items):
                self.inv_item_mapping[i] = mlData['item_labels'][i]
        else:
            #region build dataset
            self.data.fit(users=self.fileData.users,items=self.fileData.items)

            
            self.n_users, self.n_items = self.data.interactions_shape()
            #endregion
            
            (self.interactions, weights) = self.data.build_interactions(self.fileData.interactions)
            
            #region build model
            self.model = LightFM(loss="warp",item_alpha=0.01)
            self.model.fit(self.interactions,epochs=1000,num_threads=4)
            #endregion
            self.inv_user_mapping = {v: k for k, v in (self.data.mapping()[0].items())}
            self.inv_item_mapping = {v: k for k, v in (self.data.mapping()[2].items())}
        
        #self.top = self.recommend_top()

        
        print("Recommender running")
    
    def recommend(self,user: int, item:int=None):
        # user = int(user)
        if(item!=None):
            self.update([(user,item)])
        if(user>self.n_users):
            return self.recommend_top()

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
    
    def update(self, interactions, items=[]):
        """
        Update the engine with new users or items

        Parameters
        --------------------------------
        data = tuple of the form (iterable of interactions, iterable of items)
        """
        if len(interactions)>0:
            self.data.fit_partial(users=[x[0] for x in interactions],items=[x[1] for x in interactions])
            self.data.fit_partial()
        if len(items)>0:
            self.data.fit_partial(items=[x[self.fileData.itemIdKey] for x in items])
        
        self.inv_user_mapping = {v: k for k, v in self.data.mapping()[0].items()}
        self.inv_item_mapping = {v: k for k, v in self.data.mapping()[2].items()}
        (self.interactions,weights) = self.data.build_interactions(interactions)

        self.model.fit(self.interactions,epochs=1000,num_threads=4)
    
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
