# approach_two.py


import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
import numpy as np
import math
from collections import defaultdict

def process_files():

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


	responses = pd.read_csv('../case_specific_matches_code_separator/output/match_24072019.csv')
	print(responses)
	responses = responses.iloc[:100]
	responses = responses[['Res_uid', 'Name' , 'Designation', 'Location', 'block_prediction', 'district_prediction']]
	
	responses['Name'] = responses['Name'].apply(lambda x: clean_title(str(x)))
	print(responses)

	registration = pd.read_excel('name_loc_designation_match_edited.xlsx', sheet_name = 0)
	df_baseline = registration[['Individual_UID', 'block_name_baseline', 'district_name_baseline', 'Name_Baseline']]
	#df_baseline = df_baseline.iloc[:100]
	df_baseline['Individual_UID'] = df_baseline['Individual_UID'].apply(lambda x: int(x))
	df_baseline['Name_Baseline'] = df_baseline['Name_Baseline'].fillna('').str.upper()
	df_baseline = df_baseline.loc[df_baseline['Name_Baseline'] != '']
#	df_baseline = df_baseline.loc[(df_baseline['Name_Baseline']).notna() & 
#								  (df_baseline['district_name_baseline']).notna() &
#								  (df_baseline['block_name_baseline']).notna()]
#	
#	df_baseline = df_baseline.loc[pd.notna(df_baseline['Name_Baseline']) & 
#								  pd.notna(df_baseline['district_name_baseline']) &
#								  pd.notna(df_baseline['block_name_baseline'])]						

	print(df_baseline)

	return responses, df_baseline


def match_loc_start(row, df_baseline):
	print(row['Name'])
	if row['Name'] == 'nan':
		print('in none')
		row['matched_name_token_sort'] = None
		row['matched_name_confidence'] = None
		return row

	df_baseline_subset = df_baseline.loc[df_baseline['district_name_baseline'] == row['district_prediction']]
	print(df_baseline_subset)

	# grab just initials of row's Name and all df_baseline_subset's name_baselines
	# only if no periods exist - this is how things are cleaned
	if '.' not in row['Name']:
		name_list = row['Name'].split()
		name_final = ' '.join([name[0] for name in name_list[:-1]]) + ' ' + name_list[-1]
	else:
		name_final = row['Name']
	
	df_baseline_subset['Name_Baseline_initial'] = \
		df_baseline_subset['Name_Baseline'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

	print('df_baseline_subset')
	print(df_baseline_subset)

	baseline_names = list(df_baseline_subset['Name_Baseline_initial'].fillna('').unique())
	print(baseline_names)
	
	if baseline_names:
		# get other calcs also to see best
		ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.ratio))
		partial_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.partial_ratio))
		token_sort_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.token_sort_ratio))
		token_set_ratio_calc = list(process.extractOne(name_final, baseline_names, scorer = fuzz.token_set_ratio))

		print(row['Name'])
		print(name_final)
		print(ratio_calc)
		print(partial_ratio_calc)
		print(token_sort_ratio_calc)
		print(token_set_ratio_calc)


		row['matched_name_token_sort'] = token_sort_ratio_calc[0]
		row['matched_name_confidence'] = token_sort_ratio_calc[1]
		# need to add matched uid, block, and district
		#name_uid = {name:list(df_baseline_subset.loc[df_baseline_subset['Name_Baseline'] == name, 'Individual_UID']) for name in list(df_baseline_subset['Name_Baseline'])}
		row['matched_uid'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline_initial'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
		print(row['matched_uid'])
		row['matched_block'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline_initial'] == row['matched_name_token_sort'], 'block_name_baseline']).values[0]
		row['matched_district'] = row['matched_block'] = (df_baseline_subset.loc[df_baseline_subset['Name_Baseline_initial'] == row['matched_name_token_sort'], 'district_name_baseline']).values[0]
	else:
		row['matched_name_token_sort'] = ''
		row['matched_name_confidence'] = ''
		row['matched_uid'] = ''
		row['matched_block'] = ''
		row['matched_district'] = ''
	




	return row



def perform_name_matching_loc_start(responses, df_baseline):

	print('Begin matching starting with locations...')
	# for each row look within the block_prediction block in df_baseline 
	responses = responses.apply(lambda x: match_loc_start(x, df_baseline), axis=1)
	print('Done matching starting with locations...')
	responses['Approach'] = 2
	print(responses)

	return responses


def main():

	pd.options.mode.chained_assignment = None
	responses, df_baseline = process_files()

	responses_loc_start = perform_name_matching_loc_start(responses, df_baseline)



if __name__ == '__main__':
	main()
