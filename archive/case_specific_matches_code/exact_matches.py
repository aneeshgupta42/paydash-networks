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

	#Df1.name.isin(Df2.IDs).astype(int)
	df_networks['exact_match_blocks'] = \
		df_networks['mp_apo_block'].isin(df_blocks['block_name']).astype(int)

	df_networks['exact_match_full_name'] = \
		df_networks['mp_apo_block'].isin(df_blocks['full_name']).astype(int)

	#print(df_networks['exact_match_blocks'].value_counts(normalize=True).mul(100).astype(str)+'%')
	#print(df_networks['exact_match_full_name'].value_counts(normalize=True).mul(100).astype(str)+'%')

	return df_networks



# look if exact match to block_name, and also full_name
def exact_match_1(df_networks, df_blocks):
	
	# first remove all punctuation, extra whitespace, and set lowercase
	df_networks['mp_apo_block'] = df_networks['mp_apo_block'].apply(standardize_string)
	df_blocks['block_name'] = df_blocks['block_name'].apply(standardize_string)
	df_blocks['full_name'] = df_blocks['full_name'].apply(standardize_string)

	#print(df_networks['mp_apo_block'])
	#print(df_blocks['block_name'])
	#print(df_blocks['full_name'])

	df_networks = check_exact_match(df_networks, df_blocks)
	#print(df_networks)

	return df_networks, df_blocks