import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def get_levenshtein_matches(df_networks, df_blocks, location_list):

	def get_lev_ratio(network_block, location_list, ratio_type):

		if not isinstance(network_block, str):
			return None

		best_guess = list(process.extractOne(str(network_block), location_list, scorer = ratio_type))

		#best_guess[0] = best_guess[0].split(' ', 1)[0]
		return best_guess[0]


	lev_ratio_list = [fuzz.ratio, fuzz.partial_ratio, fuzz.token_sort_ratio, fuzz.token_set_ratio]
	
	df_networks['ratio'] = \
		df_networks['mp_apo_block'].apply(lambda x: get_lev_ratio(x, location_list, lev_ratio_list[0]))

	df_networks['partial_ratio'] = \
		df_networks['mp_apo_block'].apply(lambda x: get_lev_ratio(x, location_list, lev_ratio_list[1]))

	df_networks['token_sort_ratio'] = \
		df_networks['mp_apo_block'].apply(lambda x: get_lev_ratio(x, location_list, lev_ratio_list[2]))	

	df_networks['token_set_ratio'] = \
		df_networks['mp_apo_block'].apply(lambda x: get_lev_ratio(x, location_list, lev_ratio_list[3]))


	#print(df_networks.head(50))

	return df_networks
