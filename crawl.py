#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 21:11:43 2021

@author: mymelo
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup

class Weather:
    def __init__(self):
        response = requests.get('https://pythondojang.bitbucket.io/weather/observation/currentweather.html')
        soup = BeautifulSoup(response.content, 'html.parser')
 
        self.table = soup.find('table', { 'class': 'table_develop3' })    # <table class="table_develop3">을 찾음
        self.data = []
        self.city = "구미"
        self.citytemp = 0
    def run(self):       
                            
        for tr in self.table.find_all('tr'):      
            tds = list(tr.find_all('td'))    
            
            for td in tds:                   
                if td.find('a'):             
                    point = td.find('a').text    
                    if(point == self.city):
                        self.citytemp = tds[5].text    
                        break
        return self.citytemp
        
if __name__ == '__main__':
    a = Weather()
    print(a.run())