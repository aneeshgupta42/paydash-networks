import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import math

from helpers import exact_matches
from helpers import separator_present
from helpers import handle_dash
from helpers import handle_no_punc


def combine_blocks_and_districts(row):

	full_name = row['block_name'] + ', ' + row['district_name']

	return full_name


def process_files():

	df_networks = \
			pd.read_excel('../docs/network_mp_apo_responses_from_baseline.xlsx')

	# set all mp_apo_blocks from Nan to None
	df_networks['mp_apo_block'] = \
			df_networks['mp_apo_block'].replace({pd.np.nan: None})

	df_blocks = pd.read_csv('../docs/mp_blocks_2017-2018.csv')

	# Only MP
	df_blocks = df_blocks.loc[df_blocks['state_code'] == 17]

	df_blocks['full_name'] = \
			df_blocks.apply(lambda x: combine_blocks_and_districts(x), axis=1)

	return df_networks, df_blocks


def hit_cases(df_networks, df_blocks):
	
	#df_networks = df_networks.iloc[:400]

	df_networks = df_networks[['individual_uid', 'district', 'samerank', 'mp_apo_name', 'mp_apo_block']]

	df_networks['block_prediction'] = None
	df_networks['block_prediction_score'] = None
	df_networks['district_prediction'] = None
	df_networks['district_prediction_score'] = None

	df_networks_std, df_blocks_std = \
				exact_matches.process_exact_matches(df_networks, df_blocks)

	df_networks_std = separator_present.make_predictions(df_networks_std)

	df_networks_std = \
				handle_dash.match_with_dash(df_networks_std, df_blocks_std)

	df_networks_std = \
				handle_no_punc.handle_cases(df_networks_std, df_blocks_std)
	print('after all')
	print(df_networks_std)

	return df_networks_std



def main():

	pd.options.mode.chained_assignment = None  # default='warn'

	df_networks, df_blocks = process_files()

	df_networks_final = hit_cases(df_networks, df_blocks)

	df_networks_final.drop(columns=['mp_apo_block_std'], inplace=True)

	df_networks_final.to_csv('match_10072019.csv', index=False)


if __name__ == '__main__':
	main()
