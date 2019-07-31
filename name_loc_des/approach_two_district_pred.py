# approach_two_district_pred.py

import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import approach_two #import get_initialed_name, set_empty_match_columns


def process_pred_on_district(row, df_registration):
	
	df_registration_subset_district = df_registration.loc[df_registration['district_name'] == row['district_prediction']]
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
		partial_ratio_calc = list(process.extractOne(name_final, registration_names_list, scorer = fuzz.partial_ratio))
		#print(partial_ratio_calc[0])

		row['matched_name_token_sort'] = (df_registration_subset_district.loc[df_registration_subset_district['Name_initial'] == partial_ratio_calc[0], 'Name']).values[0]
		row['matched_name_confidence'] = partial_ratio_calc[1]
		row['matched_uid'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'Individual_UID']).values[0]
		row['matched_block'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'block_name']).values[0]
		row['matched_district'] = (df_registration_subset_district.loc[df_registration_subset_district['Name'] == row['matched_name_token_sort'], 'district_name']).values[0]
	else:
		row = approach_two.set_empty_match_columns(row)

	#print(row)
	return row