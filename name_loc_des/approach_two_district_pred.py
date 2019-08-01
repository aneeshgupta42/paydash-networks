# approach_two_district_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two #import get_initialed_name, set_empty_match_columns


def process_pred_on_district(row, df_registration):
	
	df_registration_subset_district = df_registration.loc[(df_registration['district_name'] == row['district_prediction']) &
														  (df_registration['Designation'] == row['Designation'])]
	# one word compare to full names
	if len(row['Name'].split()) == 1:
		registration_names_list = list(df_registration_subset_district['Name'].fillna('').unique())
		if registration_names_list:
			token_set_ratio_calc = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.token_set_ratio))
			row['matched_name_token_sort'] = list(process.extractOne(row['Name'], registration_names_list, scorer = fuzz.token_set_ratio))
			row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)
		else:
			row = approach_two.set_empty_match_columns(row)

	else:
		# with > one word, compare to both initials and original full names
		name_final = approach_two.get_initialed_name(row['Name'])

		df_registration_subset_district['Name_initial'] = \
			df_registration_subset_district['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

		registration_names_list_init = list(df_registration_subset_district['Name_initial'].fillna('').unique())
		registration_names_list_full = list(df_registration_subset_district['Name'].fillna('').unique())

		if registration_names_list_init:
			token_set_ratio_calc_init = list(process.extractOne(name_final, registration_names_list_init, scorer = fuzz.token_set_ratio))
			token_set_ratio_calc_full = list(process.extractOne(row['Name'], registration_names_list_full, scorer = fuzz.token_set_ratio))

			if token_set_ratio_calc_init[1] >= token_set_ratio_calc_full[1]:
				row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc_init[0], 'Name']).values[0]
				row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc_init)
			else:
				row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == token_set_ratio_calc_full[0], 'Name']).values[0]
				row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc_full)
		else:
			row = approach_two.set_empty_match_columns(row)

	#print(row)
	return row