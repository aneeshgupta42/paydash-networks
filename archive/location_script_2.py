# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 11:40:35 2019

@author: Aneesh
"""
def splice1(x):
    if ',' in x:
        return x.split(',')[0]
    if "(" in x:
        return x.split("(")[0]
    if '-' in x:
        return x.split('-')[0]
    else: return x

def splice2(x):
    if ',' in x:
        return x.split(',')[1]
    if "(" in x:
        return x.split("(")[1]
    if '-' in x:
        return x.split('-')[1]
    else: return ''


#from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import pandas as pd

k = ')'
base = pd.read_excel(r'docs\network_mp_apo_responses_from_baseline.xlsx')
districts = pd.read_csv(r'docs\mp_districts_2017-2018.csv')
districts = districts[districts['state_code'] == 17]
dlist = list(districts['district_name'].unique())
dlist.sort()
dlist = [x.upper() for x in dlist]
blocks = pd.read_csv(r'docs\mp_blocks_2017-2018.csv')
blocks = blocks[blocks['state_code'] == 17]
blist = list(blocks['block_name'].unique())
blist.sort()
blist = [b.upper() for b in blist]

base['separator_present'] = base['mp_apo_block'].fillna('').apply(lambda x: int((k in x) | (',' in x) | ('-' in x)))
base['block_name'] = ''
base['district_name'] = ''


base.loc[base['separator_present'] == 1, 'block_name'] = base['mp_apo_block'].fillna('').apply(lambda x: splice1(x.upper()).strip())
base.loc[base['separator_present'] == 1, 'district_name'] = base['mp_apo_block'].fillna('').apply(lambda x: splice2(x.upper()).strip().strip(k))

base.loc[base['separator_present'] == 0, 'block_name'] = base['mp_apo_block'].fillna('').apply(lambda x: x.upper().strip())
base.loc[base['separator_present'] == 0, 'district_name'] = base['mp_apo_block'].fillna('').apply(lambda x: x.upper().strip())

ourb = list(base['block_name'].unique())
ourd = list(base['district_name'].unique())
ourb.sort()
ourd.sort()

base['matched_block_name'] = ''
base['matched_district_name'] =''

base['block_confidence'] = 0
base['district_confidence'] = 0

bmatch = []
bdict = {}
dmatch = []
ddict = {}

for k in ourb:
    temp = (k,) + process.extractOne(k, blist)
    bdict[k] = temp[1]
    if k == '':
        bdict[k] = ''
    base.loc[(base['block_name'] == k), 'matched_block_name'] = bdict[k]
    base.loc[(base['block_name'] == k), 'block_condfidence'] = temp[2]

for i in ourd:
    temp = (i,) + process.extractOne(i, dlist)
    ddict[i] = temp[1]
    if i == '':
        ddict[i] = ''
    base.loc[(base['district_name'] == i), 'matched_district_name'] = ddict[i]
    base.loc[(base['district_name'] == i), 'district_confidence'] = temp[2]

base = base[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block','separator_present',
             'block_name', 'matched_block_name','block_condfidence',
       'district_name',  'matched_district_name','district_confidence',
       'corrected_uid', 'corrected_mp_apo_name', 'corrected_mp_apo_block',
       'corrected_mp_apo_district', 'comment', 'recheck']]

base.to_excel(r'docs\location_matched_mp_apo_baseline.xlsx', index = False)
