from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR


import pandas as pd
import numpy as np
import re


class data_cleaning:

    def __init__(self,data=None):
        self.df=data

    def title(self):

        location = self.df['title'].str.extract(r',\s*(.+)$')[0].tolist()
        loc_name=[name.replace("\xa0"," ") for name in location]

        self.df['title']=loc_name

    def fillna_df(self):
        list=['Çıxarış','Təmir','İpoteka']
        for col in list:
            self.df.fillna({f'{col}': 'yoxdur'}, inplace=True)

        self.df.dropna()

    def bina_mertebe(self,x):
        menzil, bina = x.split(' / ')
        return pd.Series([int(menzil), int(bina)])
    
    def Sahesi_m2(self,x):
        sahe, m2 = x.split(' ')
        return float(sahe)
    
    def full_data(self,out_csv):

        self.title()
        self.fillna_df()
        self.df[['Menzil_mertebesi', 'Bina_mertebesi']] = self.df['Mərtəbə'].apply(self.bina_mertebe)
        self.df['Sahəsi_m2'] = self.df['Sahə'].apply(self.Sahesi_m2)
        self.df.drop(['Mərtəbə','Sahə',],axis=1,inplace=True)
        self.df['price'] = self.df['price'].astype(str).str.replace(r'[^\d.]', '', regex=True)
        self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce')

        self.df.to_csv(out_csv, index=False, encoding='utf-8-sig')
        return self.df


