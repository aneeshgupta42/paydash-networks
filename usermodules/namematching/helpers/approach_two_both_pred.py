# approach_two_both_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import namematching.helpers.approach_two

# this checks the block, district prediction combination
# in the current mp_blocks doc
def check_correct_loc_combination(row):

	df_mp_blocks = pd.read_csv('../docs/mp_blocks_2017-2018.csv')

	# check if block, district combination is empty
	# need to strip because it wasn't covering that extra space in KATNI
	df_mp_blocks = df_mp_blocks.loc[(df_mp_blocks['block_name'].str.strip() == row['block_prediction'].strip()) &
									(df_mp_blocks['district_name'].str.strip() == row['district_prediction'].strip())]
	if df_mp_blocks.empty:
		return False

	return True


def handle_block_district_correct_one_word(row, df_registration_subset_block, df_registration_subset_district):
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

				# set matched name on original full name with district match
				row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
				row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)

			else:
				# registration_names_list is empty on district names
				row = approach_two.set_empty_match_columns(row)
	else:
		# registration_names_list is empty on block names
		row = approach_two.set_empty_match_columns(row)

	return row


def get_token_set_ratio_calc(row, df_registration_subset):
	name_final = approach_two.get_initialed_name(row['Name'])
#	# get initialized names of blocks
	df_registration_subset['Name_initial'] = \
		df_registration_subset['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

	# to compare on initials and original full names
	registration_names_list_init = list(df_registration_subset['Name_initial'].fillna('').unique())
	registration_names_list_full = list(df_registration_subset['Name'].fillna('').unique())

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

	else:
		token_set_ratio_calc = None
		init_larger = 0

	return token_set_ratio_calc, df_registration_subset, init_larger



def handle_block_district_correct_multi_word(row, df_registration_subset_block, df_registration_subset_district):

	token_set_ratio_calc, df_registration_subset_block, init_larger = get_token_set_ratio_calc(row, df_registration_subset_block)

	# registration_names_list is empty on block names
	if not token_set_ratio_calc:
		row = approach_two.set_empty_match_columns(row)
		return row

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

		token_set_ratio_calc, df_registration_subset_district, init_larger = get_token_set_ratio_calc(row, df_registration_subset_district)
		# registration_names_list is empty on district names
		if not token_set_ratio_calc:
			row = approach_two.set_empty_match_columns(row)
			return row

		if init_larger == 1:
			row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc[0], 'Name']).values[0]
		else:
			row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc[0], 'Name']).values[0]

		row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)

	return row



def process_pred_on_both(row, df_registration):
	print('in process_pred_on_both')
	# get matching block and district subsets
	df_registration_subset_block = df_registration.loc[(df_registration['block_name'] == row['block_prediction'])]

	df_registration_subset_district = df_registration.loc[(df_registration['district_name'] == row['district_prediction'])]

	# Grab a further subset by designation if it exists in row
	if isinstance(row['Designation'], str):
		df_registration_subset_block = df_registration_subset_block.loc[(df_registration_subset_block['Designation'] == row['Designation'])]
		df_registration_subset_district = df_registration_subset_district.loc[(df_registration_subset_district['Designation'] == row['Designation'])]

	# check if the full block, district input is a correct combination
	if check_correct_loc_combination(row) == True:
		print('check_correct_loc_combination True')
		# match on block full name
		if len(row['Name'].split()) == 1:
			row = handle_block_district_correct_one_word(row, df_registration_subset_block, df_registration_subset_district)

		else:
			print('len > 1')
			# match on block initials - len > one word
			row = handle_block_district_correct_multi_word(row, df_registration_subset_block, df_registration_subset_district)
	else:
		# block, district combination incorrect
		# compare matches on block and on district and take higher of the two
		print('check_correct_loc_combination False')
		# first if response is one word
		if len(row['Name'].split()) == 1:
			print('len == 1')
			registration_names_list_district = list(df_registration_subset_district['Name'].fillna('').unique())
			registration_names_list_block = list(df_registration_subset_block['Name'].fillna('').unique())

			# TODO: NEED TO CHECK DISTRICT AND BLOCK AT SAME TIME
			# THIS WILL LEAVE AND SET TO EMPTY IF ONLY DISTRICT MATCHING EXISTS,
			# HOWEVER THERE IS ALSO THE POSSIBILITY THAT JUST BLOCK MATCHES,
			# SO IT WON'T CAPTURE THAT MATCH
			# TO CHANGE: CAN JUST REMOVE THIS IF AND ADD IF REGISTRATION_NAMES_LIST_DISTRICT
			# AT SAME LEVEL OF registration_names_list_block AND THEN SET TO SAME [" ", 0] IF NOT
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
				print(row)
				#print()

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

			# TODO: NEED TO CHECK DISTRICT AND BLOCK AT SAME TIME
			# THIS WILL LEAVE AND SET TO EMPTY IF ONLY DISTRICT MATCHING EXISTS,
			# HOWEVER THERE IS ALSO THE POSSIBILITY THAT JUST BLOCK MATCHES,
			# SO IT WON'T CAPTURE THAT MATCH
			# TO CHANGE: CAN JUST REMOVE THIS IF AND ADD IF REGISTRATION_NAMES_LIST_DISTRICT
			# AT SAME LEVEL OF registration_names_list_block AND THEN SET TO SAME [" ", 0] IF NOT
			if registration_names_list_district_init:
				token_set_ratio_calc_district_init = list(process.extractOne(name_final, registration_names_list_district_init, scorer = fuzz.token_set_ratio))
				token_set_ratio_calc_district_full = list(process.extractOne(row['Name'], registration_names_list_district_full, scorer = fuzz.token_set_ratio))

				if registration_names_list_block_init:
					token_set_ratio_calc_block_init = list(process.extractOne(name_final, registration_names_list_block_init, scorer = fuzz.token_set_ratio))
					token_set_ratio_calc_block_full = list(process.extractOne(row['Name'], registration_names_list_block_full, scorer = fuzz.token_set_ratio))
				else:
					token_set_ratio_calc_block_init = ['', 0]
					token_set_ratio_calc_block_full = ['', 0]

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

#	print(row)
	return row
