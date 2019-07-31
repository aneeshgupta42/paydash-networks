# approach_two_district_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two #import get_initialed_name, set_empty_match_columns


def process_pred_on_district(row, df_registration):
	
	df_registration_subset_district = df_registration.loc[(df_registration['district_name'] == row['district_prediction']) &
														  (df_registration['Designation'] == row['Designation'])]
	# one word compare to full names, > one word compare to initials
	if len(row['Name'].split()) == 1:
		name_final = row['Name']
		df_registration_subset_district['Name_initial'] = df_registration_subset_district['Name']
		registration_names_list = list(df_registration_subset_district['Name'].fillna('').unique())
	else:
		name_final = approach_two.get_initialed_name(row['Name'])

		df_registration_subset_district['Name_initial'] = \
			df_registration_subset_district['Name'].apply(lambda x: ' '.join([name[0] for name in x.split()[:-1]]) + ' ' + x.split()[-1] if '.' not in x else x)

		registration_names_list = list(df_registration_subset_district['Name_initial'].fillna('').unique())

	if registration_names_list:
		token_set_ratio_calc = list(process.extractOne(name_final, registration_names_list, scorer = fuzz.token_set_ratio))

		row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == token_set_ratio_calc[0], 'Name']).values[0]
		row = approach_two.set_match_data(row, df_registration_subset_district, token_set_ratio_calc)
	else:
		row = approach_two.set_empty_match_columns(row)

	#print(row)
	return row