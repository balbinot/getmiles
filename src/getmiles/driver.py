# import required modules
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import numpy as np
import os


class Driver():
    def __init__(self):
        # assign url in the webdriver object
        options = webdriver.ChromeOptions()
        serv = webdriver.chrome.service.Service('../../chromedriver-linux64/chromedriver')
        self.driver = webdriver.Chrome(service=serv, chrome_options=options)

    def get_directions(self, destination, name):
        parts = destination.split(';')
        for part in parts:
            legs = part.split('-')
            legs_str = '/'.join(legs)
            self.driver.get(f'https://www.google.com/maps/dir/{legs_str}')
            sleep(3)
            aa = self.driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div[2]/div')
            total_km = aa.text
            print(legs_str, total_km)
            self.driver.save_screenshot(name.replace(' ', '_')+'.png')
        sleep(3)

class Organizer():
    def __init__(self, db):
        self.df = pd.read_excel(db, sheet_name="travel")
        self.alias = pd.read_excel(db, sheet_name="alias")
        self.df = self.df.reset_index()

    def get_destination(self):
        a =  np.array(self.alias['ALIAS'])
        aa = np.array(self.alias['address'])

        _route = []
        for index, row in self.df.iterrows():
            dests = [j.strip() for j in row['Route'].split('-')]
            expanded = [aa[a==j].tolist() for j in dests]
            _route.append(expanded)
        self.df.insert(2, '_route', _route, True)

    def get_files(self, dir):
        for sdate, edate in zip(self.df['Start date'].dt.date, self.df['End date'].dt.date):
            print(sdate, edate)

    def mktree(self, odir='test'):
        for tripname in self.df['Note']:
            os.makedirs(f"{odir}/{tripname}/receipts")

if __name__=='__main__':
    #d = Driver()
    #d.get_directions('groningen - amsterdam', 'test test')

    o = Organizer('../../data/Travel expenses 2022 to 2023.xlsx')
    o.mktree()
    o.get_destination()
    o.get_files(dir='../../data/Document Cloud/')
    #print(o.df['Start date'])
    print(o.df['End date'])




    


