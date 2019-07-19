import pandas as pd
from fuzzywuzzy import process
import re

pd.options.mode.chained_assignment = None
def clean_title(x):

	x = x.strip()
	list = ['\AMr.', '\ASH', '\AKU ', '\AKU.', '\ADR ', '\ADR.', '\ADr.', '\AMISS ', '\AMrs.', '\AMrs ', '\ASHRI ', ' JI\Z', ' Ji\Z', '\ASUSHRI ', '\ASMT ', '\ASmt ', '\ASMT.','\AMs.', '\AMS.', '\ASir ', 'Sir\Z']
	for k in list:
		if(re.search(k,x)):
			k = k.replace('\A', '')
			k = k.replace('\Z', '')
			x = x.replace(k, '')
	x = x.strip()
	return x

def match(x, list):
    temp = (x,) + process.extractOne(x, list)
    ret = temp[1]
    if x == '':
        ret = ''
    return ret

responses = pd.read_excel('../docs/location_matched_mp_apo_baseline.xlsx')
responses = responses[['mp_apo_name', 'matched_block_name']]
responses.columns = ['mp_apo_name', 'block_name']
print(responses.columns)
responses['mp_apo_name'] = responses['mp_apo_name'].apply(lambda x: clean_title(str(x)))

registration = pd.read_excel('name_loc_designation_match_edited.xlsx', sheet_name = 0)
df_baseline = registration[['Individual_UID', 'block_name_baseline', 'Name_Baseline']]

df_baseline['Individual_UID'] = df_baseline['Individual_UID'].apply(lambda x: int(x))
df_baseline['Name_Baseline'] = df_baseline['Name_Baseline'].fillna('')
df_baseline = df_baseline.loc[df_baseline['Name_Baseline']!='']

name_uid = pd.Series(df_baseline.Individual_UID.values,index=df_baseline.Name_Baseline).to_dict()
uid_block = pd.Series(df_baseline.block_name_baseline.values,index=df_baseline.Individual_UID).to_dict()

baseline_blocks = list(df_baseline['block_name_baseline'].fillna('').unique())
baseline_names =  list(df_baseline['Name_Baseline'].fillna('').unique())
print('Begin Matching...')
responses['matched_name'] = responses['mp_apo_name'].apply(lambda x: match(str(x), baseline_names))
print('Done Matching...')
# print(responses['matched_name'])
print('Adding UIDs...')
responses['matched_uid'] = responses['matched_name'].apply(lambda x: name_uid[x] if x!='' else '')
responses['matched_block'] = responses['matched_uid'].apply(lambda x: uid_block[x] if x!='' else '')
responses['blocks_exact_match'] = 0
responses.loc[responses['matched_block'] == responses['block_name'], 'blocks_match'] = 1
responses = responses[['mp_apo_name', 'block_name', 'matched_name', 'matched_block', 'blocks_match', 'matched_uid']]
responses.to_excel('matching_names_output.xlsx', index = False)
