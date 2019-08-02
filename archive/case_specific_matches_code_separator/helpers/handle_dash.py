import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


def match_with_dash(df_networks_std, df_blocks_std):

	def remove_whitespace(s):

		s = s.replace(" -", "-")
		s = s.replace("  -", "-")

		s = s.replace(" - ", "-")
		s = s.replace("  -  ", "-")
		s = s.replace(" -  ", "-")
		s = s.replace("  - ", "-")

		s = s.replace("- ", "-")
		s = s.replace("-  ", "-")
		return s

	# return index of first letter in dashed word
	# NOTE: Assume only one dash
	def get_AM_word_index(s):

		for word in s.split():
			if 'AGAR-MALWA' in word:
				return s.index(word)


	def handle_dashes(row, df_blocks_std):

		if not isinstance(row['Location'], str):
			return row

		if row['block_prediction'] or row['district_prediction']:
			return row

		if row['exact_match_blocks'] == 1 or row['exact_match_full_name'] == 1:
			return row

		if "," in row['Location'] or ")" in row['Location']:
			return row

		if "-" not in row['Location']:
			return row

		# No punctuation, with dash
		row['Location'] = remove_whitespace(row['Location'])

		# Check AGAR-MALWA - 67 is best cutoff
		if "AGAR-MALWA" in row['Location'] or fuzz.ratio("AGAR-MALWA", row['Location']) > 67:

			# Just AGAR-MALWA
			if len(row['Location'].split()) == 1:
				row['district_prediction'] = 'AGAR-MALWA'
				row['district_prediction_score'] = 100
			else:
				# Includes block
				blocks_list = df_block_std['block_name'].unique().tolist()
				row['district_prediction'] = 'AGAR-MALWA'
				row['district_prediction_score'] = 100
				# if A-M at beginning
				if get_AM_word_index(row['Location']) == 0:

					ratio_calc = list(process.extractOne(str(row['Location'].split()[1]), blocks_list, scorer = fuzz.ratio))

					row['block_prediction'] = ratio_calc[0]
					row['block_prediction_score'] = ratio_calc[1]

				# if A-M at end
				else:

					ratio_calc = list(process.extractOne(str(row['Location'].split()[0]), blocks_list, scorer = fuzz.ratio))

					row['block_prediction'] = ratio_calc[0]
					row['block_prediction_score'] = ratio_calc[1]
		else:
			# Incorrect spellings of AGAR-MALWA solved with ration score above
			# Assume "block-district"

			split_block_name_list = row['Location'].split('-')

			# block prediction
			location_list = list(df_blocks_std['block_name'])

			ratio_calc = list(process.extractOne(split_block_name_list[0], location_list, scorer = fuzz.ratio))

			row['block_prediction'] = ratio_calc[0]
			row['block_prediction_score'] = ratio_calc[1]

			# district prediction
			location_list = list(df_blocks_std['district_name'])

			ratio_calc = list(process.extractOne(split_block_name_list[1], location_list, scorer = fuzz.ratio))

			row['district_prediction'] = ratio_calc[0]
			row['district_prediction_score'] = ratio_calc[1]

		return row

	df_networks_std = df_networks_std.apply(lambda x: handle_dashes(x, df_blocks_std), axis=1)

	return df_networks_std
