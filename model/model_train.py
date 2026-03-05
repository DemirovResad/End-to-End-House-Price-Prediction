import pandas as pd
import numpy as np

from sklearn.metrics import r2_score,root_mean_squared_error,roc_auc_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import cross_validate, train_test_split



class train_predict:

    def __init__(self,data=None,target=None,model=None):
        self.model=model
        
        self.df=data
        self.X=data.drop(target,axis=1)
        self.y=data[target]

    def num_cat_col(self): # Columnlari ayirir

        num_col=self.X.select_dtypes(include=[np.number]).columns
        cat_col=self.X.select_dtypes(exclude=[np.number]).columns

        return num_col, cat_col
    
    def scal(self,num_col): # Scaler edir

        scaler=StandardScaler()

        for col in num_col:

            new_x=scaler.fit_transform(self.X[[col]])
            self.X[col]=new_x

    def enco(self,cat_col): # Encoder edir

        LabEn=LabelEncoder()

        for col in cat_col:

            new_x=LabEn.fit_transform(self.X[[col]])
            self.X[col]=new_x



    def data_pre(self,test_size=0.25,shuffle=True,random_state=None,stratify=None): # Data_preprosesing edir
        
        num_col, cat_col=self.num_cat_col()
        self.scal(num_col)
        self.enco(cat_col)  
        
        self.X_train, self.X_test, self.y_train, self.y_test=train_test_split(self.X, self.y,test_size=test_size,shuffle=shuffle,random_state=random_state,stratify=stratify)

        return self
    

    def train(self):
        
        self.data_pre()

        self.model.fit(self.X_train,self.y_train)


        if self.model is not None:
            self.model.fit(self.X_train, self.y_train)
        else:
            raise ValueError("Model təyin olunmayıb! __init__ zamanı model göndərin.")
        
        return self

    def predict_model(self,input_data=None,you_model=None):

        if you_model:
            self.model=you_model

        if self.model is None:
            raise ValueError("Model hələ yaradılmayıb!")

        if input_data is None:
            self.predictions = self.model.predict(self.X_test)
            return self.predictions

        else:
            predictions = self.model.predict(input_data)
            return predictions

        
    
    def metrics_score(self,mode):
        metrics_dict={
                        'R2 Score': r2_score(self.y_test,self.predictions),
                        'Root Mean Squared Error': root_mean_squared_error(self.y_test,self.predictions),
                        'Mean Absolute Error': mean_absolute_error(self.y_test,self.predictions),
                        'Mean Squared Error': mean_squared_error(self.y_test,self.predictions),
                        }

        metrics=dict()
        
        for i in mode:

            metrics[i]=metrics_dict[i]

        return metrics
        


        

