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


	responses = pd.read_csv('../case_specific_matches_code_separator/output/match_22072019.csv')
	responses = responses.iloc[:30]
	responses = responses[['Res_uid', 'Name' , 'Designation', 'Location', 'block_prediction', 'district_prediction']]
	
	responses['Name'] = responses['Name'].apply(lambda x: clean_title(str(x)))
	print(responses)

	registration = pd.read_excel('name_loc_designation_match_edited.xlsx', sheet_name = 0)
	df_baseline = registration[['Individual_UID', 'block_name_baseline', 'district_name_baseline', 'Name_Baseline']]
	#df_baseline = df_baseline.iloc[:100]
	df_baseline['Individual_UID'] = df_baseline['Individual_UID'].apply(lambda x: int(x))
	df_baseline['Name_Baseline'] = df_baseline['Name_Baseline'].fillna('').str.upper()
	df_baseline = df_baseline.loc[df_baseline['Name_Baseline']!='']

	print(df_baseline)

	return responses, df_baseline


def match_name_start(row, baseline_names):
	
	if row['Name'] == 'nan':
		print('in none')
		row['matched_name_token_sort'] = None
		row['matched_name_confidence'] = None
		return row
	
	token_sort_ratio_calc = list(process.extractOne(row['Name'], baseline_names, scorer = fuzz.token_sort_ratio))
	row['matched_name_token_sort'] = token_sort_ratio_calc[0]
	row['matched_name_confidence'] = token_sort_ratio_calc[1]
	
	return row


def perform_name_matching_name_start(responses, df_baseline):
	
	# get baseline_names for extractone function
	baseline_names = list(df_baseline['Name_Baseline'].fillna('').unique())

	print('Begin matching starting with names...')
	responses = responses.apply(lambda x: match_name_start(x, baseline_names), axis=1)
	print('Done matching starting with names...')
	print(responses)
	#return responses
	
	print('Adding UIDs...')

	# are these necessary?
	baseline_blocks = list(df_baseline['block_name_baseline'].fillna('').unique())
	baseline_districts = list(df_baseline['district_name_baseline'].fillna('').unique())
	
	
	# LOOK FOR BEST MATCH LOCATION OF UID/PERSON
	# DOING FUZZY MATCH OF SUBSET OF LOCATIONS THAT A DATA POINT (PERSON) HAS
	# WILL ACCOUNT FOR BOTH TRANSFERS ACROSS MONTHS AND IF THE PERSON HAS MULTIPLE
	# POSITION IN DIFFERENT BLOCKS/ALSO DISTRICTS
	# create dicts for getting matches - problem because of repeated names/uids
	#name_uid = defaultdict(list)
	#name_uid = dict()
	#for name in list(df_baseline['Name_Baseline']):
	#	name_uid[name] = list(df_baseline.loc[df_baseline['Name_Baseline'] == name, 'Individual_UID'])
	name_uid = {name:list(df_baseline.loc[df_baseline['Name_Baseline'] == name, 'Individual_UID']) for name in list(df_baseline['Name_Baseline'])}
	#[name_uid[name] = list(df_baseline.loc[df_baseline['Name_Baseline'] == name, 'Individual_UID']) for name in list(df_baseline['Name_Baseline'])]
	print(name_uid)
	
	uid_block = {uid:list(df_baseline.loc[df_baseline['Individual_UID'] == uid, 'block_name_baseline']) for uid in list(df_baseline['Individual_UID'])}
	#for uid in list(df_baseline['Individual_UID']):
	#	uid_block[uid] = list(df_baseline.loc[df_baseline['Individual_UID'] == uid, 'block_name_baseline'])
	print(uid_block)

	uid_district = {uid:list(df_baseline.loc[df_baseline['Individual_UID'] == uid, 'district_name_baseline']) for uid in list(df_baseline['Individual_UID'])}
	print('uid_district')
	print(uid_district)
	#for uid in list(df_baseline['Individual_UID']):
	#	uid_district[uid] = list(df_baseline.loc[df_baseline['Individual_UID'] == uid, 'district_name_baseline'])

	#name_uid = pd.Series(df_baseline.Individual_UID.values, index=df_baseline.Name_Baseline).to_dict()
	#uid_block = pd.Series(df_baseline.block_name_baseline.values, index=df_baseline.Individual_UID).to_dict()
	#uid_district = pd.Series(df_baseline.district_name_baseline.values, index=df_baseline.Individual_UID).to_dict()	
	
	responses['matched_uid'] = responses['matched_name_token_sort'].apply(lambda x: name_uid[x][0] if x != None else '')
	#print(responses['matched_uid'])
	#list(process.extractOne(uid_block[x], baseline_names, scorer = fuzz.ratio))[0]
	
	#responses['matched_block'] = responses['matched_uid'].apply(lambda x: uid_block[x] if x != '' else '')
	
	responses['matched_block'] = \
		responses.apply(lambda x: list(process.extractOne(x['block_prediction'], uid_block[x['matched_uid']], scorer = fuzz.ratio))[0] if x['matched_uid'] != '' else '', axis=1)
	print('matched_block')
	#print(responses)
	#responses['matched_district'] = responses['matched_uid'].apply(lambda x: uid_district[x] if x != '' else '')
	
	responses['matched_district'] = \
		responses.apply(lambda x: list(process.extractOne(x['district_prediction'], uid_district[x['matched_uid']], scorer = fuzz.ratio))[0] if x['matched_uid'] != '' and isinstance(x['district_prediction'], str) else '', axis=1)
	print(responses)
	# only set for not null
	responses.loc[responses['matched_name_token_sort'].notna(), 'blocks_exact_match'] = 0
	responses.loc[responses['matched_block'] == responses['block_prediction'], 'blocks_exact_match'] = 1

	responses.loc[responses['matched_name_token_sort'].notna(), 'districts_exact_match'] = 0
	responses.loc[responses['matched_district'] == responses['district_prediction'], 'districts_exact_match'] = 1
	print(responses)
#	responses = responses[['Location', 'block_name', 'matched_name', 'matched_block', 'blocks_match', 'matched_uid']]
#	print(responses.head())
#	
	return responses


def match_loc_start(row, df_baseline):
	if row['Name'] == 'nan':
		print('in none')
		row['matched_name_token_sort'] = None
		row['matched_name_confidence'] = None
		return row

	df_baseline_block = df_baseline.loc[df_baseline['block_name_baseline'] == row['block_prediction']]

	baseline_names = list(df_baseline_block['Name_Baseline'].fillna('').unique())
	print(baseline_names)
	
	if baseline_names:
		# get other calcs also to see best
		token_sort_ratio_calc = list(process.extractOne(row['Name'], baseline_names, scorer = fuzz.token_sort_ratio))
		row['matched_name_token_sort'] = token_sort_ratio_calc[0]
		row['matched_name_confidence'] = token_sort_ratio_calc[1]
	else:
		row['matched_name_token_sort'] = ''
		row['matched_name_confidence'] = ''
	
	return row



def perform_name_matching_loc_start(responses, df_baseline):

	print('Begin matching starting with locations...')
	# for each row look within the block_prediction block in df_baseline 
	responses = responses.apply(lambda x: match_loc_start(x, df_baseline), axis=1)
	print('Done matching starting with locations...')
	print(responses)

	return responses




def main():

	pd.options.mode.chained_assignment = None
	responses, df_baseline = process_files()

	#responses_name_start = perform_name_matching_name_start(responses, df_baseline)

	responses_loc_start = perform_name_matching_loc_start(responses, df_baseline)

	#responses.to_excel('matching_names_output.xlsx', index = False)


if __name__ == '__main__':
	main()

