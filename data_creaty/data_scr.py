import time
import json
import pandas as pd


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class Building_url:
    def __init__(self,output_file='new_build_links',mode='menziller'):
        self.edge_options = Options()
        self.edge_options.add_argument("--start-maximized")
        self.edge_options.add_argument("--headless")
        
        # SSL xətalarını gizlətmək və keçmək üçün əlavələr:
        self.edge_options.add_argument('--ignore-certificate-errors')
        self.edge_options.add_argument('--ignore-ssl-errors')
        self.edge_options.add_argument('--log-level=3') # Terminalda artıq xətaları göstərmir

        
        self.driver = webdriver.Edge(options=self.edge_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.mode=mode
        self.all_links = []
        self.output_file = 'data/'+ output_file +'.json'



    def scroll_bottom(self): #scroll ile asagi dusur

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        while True:

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
 
            time.sleep(2)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    break

                self.driver.execute_script("window.scrollBy(0, -300);")
                time.sleep(1)

            else:
                last_height = new_height
                scroll_attempts = 0 



    def select_location_and_scrape(self, loc_name): # Mekanlar arasinda gererek binalari axtarir

        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            list_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='chosen-locations-names-title']")))
            self.driver.execute_script("arguments[0].click();", list_div)
            

            input_field = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='search']")))
            input_field.send_keys(Keys.CONTROL + "a")
            input_field.send_keys(Keys.BACKSPACE)
            input_field.send_keys(loc_name[0:-4])

            time.sleep(1.5)
            
            loc_click = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='search-checkbox-container']")))
            self.driver.execute_script("arguments[0].click();", loc_click)
            
            # loc deyerini testiq edir
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-cy='new-search-popup--locations--submit-button']")
            self.driver.execute_script("arguments[0].click();", submit_btn)
            
            time.sleep(2)
            self.scroll_bottom()
            self.collect_links()
            
        except Exception as e:
            print(f"Tapa bilmedi ({loc_name}): {e}")



    def save_to_json(self): #melumatlari save et

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump({"Url": self.all_links}, f, ensure_ascii=False, indent=4)


    def collect_links(self): # Seyifedeki butun linkleri goturur

        card_link_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[data-cy='card-link']")
        links = [link.get_attribute("href") for link in card_link_elements if link.get_attribute("href")]
        

        for link in links:
            if link not in self.all_links:
                self.all_links.append(link)

        self.save_to_json()
    


    def start(self, start_room=1, end_room=5,progress_bar=None): # Selenuim ile melumatlar toplanir

        for idx,i in enumerate(range(start_room, end_room + 1)):

            total = end_room - start_room + 1
            if progress_bar:
                percent_complete = (idx+1) / total
                progress_bar.progress(percent_complete, text=f"Baxilan link : {idx+1}/{total}")


            url = f'https://bina.az/baki/alqi-satqi/{self.mode}/{i}-otaqli'
            self.driver.get(url)
            
            # Loc sayyisi elde edir
            list_div = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-cy='chosen-locations-names-title']")))
            list_div.click()
            
            location_names = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-cy='new-search-checkbox-list--dropdown__main']")))
            location_text = [loc.text for loc in location_names]
            
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

            for idx,loc in enumerate(location_text):

                total = len(location_text)
                
                if progress_bar:
                    percent_complete = (idx + 1) / total
                    progress_bar.progress(percent_complete, text=f"Axtarilir erazi: {loc} ")



                self.select_location_and_scrape(loc)
                # Seyfeye geri qayidir reload edir
                self.driver.get(url)

        self.driver.quit()






