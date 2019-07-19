import pandas as pd
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def standardize_string(s):

	if not isinstance(s, str):
		return None

	table = str.maketrans(dict.fromkeys(string.punctuation))
	s = s.translate(table)
	s = ' '.join(s.split())

	return s.upper()


def check_exact_match(df_networks, df_blocks):

	def set_predictions(row, df_blocks):
		if row['exact_match_blocks'] == 1:
			row['block_prediction'] = row['Location']
			row['block_prediction_score'] = 100

		if row['exact_match_full_name'] == 1:
			row['block_prediction'] = \
				(df_blocks.loc[df_blocks['full_name_std'] == row['Location_std'], 'block_name']).values[0]
			row['block_prediction_score'] = 100

			row['district_prediction'] = \
				(df_blocks.loc[df_blocks['full_name_std'] == row['Location_std'], 'district_name']).values[0]
			row['district_prediction_score'] = 100

		return row


	df_networks['exact_match_blocks'] = \
		df_networks['Location_std'].isin(df_blocks['block_name_std']).astype(int)

	df_networks['exact_match_full_name'] = \
		df_networks['Location_std'].isin(df_blocks['full_name_std']).astype(int)

	df_networks = df_networks.apply(lambda x: set_predictions(x, df_blocks), axis=1)

	# Percentage of exact matches
	print(df_networks['exact_match_blocks'].value_counts(normalize=True).mul(100).astype(str)+'%')
	print(df_networks['exact_match_full_name'].value_counts(normalize=True).mul(100).astype(str)+'%')

	return df_networks



# look if exact match to block_name, and also full_name
def process_exact_matches(df_networks, df_blocks):
	
	# first remove all punctuation, extra whitespace, and set to uppercase
	df_networks['Location_std'] = \
		df_networks['Location'].apply(standardize_string)
	df_blocks['block_name_std'] = \
		df_blocks['block_name'].apply(standardize_string)
	df_blocks['full_name_std'] = \
		df_blocks['full_name'].apply(standardize_string)

	df_networks = check_exact_match(df_networks, df_blocks)
	
	df_networks = df_networks[['Res_uid', 'Name', 'Designation', 
							   'Location', 'Location_std', 
							   'block_prediction', 'block_prediction_score', 
							   'district_prediction', 
							   'district_prediction_score', 
							   'exact_match_blocks', 'exact_match_full_name']]

	return df_networks, df_blocks
