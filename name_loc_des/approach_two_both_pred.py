# approach_two_both_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two


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
	df_registration_subset_block = df_registration.loc[(df_registration['block_name'] == row['block_prediction']) & 
													   (df_registration['Designation'] == row['Designation'])]
	df_registration_subset_district = df_registration.loc[(df_registration['district_name'] == row['district_prediction']) &
														  (df_registration['Designation'] == row['Designation'])]

	# check if the full block, district input is a correct combination
	if check_correct_loc_combination(row) == True:
		print('check_correct_loc_combination True')
		# match on block full name
		if len(row['Name'].split()) == 1:
			print('len == 1')
			# to compare with original full names on blocks
			registration_names_list = list(df_registration_subset_block['Name'].fillna('').unique())
			if registration_names_list:
				# get calc on original name and block original full names
				token_set_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.token_set_ratio))

				# CUTOFF FOR GOING TO DISTRICT MATCH
				cutoff = 75
				if token_set_ratio_calc[1] >= cutoff:
					print('above cutoff of 75')
					# score passes - set matched name on original full name with block match
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc)
					
				else:
					# below block cutoff - check district match
					print('below cutoff of 75')
					# to compare with original full names on districts
					registration_names_list = list(df_registration_subset_district['Name'].fillna('').unique())
					if registration_names_list:
						# get calc on original name and district original full names
						token_set_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.token_set_ratio))
						# SET CUTOFF FOR LOW SCORE OF DISTRICT MATCH HERE - SHOULD THEN LEAVE ALL BLANK
						# AND CALL approach_two.set_empty_match_columns
						# "if token_set_ratio_calc[1] <= new cutoff" is what the line would be

						# score passes - set matched name on original full name with district match
						row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
						row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)
						
					else:
						# registration_names_list is empty on district names
						row = approach_two.set_empty_match_columns(row)
			else:
				# registration_names_list is empty on block names
				row = approach_two.set_empty_match_columns(row)

		else:
			print('len > 1')
			# match on block initials - len > one word
			name_final = approach_two.get_initialed_name(row['Name'])

			# get initialized names of blocks
			df_registration_subset_block['Name_initial'] = \
				df_registration_subset_block['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

			# to compare on initials and original full names
			registration_names_list_init = list(df_registration_subset_block['Name_initial'].fillna('').unique())
			registration_names_list_full = list(df_registration_subset_block['Name'].fillna('').unique())

			if registration_names_list_init:
				token_set_ratio_calc_init = list(process.extractOne(name_final, registration_names_list_init, scorer = fuzz.token_set_ratio))
				token_set_ratio_calc_full = list(process.extractOne(row['Name'], registration_names_list_full, scorer = fuzz.token_set_ratio))
				
				# bool variable to decide on if initial or original full name is better
				init_larger = 0
				if token_set_ratio_calc_init[1] >= token_set_ratio_calc_full[1]:
					token_set_ratio_calc = token_set_ratio_calc_init
					init_larger = 1
				else: 
					token_set_ratio_calc = token_set_ratio_calc_full
				# CUTOFF FOR GOING TO DISTRICT MATCH
				cutoff = 50
				if token_set_ratio_calc[1] >= cutoff:
					print('above cutoff of 50')
					if init_larger == 1:
						row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name_initial'] == token_set_ratio_calc[0], 'Name']).values[0]
					else: 
						row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc)
					
				else:
					# block match is below cutoff, so match on districts -> get larger of initialized and original full names
					print('below cutoff of 50')
					df_registration_subset_district['Name_initial'] = \
						df_registration_subset_district['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)
					# below block cutoff - check district match on both initialized and original full names
					registration_names_list_init = list(df_registration_subset_district['Name_initial'].fillna('').unique())
					registration_names_list_full = list(df_registration_subset_district['Name'].fillna('').unique())

					if registration_names_list_init:
						token_set_ratio_calc_init = list(process.extractOne(name_final, registration_names_list_init, scorer = fuzz.token_set_ratio))
						token_set_ratio_calc_full = list(process.extractOne(row['Name'], registration_names_list_full, scorer = fuzz.token_set_ratio))
						# SET CUTOFF FOR LOW SCORE OF DISTRICT MATCH HERE - SHOULD THEN LEAVE ALL BLANK
						# AND CALL approach_two.set_empty_match_columns
						# if token_set_ratio_calc[1] <= new cutoff is what the line would be

						# bool variable to decide on if initial or original full name is better
						init_larger = 0
						if token_set_ratio_calc_init[1] >= token_set_ratio_calc_full[1]:
							token_set_ratio_calc = token_set_ratio_calc_init
							init_larger = 1
						else: 
							token_set_ratio_calc = token_set_ratio_calc_full

						if init_larger == 1:
							row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc[0], 'Name']).values[0]
						else: 
							row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
						row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)
					else:
						# registration_names_list is empty on district names
						row = approach_two.set_empty_match_columns(row)
			else:
				# registration_names_list is empty on block names
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
				
				token_set_ratio_calc_district = list(process.extractOne(row['Name'], registration_names_list_district, scorer = fuzz.token_set_ratio))				

				# for block prediction
				if registration_names_list_block:
					token_set_ratio_calc_block = list(process.extractOne(row['Name'], registration_names_list_block, scorer = fuzz.token_set_ratio))
				else: 
					token_set_ratio_calc_block = ['', 0]

				if token_set_ratio_calc_district[1] > token_set_ratio_calc_block[1]:
					print('prediction on district match is higher')
					# prediction on district match is higher
					row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc_district[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc_district)

				else:
					print('prediction on block match is higher')
					# match on block prediction has higher score
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc_block[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc_block)
		
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

			registration_names_list_district_init = list(df_registration_subset_district['Name_initial'].fillna('').unique())
			registration_names_list_district_full = list(df_registration_subset_district['Name'].fillna('').unique())
			registration_names_list_block_init = list(df_registration_subset_block['Name_initial'].fillna('').unique())
			registration_names_list_block_full = list(df_registration_subset_block['Name'].fillna('').unique())

			# I think only need to check one of them?
			if registration_names_list_district_init:
				token_set_ratio_calc_district_init = list(process.extractOne(name_final, registration_names_list_district_init, scorer = fuzz.token_set_ratio))
				token_set_ratio_calc_district_full = list(process.extractOne(row['Name'], registration_names_list_district_full, scorer = fuzz.token_set_ratio))
				token_set_ratio_calc_block_init = list(process.extractOne(name_final, registration_names_list_block_init, scorer = fuzz.token_set_ratio))
				token_set_ratio_calc_block_full = list(process.extractOne(row['Name'], registration_names_list_block_full, scorer = fuzz.token_set_ratio))

				# just need to get max of all these
				if token_set_ratio_calc_district_init[1] == max(token_set_ratio_calc_district_init[1], token_set_ratio_calc_district_full[1], token_set_ratio_calc_block_init[1], token_set_ratio_calc_block_full[1]):
					row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc_district_init[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc_district_init)
				elif token_set_ratio_calc_district_full[1] == max(token_set_ratio_calc_district_init[1], token_set_ratio_calc_district_full[1], token_set_ratio_calc_block_init[1], token_set_ratio_calc_block_full[1]):
					row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc_district_full[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc_district_full)
				elif token_set_ratio_calc_block_init[1] == max(token_set_ratio_calc_district_init[1], token_set_ratio_calc_district_full[1], token_set_ratio_calc_block_init[1], token_set_ratio_calc_block_full[1]):
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name_initial'] == token_set_ratio_calc_block_init[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc_block_init)
				elif token_set_ratio_calc_block_full[1] == max(token_set_ratio_calc_district_init[1], token_set_ratio_calc_district_full[1], token_set_ratio_calc_block_init[1], token_set_ratio_calc_block_full[1]):
					row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc_block_full[0], 'Name']).values[0]
					row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc_block_full)
			else:
				row = approach_two.set_empty_match_columns(row)

	print(row)
	return row