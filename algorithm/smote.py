#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import imp
import random
import pandas
import numpy as np
from sklearn.neighbors import NearestNeighbors
#imp.reload(sys)
#sys.setdefaultencoding('utf-8')

class Smote:
    def __init__(self,samples,N=10,k=5):
        self.n_samples, self.n_attrs=samples.shape
        self.N=N
        self.k=k
        self.samples=samples

    def over_sampling(self):
        keep_list=[]
        if self.N<100:
            old_n_samples=self.n_samples
            #print("old_n_samples:", old_n_samples)
            self.n_samples=int(float(self.N)/100*old_n_samples)
            #print("n_samples:", self.n_samples)
            keep=np.random.permutation(old_n_samples)[:self.n_samples]
            #print("keep:", keep)
            #change the delimiter from space to comma,why keep's elements are delimited by comma, fixme
            for item in keep:
                keep_list.append(item)
            #print("keep:", keep_list)
            new_samples=self.samples.iloc[keep_list]
            self.samples=new_samples
            self.N=100

        N=int(self.N/100) #the number of new synthetic minority class samples
        self.synthetic=np.zeros((self.n_samples*N, self.n_attrs))
        self.new_index=0

        neighbors=NearestNeighbors(n_neighbors=self.k).fit(self.samples)
        #print("neighbors:", neighbors)
        arr_samples=np.array(self.samples)
        for i in range(len(self.samples)):
            nnarray=neighbors.kneighbors(arr_samples,return_distance=False)[0]
            #store the k-nearest neighbors's index
            self.__populate(N, i, nnarray )

        return self.synthetic

    #extract n times randomly from the k-nearest neighbors, generating n synthetic samples
    def __populate(self, N, i, nnarray):
        for i in range(N):
            nn = np.random.randint(0, self.k)
            print(nnarray[nn])
            dif=self.samples.iloc[nnarray[nn]]-self.samples.iloc[i]    #including the class label
            gap=np.random.rand(1,self.n_attrs)
            self.synthetic[self.new_index]=self.samples.iloc[i]+gap.flatten()*dif
            self.new_index+=1

if __name__ == "__main__":
    #file_fullpath='/home/login01/Workspaces/python/dataset/module_data_stg1/sample'
    file_fullpath='/home/login01/Workspaces/python/dataset/cs.csv'
    cs=pandas.read_csv(file_fullpath,sep=',',index_col=0,na_values='NA',low_memory=False)
    cs_mean_MonthlyIncome = cs.MonthlyIncome.mean(skipna=True)                                          
    cs_mean_NumberOfDependents = cs.NumberOfDependents.mean(skipna=True)
    cs.ix[:, 'MonthlyIncome'] = cs.MonthlyIncome.fillna(cs_mean_MonthlyIncome, inplace=False)
    cs.ix[:, 'NumberOfDependents'] = cs.NumberOfDependents.fillna(cs_mean_NumberOfDependents, inplace=False)
    ismote=Smote(cs,20,6)
    print(ismote.n_samples)
    print(ismote.n_attrs)
    mysample=ismote.over_sampling()
    print(mysample)
