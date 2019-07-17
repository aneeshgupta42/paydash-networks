import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import math

import exact_matches
import one_word_block
import one_word_district
import three_word_case
import two_word_case


def combine_blocks_and_districts(row):

	full_name = row['block_name'] + ', ' + row['district_name']

	return full_name


def process_files():
							
	df_networks = pd.read_excel('../docs/network_mp_apo_responses_from_baseline.xlsx')
	print(df_networks.head(50))

	df_blocks = pd.read_csv('../docs/blocks.csv')
	df_blocks['full_name'] = df_blocks.apply(lambda x: combine_blocks_and_districts(x), axis=1)
	print(df_blocks.head())

	return df_networks, df_blocks



def set_final(x):
	print(x)
	if isinstance(x['final'], str):
		return x['final']
	if math.isnan(x['final']):
		print('in if')
		return x['mp_apo_block']
	if x['final'] == None:
		print('in if2')
		return x['mp_apo_block']
	if not x['final']:
		print('in if 3')
		return x['mp_apo_block']
	return x['final']
#.loc[df_networks_final['final'] == np.nan, ['final']] = df_networks_final['mp_apo_block']

def hit_cases(df_networks, df_blocks):
	df_networks = df_networks.iloc[:10]

	# Still have og df_networks and df_blocks
	df_networks = df_networks[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block']]

	df_networks_std, df_blocks_std = exact_matches.exact_match_1(df_networks, df_blocks)

	df_networks_2 = one_word_block.one_word_block_2(df_networks_std, df_blocks_std)
	#print('one word')
	#print(df_networks_2.head(50))

	df_networks_3 = one_word_district.one_word_district_3(df_networks_std, df_networks_2, df_blocks_std)

	df_three_word = three_word_case.three_word_network(df_networks_std, df_blocks_std)
	
	df_multi_word = two_word_case.multi_word_both(df_networks_std, df_blocks_std)
	
	df_with_matched = df_networks_std.loc[(df_networks_std['exact_match_blocks'] == 1) | 
										  (df_networks_std['exact_match_full_name'] == 1)]
	print(df_with_matched)										  
	df_networks_final = pd.concat([df_with_matched, df_networks_2, df_three_word, df_multi_word], sort=True)
	print(df_networks_final)
	#df_#networks_final.sort_index(inplace=True, axis=0)
	df_networks_final['final'] = df_networks_final.apply(lambda x: set_final(x), axis=1)
	print(df_networks_final)

	return df_networks_final



def main():
	pd.options.mode.chained_assignment = None  # default='warn'

	df_networks, df_blocks = process_files()


	df_networks_final = hit_cases(df_networks, df_blocks)

	#df_networks_final.to_csv('match_3.csv')

#	with pd.ExcelWriter('match_locations_predictions_2.xlsx') as writer:  # doctest: +SKIP
#		df_networks_std.to_excel(writer, sheet_name='Exact_Matches')
#		df_networks_2.to_excel(writer, sheet_name='One_word_block')
#		df_networks_3.to_excel(writer, sheet_name='One_word_district')
#		df_three_word.to_excel(writer, sheet_name='Three_word_input')
#		df_multi_word.to_excel(writer, sheet_name='two_word_input')



if __name__ == '__main__':
	main()