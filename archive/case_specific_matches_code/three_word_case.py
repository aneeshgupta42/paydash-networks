import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import lev_alg


def three_word_network(df_networks, df_blocks):
	print('more than two')
	df_networks = df_networks.loc[(df_networks['mp_apo_block'].str.split().str.len() > 2) &
								  (df_networks['exact_match_blocks'] == 0) &
								  (df_networks['exact_match_full_name'] == 0)]
#	print(df_networks.head(50))

	location_list = list(df_blocks['full_name'].loc[(df_blocks['full_name'].str.split().str.len() > 1)])
	df_networks_multi = lev_alg.get_levenshtein_matches(df_networks, df_blocks, location_list)
	
	df_networks_multi.rename(index=str, columns={"token_sort_ratio": "final"}, inplace=True)
	df_networks_multi = df_networks_multi[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block', 'final']]
	print(df_networks_multi.head(50))


	return df_networks_multi