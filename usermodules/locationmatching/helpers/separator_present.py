import pandas as pd
from fuzzywuzzy import process


def splice1(x):

    if ',' in x:
        return x.split(',')[0]
    if "(" in x:
        return x.split("(")[0]
    else: return x

def splice2(x):

    if ',' in x:
        return x.split(',')[1]
    if "(" in x:
        return x.split("(")[1].replace(')', '')
    else: return ''

#unused method that just shows a template for the location matching
#we read the location (in this case blocks) masterfile, and get a list of all true names
#convert to uppercase
#use process.extractOne to get the matching string out of the list with the highest confidence score
def block_prediction(block_name):

    blocks = pd.read_csv('./docs/mp_blocks_2017-2018.csv')
    blocks = blocks[blocks['state_code'] == 17]
    blist = list(blocks['block_name'].unique())
    blist.sort()
    blist = [b.upper() for b in blist]

    block_prediction, block_prediction_score = process.extractOne(block_name, blist)
    return block_prediction, block_prediction_score


def district_prediction(district_name):

    districts = pd.read_csv('./docs/mp_districts_2017-2018.csv')
    districts = districts[districts['state_code'] == 17]
    dlist = list(districts['block_name'].unique())
    dlist.sort()
    dlist = [d.upper() for d in dlist]

    district_prediction, district_prediction_score = process.extractOne(district_name, dlist)

    return district_prediction, district_prediction_score


def make_predictions(df):

    k = '('
    districts = pd.read_csv('./docs/mp_districts_2017-2018.csv')
    districts = districts[districts['state_code'] == 17]
    dlist = list(districts['district_name'].unique())
    dlist.sort()
    dlist = [x.upper() for x in dlist]

    blocks = pd.read_csv('./docs/mp_blocks_2017-2018.csv')
    blocks = blocks[blocks['state_code'] == 17]
    blist = list(blocks['block_name'].unique())
    blist.sort()
    blist = [b.upper() for b in blist]

    df['separator_present'] = df['Location'].fillna('').apply(lambda x: int((k in x) | (',' in x)))
    df['block_name'] = ''
    df['district_name'] = ''

    df.loc[(df['separator_present'] == 1) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'block_name'] = df['Location'].fillna('').apply(lambda x: splice1(x.upper()).strip())
    df.loc[(df['separator_present'] == 1) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'district_name'] = df['Location'].fillna('').apply(lambda x: splice2(x.upper()).strip().strip(k))

    ourb = list(df['block_name'].unique())
    ourd = list(df['district_name'].unique())
    ourb.sort()
    ourd.sort()

    df.loc[df['block_prediction'] == None, 'block_prediction'] = ''
    df.loc[df['district_prediction'] == None, 'district_prediction'] = ''

    df.loc[df['block_prediction_score'] == None, 'block_prediction_score'] = 0
    df.loc[df['district_prediction_score'] == None, 'district_prediction_score'] = 0

    bmatch = []
    bdict = {}
    dmatch = []
    ddict = {}

    #iterating through the block names we have
    #and finding the top match for each from the blocks masterlist
    for k in ourb:
        temp = (k,) + process.extractOne(k, blist)
        bdict[k] = temp[1]
        if k == '':
            bdict[k] = ''
        df.loc[(df['block_name'] == k) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'block_prediction'] = bdict[k]
        df.loc[(df['block_name'] == k) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'block_prediction_score'] = temp[2]

    #iterating through the district names we have
    #and finding the top match for each from the district masterlist
    for i in ourd:
        temp = (i,) + process.extractOne(i, dlist)
        ddict[i] = temp[1]
        if i == '':
            ddict[i] = ''
        df.loc[(df['district_name'] == i) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'district_prediction'] = ddict[i]
        df.loc[(df['district_name'] == i) & (df['exact_match_blocks'] == 0) & (df['exact_match_districts'] == 0) & (df['exact_match_full_name'] == 0), 'district_prediction_score'] = temp[2]

    df = df.drop(columns = ['block_name', 'district_name', 'separator_present'])

    return df
