import pandas as pd
from fuzzywuzzy import process
import re
import datetime
from tqdm import tqdm

#approach one
def clean_title(x):

	x = x.strip()
	list = ['\ASushri','\AMr.', '\AMR ','\AMR.','\ASH ', '\AKU ', '\AKu.', '\AKu ', '\AKU.', '\ADR ', '\ADR.', '\ADr.', '\AMISS ', '\AMrs.', '\AMrs ', '\AMRS', '\ASHRI ', ' JI\Z', ' Ji\Z', '\ASUSHRI ', '\ASMT ', '\ASmt ', '\ASMT.','\AMs.', '\AMS.', '\ASir ', 'Sir\Z', 'SIR\Z']
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
    return ret + ',' + str(temp[2])

pd.options.mode.chained_assignment = None
tqdm.pandas()

output_date = datetime.datetime.now().strftime("%d%m%Y")
responses = pd.read_csv('../docs/location_matched_blocks.csv')
responses = responses[['Res_uid', 'Name', 'Designation', 'Location', 'block_prediction', 'district_prediction']]
responses.columns = ['respondent_uid','mp_apo_name','Designation', 'Location', 'block_prediction', 'district_prediction']
#print(responses.columns)

responses['mp_apo_name'] = responses['mp_apo_name'].apply(lambda x: clean_title(str(x).upper())).fillna('')

registration = pd.read_excel('../docs/name_loc_designation_match_edited.xlsx', sheet_name = 0)
df_registration = registration[['Individual_UID','Name_Baseline','district_name_baseline','block_name_baseline','Designation_Baseline','district_name_april','block_name_april','Designation_April']]
df_registration['Individual_UID'] = df_registration['Individual_UID'].apply(lambda x: int(x))
df_registration['Name_Baseline'] = df_registration['Name_Baseline'].apply(lambda x: clean_title(str(x).upper())).fillna('')
df_registration = df_registration.loc[df_registration['Name_Baseline']!='']

name_uid = pd.Series(df_registration.Individual_UID.values,index=df_registration.Name_Baseline).to_dict()
uid_block = pd.Series(df_registration.block_name_baseline.values,index=df_registration.Individual_UID).to_dict()
uid_district = pd.Series(df_registration.district_name_baseline.values,index=df_registration.Individual_UID).to_dict()
uid_block_april = pd.Series(df_registration.block_name_april.values,index=df_registration.Individual_UID).to_dict()

baseline_blocks = list(df_registration['block_name_baseline'].fillna('').unique())
baseline_names =  list(df_registration['Name_Baseline'].fillna('').unique())

print('\nBegin Matching...\n')

responses['matching'] = responses['mp_apo_name'].progress_apply(lambda x: match(str(x), baseline_names) if ((x!='') & (x!='nan')) else ',')
responses['predicted_name'] = responses['matching'].apply(lambda x: x.split(',')[0])
responses['name_score'] = responses['matching'].apply(lambda x: x.split(',')[1])

print('Done Matching...')
print('Adding UIDs...')

responses['matched_uid'] = responses['predicted_name'].apply(lambda x: name_uid[x] if x!='' else '')
responses['matched_block_baseline'] = responses['matched_uid'].apply(lambda x: uid_block[x] if x!='' else '')
responses['matched_block_april'] = responses['matched_uid'].apply(lambda x: uid_block_april[x] if x!='' else '')
responses['matched_district'] = responses['matched_uid'].apply(lambda x: uid_district[x] if x!='' else '')
responses['blocks_exact_match'] = 0
responses.loc[(responses['matched_block_baseline'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']) | (responses['matched_block_april'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']), 'blocks_exact_match'] = 1

responses['district_exact_match'] = 0
responses.loc[responses['matched_district'] == responses['district_prediction'], 'district_exact_match'] = 1
responses.loc[responses['district_prediction'].fillna('') == '', 'district_exact_match'] = 0

responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'predicted_name'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'name_score'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'matched_uid'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'matched_block_baseline'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'matched_block_april'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['district_exact_match'] == 0), 'matched_district'] = ''

responses['approach'] = responses['matched_uid'].fillna('').apply(lambda x: 1 if x!='' else 0)

responses = responses[['respondent_uid', 'mp_apo_name', 'Designation', 'Location', 'block_prediction', 'district_prediction', 'predicted_name','name_score','matched_block_baseline','matched_block_april', 'blocks_exact_match', 'matched_district', 'district_exact_match','matched_uid', 'approach']]
responses.to_excel('../docs/matching_names_output_' + output_date + '.xlsx', index = False)
