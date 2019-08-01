# approach_two_block_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two


def process_pred_on_block(row, df_registration):

	# get block match subset
	df_registration_subset_block = df_registration.loc[(df_registration['block_name'] == row['block_prediction']) &
														(df_registration['Designation'] == row['Designation'])]
	
	# with one word, compare to full names
	if len(row['Name'].split()) == 1:
		# set both name_final and name_initial column to the original names
		registration_names_list = list(df_registration_subset_block['Name'].fillna('').unique())

		if registration_names_list:
			token_set_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.token_set_ratio))
			row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc[0], 'Name']).values[0]
			row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc)
		else:
			row = approach_two.set_empty_match_columns(row)

	else:
		# with > one word, compare to both initials and original full names
		name_final = approach_two.get_initialed_name(row['Name'])

		df_registration_subset_block['Name_initial'] = \
			df_registration_subset_block['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

		registration_names_list_init = list(df_registration_subset_block['Name_initial'].fillna('').unique())
		registration_names_list_full = list(df_registration_subset_block['Name'].fillna('').unique())

		if registration_names_list_init:
			token_set_ratio_calc_init = list(process.extractOne(name_final, registration_names_list_init, scorer = fuzz.token_set_ratio))
			token_set_ratio_calc_full = list(process.extractOne(row['Name'], registration_names_list_full, scorer = fuzz.token_set_ratio))

			if token_set_ratio_calc_init[1] >= token_set_ratio_calc_full[1]:
				row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name_initial'] == token_set_ratio_calc_init[0], 'Name']).values[0]
				row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc_init)
			else:
				row['matched_name_token_sort'] = (df_registration_subset_block.loc[df_registration_subset_block['Name'] == token_set_ratio_calc_full[0], 'Name']).values[0]
				row = approach_two.set_match_data(row, df_registration_subset_block, token_set_ratio_calc_full)
		else:
			row = approach_two.set_empty_match_columns(row)

	#print(row)
	return row