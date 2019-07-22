import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import math

def handle_one_word(row, df_blocks_std):
	
	if not isinstance(row['Location'], str) or not row['Location']:
		return row

	if row['block_prediction'] or row['district_prediction']:
			return row

	if row['exact_match_blocks'] == 1 or row['exact_match_full_name'] == 1:
		return row

	if "," in row['Location'] or "-" in row['Location'] or ")" in row['Location']: 
		return row

	if len(row['Location'].split()) != 1:
		return row


	# block prediction
	location_list = list(df_blocks_std['block_name'])

	ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.ratio))

	token_set_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_set_ratio))

	if ratio_calc[1] >= token_set_ratio_calc[1]:
		row['block_prediction'] = ratio_calc[0]
		row['block_prediction_score'] = ratio_calc[1]
	else:
		row['block_prediction'] = token_set_ratio_calc[0]
		row['block_prediction_score'] = token_set_ratio_calc[1]

	# district prediction
	location_list = list(df_blocks_std['full_name'])

	ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.ratio))

	token_set_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_set_ratio))

	if ratio_calc[1] >= token_set_ratio_calc[1]:
		predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == ratio_calc[0], 'district_name']
		row['district_prediction'] = predicted_district.values[0]
		row['district_prediction_score'] = ratio_calc[1]
	else:
		predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == token_set_ratio_calc[0], 'district_name']
		row['district_prediction'] = predicted_district.values[0]
		row['district_prediction_score'] = token_set_ratio_calc[1]

	return row


def handle_two_words(row, df_blocks_std):

	if not isinstance(row['Location'], str) or not row['Location']:
		return row

	if row['block_prediction'] or row['district_prediction']:
		return row

	if row['exact_match_blocks'] == 1 or row['exact_match_full_name'] == 1:
		return row

	if "," in row['Location'] or "-" in row['Location'] or ")" in row['Location']:
		return row

	if len(row['Location'].split()) != 2:
		return row
	
	# block prediction
	location_list = list(df_blocks_std['full_name'])

	partial_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.partial_ratio))
	token_sort_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_sort_ratio))

	if partial_ratio_calc[1] >= token_sort_ratio_calc[1]:
		predicted_row = df_blocks_std.loc[df_blocks_std['full_name'] == partial_ratio_calc[0], 'block_name']
		row['block_prediction'] = predicted_row.values[0]
		row['block_prediction_score'] = partial_ratio_calc[1]
	else:
		predicted_row = df_blocks_std.loc[df_blocks_std['full_name'] == token_sort_ratio_calc[0], 'block_name']
		row['block_prediction'] = predicted_row.values[0]
		row['block_prediction_score'] = token_sort_ratio_calc[1]

	# district prediction
	partial_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.partial_ratio))
	token_sort_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_sort_ratio))

	if partial_ratio_calc[1] >= token_sort_ratio_calc[1]:
		predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == partial_ratio_calc[0], 'district_name']
		row['district_prediction'] = predicted_district.values[0]
		row['district_prediction_score'] = partial_ratio_calc[1]
	else:
		predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == token_sort_ratio_calc[0], 'district_name']
		row['district_prediction'] = predicted_district.values[0]
		row['district_prediction_score'] = token_sort_ratio_calc[1]

	return row


def handle_multi_word(row, df_blocks_std):

	if not isinstance(row['Location'], str) or not row['Location']:
		return row

	if row['block_prediction'] or row['district_prediction']:
		return row	

	if row['exact_match_blocks'] == 1 or row['exact_match_full_name'] == 1:
		return row

	if "," in row['Location'] or "-" in row['Location'] or ")" in row['Location']:
		return row

	if len(row['Location'].split()) <= 2:
		return row

	# block prediction
	location_list = list(df_blocks_std['block_name'])

	token_sort_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_sort_ratio))
	
	row['block_prediction'] = token_sort_ratio_calc[0]
	row['block_prediction_score'] = token_sort_ratio_calc[1]

	# district prediction
	location_list = list(df_blocks_std['full_name'])

	partial_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.partial_ratio))

	predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == partial_ratio_calc[0], 'district_name']
	row['district_prediction'] = predicted_district.values[0]
	row['district_prediction_score'] = partial_ratio_calc[1]

	return row


def handle_cases(df_networks_std, df_blocks_std):
	
	# one word
	df_networks_std = df_networks_std.apply(lambda x: handle_one_word(x, df_blocks_std), axis=1)

	# two words
	df_networks_std = df_networks_std.apply(lambda x: handle_two_words(x, df_blocks_std), axis=1)

	# more than two words
	df_networks_std = df_networks_std.apply(lambda x: handle_multi_word(x, df_blocks_std), axis=1)

	return df_networks_std
	
