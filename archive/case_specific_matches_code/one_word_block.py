import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import lev_alg

def greater_of_rat_or_set(x):

	if x['ratio'][1] >= x['token_set_ratio'][1]:
		return x['ratio']
	return x['token_set_ratio']

# first get only one word
# then match to block_name
def one_word_block_2(df_networks, df_blocks):
	# get length of word
	#len(s.split()) == 1
	#print(df_networks)
	df_networks_one_word = df_networks.loc[(df_networks['mp_apo_block'].str.split().str.len() == 1) &
										   (df_networks['exact_match_blocks'] == 0) &
										   (df_networks['exact_match_full_name'] == 0) &
										    (~df_networks['mp_apo_block'].isin(list(df_blocks['district_name'])))]
										  	
	#print(df_networks_one_word)

	location_list = list(df_blocks['block_name'])

	df_networks_one_word = lev_alg.get_levenshtein_matches(df_networks_one_word, df_blocks, location_list)
	#print()
	#print(df_networks_one_word.head(50))

	df_networks_one_word['final'] = df_networks_one_word.apply(lambda x: greater_of_rat_or_set(x), axis=1)


	return df_networks_one_word[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block', 'final']]
