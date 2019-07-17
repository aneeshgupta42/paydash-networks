import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import lev_alg
import one_word_block

def one_word_district_3(df_networks, df_networks_2, df_blocks):
	#print(list(df_networks_2['final'].map(lambda x: x[0])))
	df_networks_distr = df_networks.loc[(df_networks['mp_apo_block'].str.split().str.len() == 1) &
										~df_networks['mp_apo_block'].isin(list(df_networks_2['final'].map(lambda x: x[0]))) &
										   (df_networks['exact_match_blocks'] == 0) &
										   (df_networks['exact_match_full_name'] == 0)]
	
	location_list = list(df_blocks['district_name'])
	df_networks_distr = lev_alg.get_levenshtein_matches(df_networks_distr, df_blocks, location_list)
	#print(df_networks_distr)

	df_networks_distr['final'] = df_networks_distr.apply(lambda x: one_word_block.greater_of_rat_or_set(x), axis=1)

	return df_networks_distr[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block', 'final']]
