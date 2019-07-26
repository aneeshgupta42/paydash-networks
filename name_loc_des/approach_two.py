# approach_two.py


import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import numpy as np
import math
from collections import defaultdict


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


def process_files():


	responses = pd.read_excel('../docs/matching_names_output_24072019.xlsx')
	print(responses)

	#print(responses)
	responses = responses.iloc[:100]
	#responses = responses[['Res_uid', 'Name' , 'Designation', 'Location', 'block_prediction', 'district_prediction']]
	# From Aneesh's code
	#responses = responses[['respondent_uid', 'mp_apo_name' , 'Designation', 'Location', 'block_prediction', 'district_prediction', 'approach']]
	#responses.rename(columns={'mp_apo_name': 'Name'}, inplace=True)
	
	# don't need to clean because comes in clean from Aneesh's code
	#responses['Name'] = responses['Name'].apply(lambda x: clean_title(str(x)))
	print(responses)

	registration = pd.read_excel('name_loc_designation_match_edited.xlsx', sheet_name = 0)
	df_baseline = registration[['Individual_UID', 'block_name_baseline', 'district_name_baseline', 'Name_Baseline']]

	df_baseline['Individual_UID'] = df_baseline['Individual_UID'].apply(lambda x: int(x))
	#df_baseline['Name_Baseline'] = df_baseline['Name_Baseline'].fillna('').str.upper()
	df_baseline = df_baseline.loc[df_baseline['Name_Baseline'] != '']
	
	# need to clean baseline data as well
	df_registration['Name_Baseline'] = df_registration['Name_Baseline'].apply(lambda x: clean_title(str(x).upper())).fillna('')					

	print(df_baseline)

	return responses, df_baseline


def match_loc_start(row, df_baseline):
	#print(row['Name'])
	if row['Name'] == 'NAN':
		#print('in none')
		row['matched_name_token_sort'] = None
		row['matched_name_confidence'] = None
		return row
	if isinstance(row['district_prediction'], str):
		row['district_prediction'] = row['district_prediction'].strip()

	df_baseline_subset = df_baseline.loc[df_baseline['district_name_baseline'] == row['district_prediction']]
	if row['Name'] == 'AJEET SINGH':
		print('AJEET SINGH')
		print(row)
		print(df_baseline_subset)
	#print(row['district_prediction'])
	#print(df_baseline_subset)

	# grab just initials of row's Name and all df_baseline_subset's name_baselines
	# only if no periods exist - this is how things are cleaned
	if '.' not in row['Name']:
		name_list = row['Name'].split()
		name_final = ' '.join([name[0] for name in name_list[:-1]]) + ' ' + name_list[-1]
	else:
		name_final = row['Name']
	
	df_baseline_subset['Name_Baseline_initial'] = \
		df_baseline_subset['Name_Baseline'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

	#print('df_baseline_subset')
	#print(df_baseline_subset)

	baseline_names = list(df_baseline_subset['Name_Baseline_initial'].fillna('').unique())
	#print(baseline_names)
	
	if baseline_names:
		# get other calcs also to see best
		ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.ratio))
		partial_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.partial_ratio))
		token_sort_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.token_sort_ratio))
		token_set_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.token_set_ratio))

		#print(row['Name'])
		#print(name_final)
		#print(ratio_calc)
		#print(partial_ratio_calc)
		#print(token_sort_ratio_calc)
		#print(token_set_ratio_calc)

		#print(token_sort_ratio_calc[0])
		#print(df_baseline_subset)
		#row['matched_name_token_sort'] = token_sort_ratio_calc[0]
		row['matched_name_token_sort'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline_initial'] == token_sort_ratio_calc[0], 'Name_Baseline']).values[0]
		row['matched_name_confidence'] = token_sort_ratio_calc[1]
		# need to add matched uid, block, and district
		#name_uid = {name:list(df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == name, 'Individual_UID']) for name in list(df_baseline_subset['Name_Baseline'])}
		row['matched_uid'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
		#print(row['Name'])
		
		
		row['matched_block'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == row['matched_name_token_sort'], 'block_name_baseline']).values[0]
		#if row['Name'] == 'CHANDAR MANDLOI':
		#	print('Chandar Singh Man')
		#	print(df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == row['matched_name_token_sort'], 'block_name_baseline'])
		#	print(row['matched_block'])

		row['matched_district'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == row['matched_name_token_sort'], 'district_name_baseline']).values[0]
	else:
		row['matched_name_token_sort'] = ''
		row['matched_name_confidence'] = ''
		row['matched_uid'] = ''
		row['matched_block'] = ''
		row['matched_district'] = ''
	


	return row



def perform_name_matching_loc_start(responses, df_baseline):
	responses = responses[['respondent_uid', 'mp_apo_name' , 'Designation', 'Location', 'block_prediction', 'district_prediction', 'approach']]
	responses.rename(columns={'mp_apo_name': 'Name'}, inplace=True)

	print('Begin matching starting with locations...')
	# for each row look within the block_prediction block in df_baseline 
	responses = responses.apply(lambda x: match_loc_start(x, df_baseline), axis=1)
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
	print(responses)

	return responses


def main():

	pd.options.mode.chained_assignment = None
	responses, df_baseline = process_files()

	responses.loc[responses['approach'] == 0] = perform_name_matching_loc_start(responses, df_baseline)
	
	responses.rename(columns={'mp_apo_name': 'Name'}, inplace=True)
	responses.loc[responses['Name'] == 'NAN', 'approach'] = ''

	responses = \
		responses[['respondent_uid', 'Name', 'Designation', 'Location',
							'block_prediction', 'district_prediction',
							'predicted_name', 'name_score', 'matched_uid',
							'matched_block_baseline', 'matched_block_april',
							'matched_district', 'blocks_exact_match',
							'district_exact_match', 'approach']]

	print(responses)
	#responses.to_excel('matching_names_from_responses_final_25072019.xlsx', index = False)



if __name__ == '__main__':
	main()
