# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 22:08:11 2016

@author: Nick
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn

seaborn.set_style('white')

def finishers_only(data):
    data.dropna(inplace=True)
    data.reset_index(inplace=True)

def collect_median_times(data, col_start_char):
    column_name_list = [col for col in data.columns if col.startswith(col_start_char)]
    median_times = [data[series].median() for series in data[column_name_list]]
    return column_name_list, median_times

def create_median_df(data, column_names, median_times):
    for index in range(data.shape[0]):
        for i, col in enumerate(column_names):    
            data.loc[index, col] = data.loc[index,col] - median_times[i]
    return data

def plotgraph(data, cols, num, stage_list, rider = False, team = False):
    
    colors = ['indigo', 'green', 'dodgerblue', 'aqua', 'cadetblue', 'lightskyblue','lightgreen',\
          'magenta','cornflowerblue', 'darkturquoise']
    
    fig = plt.figure(figsize=(16,7))
    ax = plt.axes()
    x = np.linspace(1, num, num)
    
    for i in range(data.shape[0]):
        y = np.asarray(data[cols].loc[i,:])
        ax.plot(x,y,c='coral',alpha=0.2)
    
    if rider:    
        y = np.asarray(data[data.Riders == rider][cols])[0]
        ax.plot(x,y,c='royalblue',alpha=0.9,linewidth=4,label=rider)
        
        name = rider.split(' ')
        
        ax.set_title('Rider: ' + name[1] + ' ' + name[0].title(), fontweight='bold')
    
    if team:
        index_vals = data[data.Team == team][cols].index
        for i,j in enumerate(index_vals):
            y = np.asarray(data[cols].loc[j,:])
            ax.plot(x,y,c=colors[i],alpha=1,label=data.loc[j,'Riders'],linewidth=3)
            ax.legend(loc='best',frameon=False)
            ax.set_title('Team: ' + team, fontweight='bold')
    
    if cols[0][0].startswith('s'):
        ax.set_ylabel('Seconds',fontweight='bold')
        plt.suptitle('Rider Stage Time Minus Median Stage Time', fontsize=16, fontweight='bold')
    elif cols[0][0].startswith('r'):
        ax.set_ylabel('Tour Rank', fontweight='bold')
        plt.suptitle('Rider\'s Overall Rank Per Stage', fontsize=16, fontweight='bold')
    else:
        ax.set_ylim([-13000,7500])
        ax.set_ylabel('Seconds',fontweight='bold')
        plt.suptitle('Rider Cumulative Time Minus Median Cumulative Time', fontsize=16, fontweight='bold')

    ax.set_xlabel('Stages',fontweight='bold')
    ax.set_xlim([1,21])
    ax.set_xticks(x)
    ax.set_xticklabels(np.asarray(stage_list),ha='right',rotation=45)

    plt.show()


