import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import math


def check_if_processed(row):

	# a number of these are redundant, but just covered for now to be sure
	if not isinstance(row['Location'], str) or not row['Location']:
		return True

	if row['block_prediction'] or row['district_prediction']:
		return True

	if row['exact_match_blocks'] == 1 or row['exact_match_districts'] == 1 or row['exact_match_full_name'] == 1:
		return True

	if "," in row['Location'] or "-" in row['Location'] or ")" in row['Location']: 
		return True

	return False


def handle_one_word(row, df_blocks_std):
	
	if check_if_processed(row) == True:
		return row

	if len(row['Location'].split()) != 1:
		return row

	# block prediction
	location_list = list(df_blocks_std['block_name'])

	ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.ratio))

	token_set_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_set_ratio))

	if ratio_calc[1] >= token_set_ratio_calc[1]:
		final_block_pred = ratio_calc[0]
		final_block_pred_score = ratio_calc[1]
	else:
		final_block_pred = token_set_ratio_calc[0]
		final_block_pred_score = token_set_ratio_calc[1]

	# district prediction
	location_list = list(df_blocks_std['district_name'])

	ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.ratio))

	token_set_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.token_set_ratio))

	if ratio_calc[1] >= token_set_ratio_calc[1]:
		final_district_pred = ratio_calc[0]
		final_district_pred_score = ratio_calc[1]
	else:
		final_district_pred = token_set_ratio_calc[0]
		final_district_pred_score = token_set_ratio_calc[1]


	if final_block_pred_score > final_district_pred_score:
		row['block_prediction'] = final_block_pred
		row['block_prediction_score'] = final_block_pred_score
	elif final_district_pred_score > final_block_pred_score:
		row['district_prediction'] = final_district_pred
		row['district_prediction_score'] = final_district_pred_score
	else:
		# if name scores match - for block/district same names
		row['block_prediction'] = final_block_pred
		row['block_prediction_score'] = final_block_pred_score
		row['district_prediction'] = final_district_pred
		row['district_prediction_score'] = final_district_pred_score

	row['num_words'] = 1

	return row


def handle_two_words(row, df_blocks_std):

	if check_if_processed(row):
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

	row['num_words'] = 2

	return row


def handle_multi_word(row, df_blocks_std):

	if check_if_processed(row):
		return row

	if len(row['Location'].split()) <= 2:
		return row

	# check if Janpad Panchayat is in location, if so -> remove and get block prediction
	if "JANPAD PANCHAYAT" in row['Location']:
		row['Location'] = row['Location'].replace("JANPAD PANCHAYAT", "")

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
		row['num_words'] = 3
		return row

	# block prediction
	location_list = list(df_blocks_std['full_name'])

	ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.ratio))

	predicted_block = df_blocks_std.loc[df_blocks_std['full_name'] == ratio_calc[0], 'block_name']
	row['block_prediction'] = predicted_block.values[0]
	row['block_prediction_score'] = ratio_calc[1]

	# district prediction
	partial_ratio_calc = list(process.extractOne(str(row['Location']), location_list, scorer = fuzz.partial_ratio))

	predicted_district = df_blocks_std.loc[df_blocks_std['full_name'] == partial_ratio_calc[0], 'district_name']
	row['district_prediction'] = predicted_district.values[0]
	row['district_prediction_score'] = partial_ratio_calc[1]


	row['num_words'] = 3
	return row


def handle_cases(df_networks_std, df_blocks_std):
	df_networks_std['num_words'] = 0
	# one word
	df_networks_std = df_networks_std.apply(lambda x: handle_one_word(x, df_blocks_std), axis=1)

	# two words
	df_networks_std = df_networks_std.apply(lambda x: handle_two_words(x, df_blocks_std), axis=1)

	# more than two words
	df_networks_std = df_networks_std.apply(lambda x: handle_multi_word(x, df_blocks_std), axis=1)
	

	print('one word')
	print(df_networks_std.loc[df_networks_std['num_words'] == 1])
	print('two words')
	print(df_networks_std.loc[df_networks_std['num_words'] == 2])
	
	print('more than two words')
	print(df_networks_std.loc[df_networks_std['num_words'] == 3])

	df_networks_std.drop(columns=['num_words'], inplace=True)
	return df_networks_std
	
