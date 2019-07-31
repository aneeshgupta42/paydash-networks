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
			pd.read_csv('../docs/block_level_responses_all.csv')

	# set all Locations from Nan to None
	df_networks['Location'] = \
			df_networks['Location'].replace({pd.np.nan: None})

	df_blocks = pd.read_csv('../docs/mp_blocks_2017-2018.csv')

	# Only MP
	df_blocks = df_blocks.loc[df_blocks['state_code'] == 17]

	df_blocks['full_name'] = \
			df_blocks.apply(lambda x: combine_blocks_and_districts(x), axis=1)

	return df_networks, df_blocks


def handle_all_cases(row):

	if not isinstance(row['Location'], str) or not row['Location']:
		return row

	all_list = ['ALL', 'All', 'all']
	if not any(x in row['Location'] for x in all_list):
		return row

	row['block_prediction'] = None
	row['block_prediction_score'] = None
	row['district_prediction'] = None
	row['district_prediction_score'] = None

	return row


def hit_cases(df_networks, df_blocks):
	
	#df_networks = df_networks.iloc[:5]

	df_networks = df_networks[['Res_uid', 'Name', 'Designation', 'Location']]

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
	

	df_networks_std = df_networks_std.apply(lambda x: handle_all_cases(x), axis=1)
		
	print('after all')
	print(df_networks_std)

	return df_networks_std



def main():

	pd.options.mode.chained_assignment = None  # default='warn'

	df_networks, df_blocks = process_files()
	print(df_blocks.head(100))

	df_networks_final = hit_cases(df_networks, df_blocks)

	df_networks_final.drop(columns=['Location_std'], inplace=True)
	print(df_networks_final.head(50))
	df_networks_final.to_csv('./output/match_31072019.csv', index=False)


if __name__ == '__main__':
	main()
