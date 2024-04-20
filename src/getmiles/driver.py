# import required modules
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from PyPDF2 import PdfReader
import datetime
import pandas as pd
import numpy as np
import os
import shutil
import glob

class Driver():
    def __init__(self):
        # assign url in the webdriver object
        options = webdriver.ChromeOptions()
        options.binary_location = "../../chrome-linux64/chrome"
        serv = webdriver.chrome.service.Service('../../chromedriver-linux64/chromedriver')
        self.driver = webdriver.Chrome(service=serv, chrome_options=options, executable_path='../../chrome-linux64/chrome')

    def get_directions(self, destination, name):
        parts = destination.split(';')
        TOTALKM = 0
        for np, part in enumerate(parts):
            legs = part.split('-')
            legs_str = '/'.join(legs)
            self.driver.get(f'https://www.google.com/maps/dir/{legs_str}')
            sleep(3)
            aa = self.driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div[2]/div')
            total_km = aa.text.replace(',','.')
            print(total_km.split())
            #print(legs_str, total_km)
            #print(name.split('/')[-2], total_km)
            kmunit = total_km.split()[-1].strip()
            if kmunit=='km':
                TOTALKM += float(total_km.split('km')[0])
            else:
                TOTALKM += float(total_km.split()[0])*1.61
            self.driver.save_screenshot(name+f'screenshot_leg{np}.png')
        print(name, TOTALKM)
        sleep(3)

class Organizer():
    def __init__(self, db):
        self.df = pd.read_excel(db, sheet_name="travel")
        self.alias = pd.read_excel(db, sheet_name="alias")
        self.df = self.df.reset_index()

        self.df['Start date'] = pd.to_datetime(self.df['Start date'])
        self.df['End date'] = pd.to_datetime(self.df['End date'])

    def get_destination(self):
        a =  np.array(self.alias['ALIAS'])
        aa = np.array(self.alias['address'])
        _route = []
        for index, row in self.df.iterrows():
            print(row['Route'])
            if pd.notnull(row['Route']):
                dests = [j.strip() for j in row['Route'].split('-')]
                expanded = []
                for dest in dests:
                    if dest in a:
                        expanded.append(aa[a==dest].tolist()[0])
                    else:
                        expanded.append(dest)
                _route.append(expanded)
            else:
                _route.append(pd.NA)
        self.df.insert(2, '_route', _route, True)

    def get_files(self, dir):
        flist = glob.glob(dir+'/*.pdf')
        cdate = []
        for f in flist:
            pdf = PdfReader(f)
            meta = pdf.metadata
            try:
                _d = datetime.date(year=int(meta.creation_date_raw[2:6]),
                                   month=int(meta.creation_date_raw[6:8]),
                                   day=int(meta.creation_date_raw[8:10]),)
                cdate.append(_d)
            except:
                dd = f.split('/')[-1][0:8]
                _d = datetime.date(year=int(dd[0:4]),
                                   month=int(dd[4:6]),
                                   day=int(dd[6:8]),)
                cdate.append(_d)

        d = {
               'fname': np.array(flist),
                'date': np.array(cdate),
               }

        self.fdf = pd.DataFrame(d)
        self.fdf['date'] = pd.to_datetime(self.fdf['date'])  
        for sdate, edate, dir in zip(self.df['Start date'], self.df['End date'], self.df['DIR']):
            mask = (self.fdf['date'] >= sdate) & (self.fdf['date'] <= edate)
            print(sdate, edate, len(self.fdf.loc[mask]), dir)
            for f in self.fdf.loc[mask]['fname']:
                print(f)
                shutil.copyfile(f, f"{dir}/receipts/{f.split('/')[-1]}")


    def mktree(self, odir='test'):
        self.DIRS = []
        for tripname in self.df['Note']:
            if pd.notnull(tripname):
                print(tripname)
                self.DIRS.append(f"{odir}/{tripname}/")
                os.makedirs(f"{odir}/{tripname}/receipts")
            else:
                self.DIRS.append(pd.NA)
        self.df.insert(5, 'DIR', self.DIRS, True)

if __name__=='__main__':
    d = Driver()
    #d.get_directions('groningen - amsterdam', 'test test')

    o = Organizer('~/Travel expenses 2022 to 2023 to 2024.xlsx')
    o.mktree()
    o.get_destination()
    #o.get_files(dir='../../data/Document Cloud/')

    for route, dir in zip(o.df['_route'], o.df['DIR']):
        #print(route, dir)
        d.get_directions(' - '.join(route), dir)
    #print(o.df['Start date'])
    #print(o.df['End date'])




    


