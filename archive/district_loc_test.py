# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 16:11:49 2019
Location Matching for district names, MP
@author: Aneesh
"""

import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz


df = pd.read_excel('district_location_test.xlsx')

districts = pd.read_csv('mp_districts_2017-2018.csv')

districts = districts[districts['state_code'] == 17]
dlist = list(districts['district_name'].unique())
dlist.sort()
dlist = [x.upper() for x in dlist]

df['district_name'] = df['mp_dpo_district'].fillna('').apply(lambda x: ('' if (str(x) == '') else str(x)))
df['district_name'] = df['mp_dpo_district'].fillna('').apply(lambda x: str(x).split(',')[1] if (',' in str(x)) else str(x))

ourd = list(df['district_name'].unique())

ddict = {}
ourd.sort()

for i in ourd:
    temp = (i,) + process.extractOne(i, dlist)
    ddict[i] = temp[1]
    if i == '':
        ddict[i] = ''
    df.loc[(df['district_name'] == i), 'matched_district'] = ddict[i]
    #df.loc[(df['district_name'] == i), 'district_confidence'] = (temp[2]%100)

df.loc[df['matched_district'].apply(lambda x: str(x).strip()) == df['mp_dpo_district'].apply(lambda x: str(x).strip()), 'exact_match_location'] = 1
df = df.drop(columns = 'district_name')

df.to_excel('district_location_test_filled.xlsx', index = False)
