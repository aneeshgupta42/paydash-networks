# approach_two_both_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two# import approach_two.get_initialed_name, approach_two.set_empty_match_columns


def check_correct_loc_combination(row):

	df_mp_blocks = pd.read_csv('../docs/mp_blocks_2017-2018.csv')

	# check if block, district combination is empty 
	df_mp_blocks = df_mp_blocks.loc[(df_mp_blocks['block_name'] == row['block_prediction']) &
									(df_mp_blocks['district_name'] == row['district_prediction'])]
	if df_mp_blocks.empty:
		return False

	return True									


def process_pred_on_both(row, df_registration):
	print('in process_pred_on_both')
	# get matching block and district subsets
	df_registration_subset_block = df_registration.loc[df_registration['block_name'] == row['block_prediction']]
	df_registration_subset_district = df_registration.loc[df_registration['district_name'] == row['district_prediction']]

	# check if the full block, district input is a correct combination
	if check_correct_loc_combination(row) == True:
		print('check_correct_loc_combination True')
		# match on block full name
		if len(row['Name'].split()) == 1:
			print('len == 1')
			registration_names_list = list(df_registration_subset_block['Name'].fillna('').unique())
			if registration_names_list:
				partial_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.partial_ratio))

				# CUTOFF FOR GOING TO DISTRICT MATCH
				cutoff = 75
				if partial_ratio_calc[1] >= cutoff:
					print('above cutoff of 75')
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == partial_ratio_calc[0], 'Name']).values[0]
					row['matched_name_confidence'] = partial_ratio_calc[1]
					row['matched_uid'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					row['matched_block'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
				else:
					# below block cutoff - check district match
					print('below cutoff of 75')
					registration_names_list = list(df_registration_subset_district['Name'].fillna('').unique())
					if registration_names_list:
						partial_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.partial_ratio))
						# SET CUTOFF FOR LOW SCORE OF DISTRICT MATCH HERE - SHOULD THEN LEAVE ALL BLANK
						# AND CALL approach_two.set_empty_match_columns
						# if partial_ratio_calc[1] <= new cutoff is what the line would be
						row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == partial_ratio_calc[0], 'Name']).values[0]
						row['matched_name_confidence'] = partial_ratio_calc[1]
						row['matched_uid'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
						row['matched_block'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
						row['matched_district'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
					else:
						row = approach_two.set_empty_match_columns(row)
			else:
				row = approach_two.set_empty_match_columns(row)

		else:
			print('len > 1')
			# match on block initials - len > one word
			name_final = approach_two.get_initialed_name(row['Name'])

			df_registration_subset_block['Name_initial'] = \
				df_registration_subset_block['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

			registration_names_list_init = list(df_registration_subset_block['Name_initial'].fillna('').unique())
			registration_names_list_full = list(df_registration_subset_block['Name'].fillna('').unique())
			if registration_names_list_init:
				partial_ratio_calc_init = list(process.extractOne(name_final, registration_names_list_init, scorer = fuzz.partial_ratio))
				partial_ratio_calc_full = list(process.extractOne(row['Name'], registration_names_list_full, scorer = fuzz.partial_ratio))
				init_larger = 0
				if partial_ratio_calc_init[1] >= partial_ratio_calc_full[1]:
					partial_ratio_calc = partial_ratio_calc_init
					init_larger = 1
				else: partial_ratio_calc = partial_ratio_calc_full
				# CUTOFF FOR GOING TO DISTRICT MATCH
				cutoff = 0
				if partial_ratio_calc[1] >= cutoff:
					print('above cutoff of 0')
					if init_larger == 1:
						row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name_initial'] == partial_ratio_calc[0], 'Name']).values[0]
					else: row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == partial_ratio_calc[0], 'Name']).values[0]
					row['matched_name_confidence'] = partial_ratio_calc[1]
					row['matched_uid'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					row['matched_block'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
				else:
					print('below cutoff of 0')
					# below block cutoff - check district match
					registration_names_list = list(df_registration_subset_district['Name_initial'].fillna('').unique())
					if registration_names_list:
						partial_ratio_calc = list(process.extractOne(name_final, registration_names_list, scorer = fuzz.partial_ratio))
						# SET CUTOFF FOR LOW SCORE OF DISTRICT MATCH HERE - SHOULD THEN LEAVE ALL BLANK
						# AND CALL approach_two.set_empty_match_columns
						# if partial_ratio_calc[1] <= new cutoff is what the line would be
						row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == partial_ratio_calc[0], 'Name']).values[0]
						row['matched_name_confidence'] = partial_ratio_calc[1]
						row['matched_uid'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
						row['matched_block'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
						row['matched_district'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
					else:
						row = approach_two.set_empty_match_columns(row)
			else:
				row = approach_two.set_empty_match_columns(row)
	else:
		# block, district combination incorrect
		# compare matches on block and on district and take higher of the two
		print('check_correct_loc_combination False')
		# first if response is one word
		if len(row['Name'].split()) == 1:
			print('len == 1')
			registration_names_list_district = list(df_registration_subset_district['Name'].fillna('').unique())
			registration_names_list_block = list(df_registration_subset_block['Name'].fillna('').unique())

			if registration_names_list_district:
				# get other calcs also to see best
				#ratio_calc = list(process.extractOne(row['Name'], registration_names_list_district, scorer = fuzz.ratio))
				#partial_ratio_calc = list(process.extractOne(row['Name'], registration_names_list_district, scorer = fuzz.partial_ratio))
				token_sort_ratio_calc_district = list(process.extractOne(row['Name'], registration_names_list_district, scorer = fuzz.token_sort_ratio))
				#token_set_ratio_calc = list(process.extractOne(row['Name'], registration_names_list_district, scorer = fuzz.token_set_ratio))

				# for block prediction
				if registration_names_list_block:
					token_sort_ratio_calc_block = list(process.extractOne(row['Name'], registration_names_list_block, scorer = fuzz.token_sort_ratio))
				else: 
					token_sort_ratio_calc_block = ['', 0]


				if token_sort_ratio_calc_district[1] > token_sort_ratio_calc_block[1]:
					print('prediction on district match is higher')
					# prediction on district match is higher
					row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_sort_ratio_calc_district[0], 'Name']).values[0]
					row['matched_name_confidence'] = token_sort_ratio_calc_district[1]
					# need to add matched uid, block, and district
					#name_uid = {name:list(df_registration_subset_district.loc[df_registration_subset_district['Name'] == name, 'Individual_UID']) for name in list(df_registration_subset_district['Name'])}
					row['matched_uid'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					#print(row['Name'])
					row['matched_block'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]

				else:
					print('prediction on block match is higher')
					# match on block prediction has higher score
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_sort_ratio_calc_block[0], 'Name']).values[0]
					row['matched_name_confidence'] = token_sort_ratio_calc_block[1]
					row['matched_uid'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					row['matched_block'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
			else:
				row = approach_two.set_empty_match_columns(row)
		else:
			# len > one word - match on initials
			print('len > 1')
			name_final = approach_two.get_initialed_name(row['Name'])

			df_registration_subset_district['Name_initial'] = \
				df_registration_subset_district['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

			df_registration_subset_block['Name_initial'] = \
				df_registration_subset_block['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

			registration_names_list_district = list(df_registration_subset_district['Name_initial'].fillna('').unique())
			registration_names_list_block = list(df_registration_subset_block['Name_initial'].fillna('').unique())

			if registration_names_list_district:
				token_set_ratio_calc_district = list(process.extractOne(name_final, registration_names_list_district, scorer = fuzz.token_set_ratio))

				# for block prediction
				if registration_names_list_block:
					token_set_ratio_calc_block = list(process.extractOne(name_final, registration_names_list_block, scorer = fuzz.token_set_ratio))
				else: 
					token_set_ratio_calc_block = ['', 0]

				if token_set_ratio_calc_district[1] > token_set_ratio_calc_block[1]:
					print('prediction on district match is higher')
					# prediction on district match is higher
					row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc_district[0], 'Name']).values[0]
					row['matched_name_confidence'] = token_set_ratio_calc_district[1]
					# need to add matched uid, block, and district
					#name_uid = {name:list(df_registration_subset_district.loc[df_registration_subset_district['Name'] == name, 'Individual_UID']) for name in list(df_registration_subset_district['Name'])}
					row['matched_uid'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					#print(row['Name'])
					row['matched_block'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
				else:
					print('prediction on block match is higher')
					# match on block prediction has higher score
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name_initial'] == token_set_ratio_calc_block[0], 'Name']).values[0]
					row['matched_name_confidence'] = token_set_ratio_calc_block[1]
					row['matched_uid'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
					row['matched_block'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
					row['matched_district'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
			else:
				row = approach_two.set_empty_match_columns(row)

	print(row)
	return row