'''
We tackle 3 different types of cases within Approach 2 (which is the location first approach).
After location matching, three cases exist: either we have just a block prediction, just a district prediction,
or predictions for both a block and a district. As a high level overview, Approach 2 basically scopes in to the
predicted location in the mastersheet, and searches for the best match to the response name (by comparing different calculations).
'''

#Approach Two refers to Location First matching
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import numpy as np
import math
import datetime
#from collections import defaultdict

#for the three different cases of location predictions
import namematching.helpers.approach_two_block_pred as approach_two_block_pred
import namematching.helpers.approach_two_district_pred as approach_two_district_pred
import namematching.helpers.approach_two_both_pred as approach_two_both_pred


# clean title only needs to be applied to registration dataframe here in
# approach 2 because responses df comes from Aneesh's output of approach 1
# -- he already ran this same function on the original responses in approach 1

#cleaning the name of titles such as Mr. Shri. Dr. etc etc
#to ensure consistency b/w response and mastersheet
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

def all_present(x):
	x = x.strip()

	all = '\AALL'
	if(re.search(all, x)):
		x = 1
	else:
		x = 0
	return x


def process_files():

	responses = pd.read_excel('./docs/approach_one_output.xlsx')

	#print(responses)
	#responses = responses.iloc[1000:2000]
	print(responses)

	#initialize this particular flag here
	responses['block_not_in_district'] = 0

	# this is edited in a specific format that is different that how Aneesh
	# edited it, which is documented
	# it also has Sehore district data now at the bottom with
	# dummy uid's - we don't have those yet
	registration = pd.read_excel('./docs/mastersheet_edited_two.xlsx',
								 sheet_name = 0)
	registration.rename(columns={'block_name_baseline': 'block_name',
								 'district_name_baseline': 'district_name',
								 'Name_Baseline': 'Name',
								 'Designation_Baseline': 'Designation'},
								 inplace=True)
	df_registration = registration[['Individual_UID', 'block_name', 'district_name', 'Name', 'Designation']]

	df_registration['Individual_UID'] = df_registration['Individual_UID'].apply(lambda x: int(x))
	#df_registration['Name'] = df_registration['Name'].fillna('').str.upper()

	# keep only datapoints with name input
	df_registration = df_registration.loc[df_registration['Name'] != '']

	# clean title only needs to be applied to registration dataframe here in
	# approach 2 because responses df comes from Aneesh's output of approach 1
	# -- he already ran this same function on the original responses in approach 1
	df_registration['Name'] = df_registration['Name'].apply(lambda x: clean_title(str(x).upper())).fillna('')

	print(df_registration)

	#print(responses.loc[responses['Designation'].isna(), 'Designation'])
	#print(responses['Designation'].loc[(responses['Designation'] != "Block APO") & (responses['Designation'] != "Block CEO")])
	return responses, df_registration


def set_empty_match_columns(row):

	row['matched_name_token_sort'] = ''
	row['matched_name_confidence'] = ''
	row['matched_uid'] = ''
	row['matched_block'] = ''
	row['matched_district'] = ''

	return row


# clean string to create a version with initials
# strings with one word remain the same
# everything before the last word gets "initialized"
# for example, "FIRST LAST" -> "F LAST"
# for example, "FIRST MIDDLE LAST" -> "F M LAST"
def get_initialed_name(name_original):

	# only if no periods exist
	if '.' not in name_original:
		name_list = name_original.split()
		name_final = ' '.join([name[0] for name in name_list[:-1]]) + ' ' + name_list[-1]
	else:
		# in cases with period, just replace with space
		name_final = name_original.replace(".", " ")

	return name_final


def set_match_data(row, df_registration_subset, fuzzy_calc):

	row['matched_name_confidence'] = fuzzy_calc[1]
	row['matched_uid'] = (df_registration_subset.loc[df_registration_subset['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
	row['matched_block'] = (df_registration_subset.loc[df_registration_subset['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
	row['matched_district'] = (df_registration_subset.loc[df_registration_subset['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
	row['matched_designation'] = (df_registration_subset.loc[df_registration_subset['Name'] == row['matched_name_token_sort'], 'Designation']).values[0]

	return row


def match_row(row, df_registration):

	#print(row['Name'])
	# already been covered in approach 1
	if row['approach'] == 1:
		return row

	if row['Name'] == 'NAN':
		#print('in none')
		row['matched_name_token_sort'] = None
		row['matched_name_confidence'] = None
		return row

	# for KATNI - which has an extra space
	if isinstance(row['district_prediction'], str):
		row['district_prediction'] = row['district_prediction'].strip()

	# Just block prediction
	if isinstance(row['block_prediction'], str) and not isinstance(row['district_prediction'], str):
		#print('block prediction')
		#print(row['Name'])
		return approach_two_block_pred.process_pred_on_block(row, df_registration)

	# Just district prediction
	if not isinstance(row['block_prediction'], str) and isinstance(row['district_prediction'], str):
		#print('district prediction')
		#print(row['Name'])
		return approach_two_district_pred.process_pred_on_district(row, df_registration)

	# Both block and district prediction
	if isinstance(row['block_prediction'], str) and isinstance(row['district_prediction'], str):
		print('both prediction')
		print(row['Name'])
		return approach_two_both_pred.process_pred_on_both(row, df_registration)

	return row



def perform_name_matching(responses, df_registration):


	responses = responses[['respondent_uid', 'mp_apo_name' , 'Designation',
						   'Location', 'block_prediction',
						   'block_prediction_score', 'district_prediction',
						   'district_prediction_score', 'matched_designation',
						   'approach', 'block_not_in_district']]

	responses.rename(columns={'mp_apo_name': 'Name'}, inplace=True)

	responses.loc[responses['Designation'] == 'Block APO', 'Designation'] = 'PO'
	responses.loc[responses['Designation'] == 'Block CEO', 'Designation'] = 'CEO'


	print('Begin matching starting with locations...')

	responses = responses.apply(lambda x: match_row(x, df_registration), axis=1)
	print('Done matching starting with locations...')

	responses['approach'] = 2

	responses.loc[responses['matched_name_token_sort'].notna(), 'blocks_exact_match'] = 0
	responses.loc[responses['matched_block'] == responses['block_prediction'], 'blocks_exact_match'] = 1

	responses.loc[responses['matched_name_token_sort'].notna(), 'district_exact_match'] = 0
	responses.loc[responses['matched_district'] == responses['district_prediction'], 'district_exact_match'] = 1

	responses.rename(columns={'Name': 'mp_apo_name',
							  'matched_name_token_sort': 'predicted_name',
							  'matched_name_confidence': 'name_score',
							  'matched_block': 'matched_block_baseline'}, inplace=True)

	responses.loc[responses['Designation'] == 'PO', 'Designation'] = 'Block APO'
	responses.loc[responses['Designation'] == 'CEO', 'Designation'] = 'Block CEO'
	print(responses)

	return responses


def approach_two():

	output_date = datetime.datetime.now().strftime("%d%m%Y")
	pd.options.mode.chained_assignment = None
	responses, df_registration = process_files()

	# only set to responses that were not covered with approach 1
	responses.loc[responses['approach'] == 0] = perform_name_matching(responses, df_registration)

	responses.rename(columns={'mp_apo_name': 'Name'}, inplace=True)
	responses.loc[responses['Name'] == 'NAN', 'approach'] = ''

	responses = \
		responses[['respondent_uid', 'Name', 'Designation', 'Location',
							'block_prediction', 'block_prediction_score',
							'district_prediction', 'district_prediction_score',
							'predicted_name', 'name_score', 'matched_uid',
							'matched_block_baseline', 'matched_block_april',
							'matched_district', 'blocks_exact_match',
							'district_exact_match', 'block_not_in_district', 'matched_designation',
							'approach']]

	responses.rename(columns = {'blocks_exact_match' : 'blocks_exact', 'district_exact_match' : 'districts_exact'}, inplace = True)

	#print(responses.loc[responses['Designation'].isnull() | responses['Designation'] == ''])
	#print(responses.loc[responses['Designation'].isna()])
	#print('after')
	#rename NAN to '' to mantain consistency
	responses['Name'] = responses['Name'].apply(lambda x: '' if (str(x).strip() == 'NAN') else x)

	#handling cases where all is present in location or name
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'predicted_name'] = ''
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'matched_uid'] = ''
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'matched_block_baseline'] = ''
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'matched_block_april'] = ''
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'matched_district'] = ''
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'matched_designation'] = ''
	#letting approach column be, as we can say that the correct thing to do is in fact to give no output

	#Renaming approach from 1/2 to Name First/ Location First
	responses['approach'] = responses['approach'].apply(lambda x: 'Name First' if str(x) == '1' else x)
	responses['approach'] = responses['approach'].apply(lambda x: 'Location First' if str(x) == '2' else x)

	#intialize flags
	responses['location_missing'] = 0
	responses['name_missing'] = 0
	responses['designation_missing'] = 0
	responses['all_present'] = 0
	responses['unique_perfect_name_wrong_location'] = 0
	responses['designation_mismatch'] = 0

	#reorder columns
	responses = \
		responses[['respondent_uid', 'Name', 'name_missing', 'Designation', 'designation_missing', 'Location', 'location_missing', 'all_present',
							'block_prediction', 'block_prediction_score',
							'district_prediction', 'district_prediction_score',
							'predicted_name', 'name_score', 'matched_uid',
							'matched_block_baseline', 'matched_block_april',
							'matched_district', 'blocks_exact',
							'districts_exact', 'block_not_in_district', 'unique_perfect_name_wrong_location', 'matched_designation', 'designation_mismatch',
							'approach']]

	#add flags based on values of other columns
	responses.loc[responses['Location'].isnull(), 'location_missing'] = 1
	responses.loc[responses['Name'].apply(lambda x: str(x)) == '', 'name_missing'] = 1
	responses.loc[responses['Designation'].isnull(), 'designation_missing'] = 1
	responses.loc[(responses['Name'].apply(lambda x: all_present(str(x))) == 1) | (responses['Location'].apply(lambda x: all_present(str(x))) == 1), 'all_present'] = 1
	responses.loc[(responses['name_score']==100) & ((responses['districts_exact'] == 0) | (responses['districts_exact'].fillna('') == '')) & ((responses['blocks_exact'] == 0) | (responses['blocks_exact'].fillna('') == '')), 'unique_perfect_name_wrong_location'] = 1
	responses.loc[(responses['matched_designation'].apply(lambda x: str(x).strip()) != responses['Designation'].apply(lambda x: str(x).replace('Block ', '').replace('A', '').strip())) & (responses['matched_designation'].fillna('') != '') & (responses['Designation'].fillna('') != ''), 'designation_mismatch'] = 1

	#print(responses.loc[(responses['matched_block_april'].fillna('') != responses['matched_block_baseline'].fillna('')) & (responses['approach'] == 'Name First')][['matched_block_baseline', 'matched_block_april']])

	#final output as excel file
	responses.to_excel('./docs/mp_block_matching_output_' + output_date + '.xlsx', index = False)
