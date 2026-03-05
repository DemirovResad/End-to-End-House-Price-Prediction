import json
import time
import pandas as pd

import requests
from bs4 import BeautifulSoup



class DataExtractor:

    def __init__(self,input_js,out_cvs='all_builds'):
        self.build_urls=input_js
        self.out_cvs='data/' + out_cvs + '.cvs'
        self.headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        
        self.all_builds=pd.DataFrame()




    def start_scr(self,progress_bar=None):

        with open(self.build_urls, 'r', encoding='utf-8') as f:
            build_js = json.load(f)


        for idx,link in enumerate(build_js["Url"]):
            total = len(build_js["Url"])
                
            if progress_bar:
                percent_complete = (idx + 1) / total
                progress_bar.progress(percent_complete, text=f"Baxilan Bina: {idx+1}/{total} ")

            req=self.request_url(link)

            if not req:
                print(f"\n{link} keçildi (7 cəhddən sonra cavab alınmadı).")
                continue
   
            self.get_prop_builds(req,link)
            self.save_cvs()





    def request_url(self,link):
        test_response = 0
        while test_response < 7:
                try:
                    response = requests.get(link, headers=self.headers, timeout=15) # Timeout-u bir az artırdıq
                    if response.status_code == 200:
                        return response

                    else:
                        test_response += 1
                        time.sleep(3)
                except Exception as e:
                    # Əgər Timeout və ya Connection error olsa, proqram dayanmır, yenidən cəhd edir
                    test_response += 1
                    print(f"\nCəhd {test_response}: Bağlantı xətası - {e}")
                    time.sleep(3)
                

        return False    
                



    def get_prop_builds(self,response,link):
  
        temp = dict()

        soup = BeautifulSoup(response.content, 'html.parser')

        temp['Url']=link

        title_tag = soup.find('h1', class_='product-title')
        temp['title'] = title_tag.text.strip()

        properties = soup.find_all('div', class_='product-properties__i')

        for prop in properties:

            name_tag = prop.find('label', class_='product-properties__i-name')
            value_tag = prop.find('span', class_='product-properties__i-value')

            if name_tag and value_tag:

                name = name_tag.text.strip()
                value = value_tag.text.strip()
                temp[name] = value
                
            temp[name]=value
        
        price_tag = soup.find('span', class_='price-val')
        temp['price']=price_tag.text.strip()

        new_df=pd.DataFrame([temp])

        self.all_builds=pd.concat([self.all_builds,new_df], ignore_index=True)

    
    def save_cvs(self):
        self.all_builds.to_csv(self.out_cvs, index=False, encoding='utf-8-sig')









