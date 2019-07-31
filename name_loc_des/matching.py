import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
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
responses = responses[['Res_uid', 'Name', 'Designation', 'Location', 'block_prediction', 'block_prediction_score','district_prediction','district_prediction_score']]
responses.columns = ['respondent_uid','mp_apo_name','Designation', 'Location', 'block_prediction', 'block_prediction_score','district_prediction','district_prediction_score']
#print(responses.columns)

responses['mp_apo_name'] = responses['mp_apo_name'].apply(lambda x: clean_title(str(x).upper())).fillna('')
responses['block_prediction'] = responses['block_prediction'].apply(lambda x: str(x).replace('nan', '')).fillna('')
responses['district_prediction'] = responses['district_prediction'].apply(lambda x: str(x).replace('nan', '')).fillna('')

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
baseline_names =  list(df_registration['Name_Baseline'].fillna('').values.tolist())

print('\nBegin Matching...\n')

responses['matching'] = responses['mp_apo_name'].progress_apply(lambda x: match(str(x), baseline_names) if ((x!='') & (x!='nan')) else ',')
responses['predicted_name'] = responses['matching'].apply(lambda x: x.split(',')[0])
responses['name_score'] = responses['matching'].apply(lambda x: int(x.split(',')[1]))
responses['name_score'] = responses['name_score'].apply(lambda x: int(x))

print('Done Matching...')
print('Adding UIDs...')

responses['matched_uid'] = responses['predicted_name'].apply(lambda x: name_uid[x] if x!='' else '')
responses['matched_block_baseline'] = responses['matched_uid'].apply(lambda x: uid_block[x] if x!='' else '')
responses['matched_block_april'] = responses['matched_uid'].apply(lambda x: uid_block_april[x] if x!='' else '')
responses['matched_district'] = responses['matched_uid'].apply(lambda x: uid_district[x] if x!='' else '')

#first set to 0, then set to 1 where it matches, and then to '' where block prediction was absent
responses['blocks_exact_match'] = 0
responses.loc[(responses['matched_block_baseline'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']) | (responses['matched_block_april'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']), 'blocks_exact_match'] = 1
responses.loc[responses['block_prediction'].fillna('') == '', 'blocks_exact_match'] = ''

responses['district_exact_match'] = ''
responses.loc[(responses['block_prediction'].fillna('') == '') & (responses['matched_district'] == responses['district_prediction']), 'district_exact_match'] = 1
responses.loc[(responses['block_prediction'].fillna('') == '') & (responses['matched_district'] != responses['district_prediction']), 'district_exact_match'] = 0
responses.loc[responses['district_prediction'].fillna('') == '', 'district_exact_match'] = ''

responses.loc[(responses['name_score']==100) & (responses['matched_district'] == responses['district_prediction']), 'district_exact_match'] = 1

responses.loc[(responses['name_score'] < 80), 'predicted_name'] = ''
responses.loc[(responses['name_score'] < 80), 'matched_uid'] = ''
responses.loc[(responses['name_score'] < 80), 'matched_block_baseline'] = ''
responses.loc[(responses['name_score'] < 80), 'matched_block_april'] = ''
responses.loc[(responses['name_score'] < 80), 'matched_district'] = ''

responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'predicted_name'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_uid'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_baseline'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_april'] = ''
responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_district'] = ''

responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'predicted_name'] = ''
responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_uid'] = ''
responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_baseline'] = ''
responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_april'] = ''
responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_district'] = ''

responses_2 = responses[(responses['name_score']==100) & ((responses['district_exact_match'] == 0) | (responses['district_exact_match'] == ''))]

print(responses)
print(responses_2)
print('\nBeginning process for the 100 name_score entries...\n')

for line,row in tqdm(enumerate(responses_2.itertuples(), 1)):
	k = row.mp_apo_name
	count = 0
	print(k)
	for i in tqdm(baseline_names):
		if(fuzz.token_set_ratio(k,i) == 100): count+=1
	print(count)
	if(count > 1):
		responses.set_value(row.Index, 'predicted_name', '')
		responses.set_value(row.Index, 'matched_uid', '')
		responses.set_value(row.Index, 'matched_block_baseline', '')
		responses.set_value(row.Index, 'matched_block_april', '')
		responses.set_value(row.Index, 'matched_district', '')

print('\nDone with the 100 name_score cases...')

responses['approach'] = responses['matched_uid'].fillna('').apply(lambda x: 1 if x!='' else 0)

responses['name_absent'] = responses['mp_apo_name'].fillna('').apply(lambda x: 1 if (x=='')|(x=='NAN') else 0)
responses['name_exact_match'] = responses['name_score'].apply(lambda x: 1 if x==100 else 0)
responses['name_above_threshold'] = responses['name_score'].apply(lambda x: 1 if (x>80) & (x<100) else 0)
responses['name_match_and_block_match'] = 0
responses.loc[(responses['name_score']==100) &(responses['blocks_exact_match']==1), 'name_match_and_block_match'] = 1
responses['name_good_and_blocks_match'] = 0
responses.loc[(responses['name_score']>80) &(responses['blocks_exact_match']==1), 'name_good_and_blocks_match'] = 1

print('\nNo. of absent names: {}'.format(responses['name_absent'].sum()))
print('\nNo. of exact matching names: {}'.format(responses['name_exact_match'].sum()))
print('\nNo. of exact name matches with block exact matches: {}'.format(responses['name_match_and_block_match'].sum()))
print('\nNo. of good name matches: {}'.format(responses['name_above_threshold'].sum()))
print('\nNo. of good name matches and block exact matches: {}'.format(responses['name_good_and_blocks_match'].sum()))

responses = responses[['respondent_uid', 'mp_apo_name', 'Designation', 'Location', 'block_prediction', 'block_prediction_score', 'district_prediction', 'district_prediction_score', 'predicted_name','name_score','matched_block_baseline','matched_block_april', 'blocks_exact_match', 'matched_district', 'district_exact_match','matched_uid', 'approach']]
responses.to_excel('../docs/matching_names_output_' + output_date + '.xlsx', index = False)
