import pandas as pd
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import re
import datetime
from tqdm import tqdm


#does not cover additional charge yet
#function for cleaning away titles, that maybe inconsitent across different sources
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

def approach_one():

	#turn off warnings
	pd.options.mode.chained_assignment = None
	#tqdm progress bar because process takes a fair bit of time
	tqdm.pandas()

	output_date = datetime.datetime.now().strftime("%d%m%Y")
	#read response sheet
	responses = pd.read_csv('./docs/location_matched_blocks.csv')
	responses = responses[['Res_uid', 'Name', 'Designation', 'Location', 'block_prediction', 'block_prediction_score','district_prediction','district_prediction_score']]
	responses.columns = ['respondent_uid','mp_apo_name','Designation', 'Location', 'block_prediction', 'block_prediction_score','district_prediction','district_prediction_score']

	#cleaning
	responses['mp_apo_name'] = responses['mp_apo_name'].apply(lambda x: clean_title(str(x).upper())).fillna('')
	responses['block_prediction'] = responses['block_prediction'].apply(lambda x: str(x).replace('nan', '')).fillna('')
	responses['district_prediction'] = responses['district_prediction'].apply(lambda x: str(x).replace('nan', '')).fillna('')

	#read registration sheet - used as master list for names
	registration = pd.read_excel('./docs/name_loc_designation_match_edited.xlsx', sheet_name = 0)
	df_registration = registration[['Individual_UID','Name_Baseline','district_name_baseline','block_name_baseline','Designation_Baseline','district_name_april','block_name_april','Designation_April']]
	df_registration['Individual_UID'] = df_registration['Individual_UID'].apply(lambda x: int(x))
	df_registration['Name_Baseline'] = df_registration['Name_Baseline'].apply(lambda x: clean_title(str(x).upper())).fillna('')
	df_registration = df_registration.loc[df_registration['Name_Baseline']!='']
	df_registration = df_registration.drop_duplicates(subset = 'Individual_UID')

	#get dictionaries between names, uid, blocks and district
	name_uid = pd.Series(df_registration.Individual_UID.values,index=df_registration.Name_Baseline).to_dict()
	uid_block = pd.Series(df_registration.block_name_baseline.values,index=df_registration.Individual_UID).to_dict()
	uid_district = pd.Series(df_registration.district_name_baseline.values,index=df_registration.Individual_UID).to_dict()
	uid_block_april = pd.Series(df_registration.block_name_april.values,index=df_registration.Individual_UID).to_dict()
	uid_designation = pd.Series(df_registration.Designation_Baseline.values,index=df_registration.Individual_UID).to_dict()
	#list of 'true' names for the purpose of matching
	baseline_names =  list(df_registration['Name_Baseline'].fillna('').values.tolist())

	print('\nBegin Matching...\n')
	#matching takes place - progress_apply from tqdm prints out a nice progress bar

	responses['matching'] = responses['mp_apo_name'].progress_apply(lambda x: match(str(x), baseline_names) if ((x!='') & (x!='nan')) else ',')
	responses['predicted_name'] = responses['matching'].apply(lambda x: x.split(',')[0])
	responses['name_score'] = responses['matching'].apply(lambda x: int(x.split(',')[1]))
	responses['name_score'] = responses['name_score'].apply(lambda x: int(x))

	print('Done Matching...')
	print('Adding UIDs...')

	#add uids and other fields using the dictionary
	responses['matched_uid'] = responses['predicted_name'].apply(lambda x: name_uid[x] if x!='' else '')
	responses['matched_block_baseline'] = responses['matched_uid'].apply(lambda x: uid_block[x] if x!='' else '')
	responses['matched_block_april'] = responses['matched_uid'].apply(lambda x: uid_block_april[x] if x!='' else '')
	responses['matched_district'] = responses['matched_uid'].apply(lambda x: uid_district[x] if x!='' else '')
	responses['matched_designation'] = responses['matched_uid'].apply(lambda x: uid_designation[x] if x!='' else '')
	#checking is blocks match
	#first set to 0, then set to 1 where it matches, and then to '' where block prediction was absent
	responses['blocks_exact_match'] = 0
	responses.loc[(responses['matched_block_baseline'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']) | (responses['matched_block_april'].apply(lambda x: str(x).replace('_', ' ')) == responses['block_prediction']), 'blocks_exact_match'] = 1
	responses.loc[responses['block_prediction'].fillna('') == '', 'blocks_exact_match'] = ''

	#similar as above, checking if district of name and matched name match
	responses['district_exact_match'] = ''
	responses.loc[(responses['block_prediction'].fillna('') == '') & (responses['matched_district'] == responses['district_prediction']), 'district_exact_match'] = 1
	responses.loc[(responses['block_prediction'].fillna('') == '') & (responses['matched_district'] != responses['district_prediction']), 'district_exact_match'] = 0
	responses.loc[responses['district_prediction'].fillna('') == '', 'district_exact_match'] = ''

	#special check for cases where there is an exactly matching name present
	responses.loc[(responses['name_score']==100) & (responses['matched_district'] == responses['district_prediction']), 'district_exact_match'] = 1

	#discard bad name matches -- their matching will be attempted through approach 2
	responses.loc[(responses['name_score'] < 80), 'predicted_name'] = ''
	responses.loc[(responses['name_score'] < 80), 'matched_uid'] = ''
	responses.loc[(responses['name_score'] < 80), 'matched_block_baseline'] = ''
	responses.loc[(responses['name_score'] < 80), 'matched_block_april'] = ''
	responses.loc[(responses['name_score'] < 80), 'matched_district'] = ''
	responses.loc[(responses['name_score'] < 80), 'matched_designation'] = ''

	#discard where blocks dont match
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'predicted_name'] = ''
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_uid'] = ''
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_baseline'] = ''
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_april'] = ''
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_district'] = ''
	responses.loc[(responses['blocks_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_designation'] = ''


	#since district check only kicks in where blocks are absent, discard where districts dont match as well
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'predicted_name'] = ''
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_uid'] = ''
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_baseline'] = ''
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_block_april'] = ''
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_district'] = ''
	responses.loc[(responses['district_exact_match'] == 0) & (responses['name_score'] != 100), 'matched_designation'] = ''

	#for perfect name matches, we need to check for duplicate names, as well as district matches
	responses_2 = responses[(responses['name_score']==100) & ((responses['district_exact_match'] == 0) | (responses['district_exact_match'] == ''))]
	print('\nBeginning process for the 100 name_score entries...\n')

	#if same name exists twice, leave perfect name matches to it alone, and cover in approach 2
	for line,row in tqdm(enumerate(responses_2.itertuples(), 1)):
		k = row.mp_apo_name
		count = 0
		#print(k)
		for i in baseline_names:
			if(fuzz.token_set_ratio(k,i) == 100): count+=1
		#print(count)
		if(count > 1):
			responses.set_value(row.Index, 'predicted_name', '')
			responses.set_value(row.Index, 'matched_uid', '')
			responses.set_value(row.Index, 'matched_block_baseline', '')
			responses.set_value(row.Index, 'matched_block_april', '')
			responses.set_value(row.Index, 'matched_district', '')
			responses.set_value(row.Index, 'matched_designation', '')


	print('\nDone with the 100 name_score cases...')

	responses['approach'] = responses['matched_uid'].fillna('').apply(lambda x: 1 if x!='' else 0)

	#discard where no location given - discarding them is the correct output (approach one)
	print('\nNo. of location blank cases: {}'.format(len(responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == '')])))
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'predicted_name'] = ''
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'matched_uid'] = ''
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'matched_block_baseline'] = ''
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'matched_block_april'] = ''
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'matched_district'] = ''
	responses.loc[(responses['block_prediction'] == '') & (responses['district_prediction'] == ''), 'matched_designation'] = ''

	#simple statistical count of different cases
	responses['name_absent'] = responses['mp_apo_name'].fillna('').apply(lambda x: 1 if (x=='')|(x=='NAN') else 0)
	responses['name_exact_match'] = responses['name_score'].apply(lambda x: 1 if x==100 else 0)
	responses['name_above_threshold'] = responses['name_score'].apply(lambda x: 1 if (x>=80) & (x<100) else 0)
	responses['name_match_and_block_match'] = 0
	responses.loc[(responses['name_score']==100) &(responses['blocks_exact_match']==1), 'name_match_and_block_match'] = 1
	responses['name_good_and_blocks_match'] = 0
	responses.loc[(responses['name_score']>80) &(responses['blocks_exact_match']==1), 'name_good_and_blocks_match'] = 1

	print('\nNo. of absent names: {}'.format(responses['name_absent'].sum()))
	print('\nNo. of exact matching names: {}'.format(responses['name_exact_match'].sum()))
	print('\nNo. of exact name matches with block exact matches: {}'.format(responses['name_match_and_block_match'].sum()))
	print('\nNo. of good name matches: {}'.format(responses['name_above_threshold'].sum()))
	print('\nNo. of good name matches and block exact matches: {}'.format(responses['name_good_and_blocks_match'].sum()))

	#keep only relevant columns
	designation_mismatch = responses.loc[(responses['approach'] == 1) & (responses['matched_designation'].apply(lambda x: str(x).strip()) != responses['Designation'].apply(lambda x: str(x).replace('Block ', '').replace('A', '').strip())) & (responses['matched_designation'].apply(lambda x: str(x).strip()) !='')]
	print(designation_mismatch)
	designation_mismatch = designation_mismatch[['respondent_uid', 'mp_apo_name', 'Designation', 'Location', 'block_prediction', 'block_prediction_score', 'district_prediction', 'district_prediction_score', 'predicted_name','name_score','matched_block_baseline','matched_block_april', 'blocks_exact_match', 'matched_district', 'district_exact_match','matched_uid','matched_designation','approach']]
	designation_mismatch.to_excel('./docs/designation_mismatch_scrutiny_' + output_date+ '.xlsx', index = False)

	responses = responses[['respondent_uid', 'mp_apo_name', 'Designation', 'Location', 'block_prediction', 'block_prediction_score', 'district_prediction', 'district_prediction_score', 'predicted_name','name_score','matched_block_baseline','matched_block_april', 'blocks_exact_match', 'matched_district', 'district_exact_match','matched_uid','matched_designation','approach']]
	responses.to_excel('./docs/approach_one_output.xlsx', index = False)
