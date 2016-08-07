import numpy as np
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import pickle
import sys

class Scrape_Giro():
    
    def __init__(self, stage_nums):
        self.stage_nums = stage_nums
        self.stage_names = []
        
        stage_num_range = np.linspace(1,self.stage_nums,self.stage_nums).astype(int)        
            
        for stage in stage_num_range:
            url = self.create_url(stage)
            root = self.scrape_xml(url)
            stage_name, riders, stage_times = self.collect_data(root)
            
            if stage == 1:
                self.total_riders, self.df = self.create_df(root, riders, stage_times)
            else:
                self.df = self.concat_data(self.df, riders, stage_times, stage)
            self.stage_names.append(stage_name)
            
        self.df = self.df.fillna(0)


    def create_url(self, stage_num):
        stage_num = str(stage_num).zfill(2)        
        url = 'http://xml2.temporeale.gazzettaobjects.it/Giroditalia/2016/classifiche/xml/arrivo/cls_tp_arrivo_'+stage_num+'.xml'
        return url

    def scrape_xml(self, url):
        xml = requests.get(url).text
        root = ET.fromstring(xml)
        
        return root
    
    def collect_data(self, root):
        stage_name = root.find('localita').text
        
        riders = []
        for name in root.iter('nome'):
            rider = name.text
            riders.append(rider)
        
        stage_times = []
        for temp in root.iter('tempo'):
            time = temp.text
            stage_times.append(time)
            
        return stage_name, riders, stage_times
        
        
    def create_df(self, root, riders, stage_times):
        col_title = 's1'
        index = np.arange(len(riders))
        
        teams = []
        for squadra in root.iter('squadra'):
            squad = squadra.text
            teams.append(squad)
        
        df = pd.DataFrame({'Riders' : riders,'Team' : teams ,col_title : stage_times}, index=index)
        
        total_riders = df.shape[0]        
        
        return total_riders, df
        
    def concat_data(self, df, riders, stage_times, stage):
        col_title = 's' + str(stage)
        index = np.arange(len(riders))
        
        temp_df = pd.DataFrame({'Riders' : riders, col_title : stage_times}, index=index)       
                
        df = df.merge(right = temp_df, on = 'Riders', how = 'outer')
        
        return df
        
 # Create Data Expansion Functions

def ugly_second_converter(x):
    time = str(x).split(':')
    time = [int(x) for x in time]    
    
    if len(time) == 3:
        time = time[0]*3600 + time[1]*60 + time[2]
    elif len(time) == 2:
        time = time[0]*60 + time[1]
    else:
        return time[0]
    return time

def cum_time_col(df, cols):
    
    for i, col in enumerate(cols):
        new_col = 't' + col.strip('s')
        cols_to_sum = cols[:i+1]
        df[new_col] = df[cols_to_sum].sum(axis=1)
    
    return df
    
def tour_rank(df):
    cols = [col for col in df.columns if col[0] == 't']
    
    for col in cols:
        new_col = 'r' + col.strip('t')
        col2 = col.replace('t','s')
        df[new_col] = df.loc[:,col][df[col2] != 0].rank(method='min').astype(int)
        
    return df


giro = Scrape_Giro(21)

df = giro.df

# Check no duplications of riders has occured

if giro.total_riders != df.shape[0]:
    # Duplication of riders due to differences in XML files
    # Amend using Excel - Quicker
    df.to_csv('Giro-stage-check.csv', sep=',', index=False)
    sys.exit("Check and amend duplications in Excel")


# Extend data to include cumulative time and tour rank at the end of each stage
else:
    cols = [col for col in df.columns if col[0] == 's']

    # Error made by XML file creators, stage 9  and 15 have been coded incorrectly
    # Below line has been inserted to correct this    
    df['s9'] = df['s9'].apply(lambda x: x if x.startswith('0') else x[:-3])
    df['s15'] = df['s15'].apply(lambda x: x if x.startswith('0') else x[:-3])
    df[cols] = df[cols].applymap(ugly_second_converter)

    df = cum_time_col(df, cols)
    df = tour_rank(df)

    # Write data to csv and save stage names

    df.to_csv('Giro-2016.csv', sep=',', index=False)

    pickle.dump( giro.stage_names, open("stage_names_G2016.pkl", "wb" ))

sys.exit("Process Complete")


""" 

If duplicates were found, copy the below code and run in a new script 

import pandas as pd
import pickle
from scrapeGiro.py import ugly_second_converter, cum_time_col, tour_rank

df = pd.read_csv('Giro-stage-check.csv')

cols = [col for col in df.columns if col[0] == 's']
df[cols] = df[cols].applymap(ugly_second_converter)

df = cum_time_col(df, cols)
df = tour_rank(df)

# Write data to csv and save stage names

df.to_csv('Giro-20167.csv', sep=';', index=False)

pickle.dump( giro.stage_names, open("stage_names_G20167.pkl", "wb" ))

"""
