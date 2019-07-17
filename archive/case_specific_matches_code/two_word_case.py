import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import lev_alg


def multi_word_both(df_networks, df_blocks):

	print('two')
	df_networks = df_networks.loc[(df_networks['mp_apo_block'].str.split().str.len() == 2) &
								  (df_networks['exact_match_blocks'] == 0) &
								  (df_networks['exact_match_full_name'] == 0)]
	print(df_networks.head(50))

	location_list = list(df_blocks['full_name'])
	df_networks = lev_alg.get_levenshtein_matches(df_networks, df_blocks, location_list)
	
	df_networks.rename(index=str, columns={"token_sort_ratio": "final"}, inplace=True)
	df_networks = df_networks[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block', 'final']]
	print(df_networks.head(50))
	return df_networks