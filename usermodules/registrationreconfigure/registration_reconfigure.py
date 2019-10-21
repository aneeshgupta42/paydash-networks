import pandas as pd
import re

#This code will be needed to adapted for different registration sheets for different states
#At the time of writing, the team only had access to the MP registration sheet
#This can basically be thought of as a standalone script for all purposes

#cleaning the name of titles such as Mr. Shri. Dr. etc etc
#to ensure consistency b/w response and mastersheet
def clean_title(x):

	x = x.strip()
	list = ['\AMr.', '\ASH', '\AKU ', '\AKU.', '\ADR ', '\ADR.', '\ADr.', '\AMISS ', '\AMrs.', '\AMrs ', '\ASHRI ', ' JI\Z', ' Ji\Z', '\ASUSHRI ', '\ASMT ', '\ASmt ', '\ASMT.','\AMs.', '\AMS.', '\ASir ', 'Sir\Z']
	for k in list:
		if(re.search(k,x)):
			k = k.replace('\A', '')
			k = k.replace('\Z', '')
			x = x.replace(k, '')
	x = x.strip()

	return x

def process_file():

	df = pd.read_excel('./docs/20171113_MP_Transfers_Registration_Combined_April end.xlsx', usecols='A:JK')
	print(df.head())
	#print(df['Unnamed: 7'].head())
	df['Unnamed: 3'] = df['Unnamed: 3'].fillna('')
	df['Unnamed: 4'] = df['Unnamed: 4'].fillna('')

	df_blocks = df.loc[(df['Unnamed: 3']!='') & (df['Unnamed: 4']!='')]
	print(df_blocks.head())
	df_districts = df.loc[(df['Unnamed: 3']=='') & (df['Unnamed: 4']=='')]

	# Drop initial general location info
	df_blocks.drop(columns=['Unnamed: 0', 'Unnamed: 2',
					 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6'], inplace=True)

	df_districts.drop(columns=['Unnamed: 0', 'Unnamed: 2',
					 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6'], inplace=True)

	df_blocks.drop(df_blocks.index[0], inplace=True)


	return df_blocks, df_districts


def reformat_months(df, dftype):

	df = df.loc[df['Individual_UID'].notna()]

	df = df[['Name_{}'.format(dftype), 'Individual_UID', 'Designation', 'block_name_{}'.format(dftype.lower()), 'district_name_{}'.format(dftype.lower())]]

	df['Designation_{}'.format(dftype)] = df['Designation'].apply(lambda x: "_".join(x.split("_")[-1:]) if isinstance(x, str) else '')

	#df['Location_{}'.format(dftype)] = df['Designation'].apply(lambda x: "_".join(x.split("_")[:-1]) if isinstance(x, str) else '')

	df['Name_{}'.format(dftype)] = df['Name_{}'.format(dftype)].apply(lambda x: clean_title(str(x)))
	#df.drop(df.index[0], inplace=True)
	df.reset_index(drop=True, inplace=True)

	df.drop(['Designation'], inplace=True, axis=1)
	print('reformatted months')
	#print(df.head())

	return df

def split_to_months(df_registration):

	baseline_df = df_registration.loc[:,'Baseline Information':'Unnamed: 39']
	baseline_df['Designation'] = df_registration['Unnamed: 7']
	baseline_df['block_name_baseline'] = df_registration['Unnamed: 3']
	baseline_df['district_name_baseline'] = df_registration['Unnamed: 1']
	baseline_df['Individual_UID'] = df_registration['Unnamed: 11']
	baseline_df['Name_Baseline'] = df_registration['Baseline Information']
	#print(baseline_df.head())
	baseline_df = reformat_months(baseline_df, "Baseline")
	#print(baseline_df.head())

	april_df = df_registration.loc[:, 'END OF MONTH 1':'Unnamed: 78']
	april_df['Designation'] = df_registration['Unnamed: 7']
	april_df['block_name_april'] = df_registration['Unnamed: 3']
	april_df['district_name_april'] = df_registration['Unnamed: 1']
	april_df['Individual_UID'] = df_registration['Unnamed: 52']
	april_df['Name_April'] = df_registration['Unnamed: 44']

	april_df = reformat_months(april_df, "April")
	#print(april_df.head())

	may_df = df_registration.loc[:, 'END OF MONTH 2 (MAY-END) INFORMATION ':'Unnamed: 119']
	may_df['Designation'] = df_registration['Unnamed: 7']
	may_df['block_name_may'] = df_registration['Unnamed: 3']
	may_df['district_name_may'] = df_registration['Unnamed: 1']
	may_df['Individual_UID'] = df_registration['Unnamed: 91']
	may_df['Name_May'] = df_registration['Unnamed: 83']

	may_df = reformat_months(may_df, "May")
	#print(may_df.head())

	july_df = df_registration.loc[:, 'END OF MONTH 4 (JULY-END) INFORMATION ': 'Unnamed: 169']
	july_df['Designation'] = df_registration['Unnamed: 7']
	july_df['block_name_july'] = df_registration['Unnamed: 3']
	july_df['district_name_july'] = df_registration['Unnamed: 1']
	july_df['Individual_UID'] = df_registration['Unnamed: 132']
	july_df['Name_July'] = df_registration['Unnamed: 124']

	july_df = reformat_months(july_df, "July")
	#print(july_df.head())

	sept_df = df_registration.loc[:, 'END OF MONTH 5 (SEPTEMBER-END) INFORMATION ':'Unnamed: 219']
	sept_df['Designation'] = df_registration['Unnamed: 7']
	sept_df['block_name_sept'] = df_registration['Unnamed: 3']
	sept_df['district_name_sept'] = df_registration['Unnamed: 1']
	sept_df['Individual_UID'] = df_registration['Unnamed: 182']
	sept_df['Name_Sept'] = df_registration['Unnamed: 174']

	sept_df = reformat_months(sept_df, "Sept")
	#print(sept_df.head())

	oct_df = df_registration.loc[:, 'END OF MONTH 6 (OCTOBER-END) INFORMATION ':'Unnamed: 270']
	oct_df['Designation'] = df_registration['Unnamed: 7']
	oct_df['block_name_oct'] = df_registration['Unnamed: 3']
	oct_df['district_name_oct'] = df_registration['Unnamed: 1']
	oct_df['Individual_UID'] = df_registration['Unnamed: 232']
	oct_df['Name_Oct'] = df_registration['Unnamed: 224']

	oct_df = reformat_months(oct_df, "Oct")
	#print(oct_df.head())

	return baseline_df, april_df, may_df, july_df, sept_df, oct_df


def perform_merge(df_registration):

	baseline_df, april_df, may_df, july_df, sept_df, oct_df = split_to_months(df_registration)
	#print(baseline_df.head(20))
	#print(april_df.head(20))

	result = pd.merge(baseline_df, april_df, on='Individual_UID', how='outer')
	result = pd.merge(result, may_df, on='Individual_UID', how='outer')
	result = pd.merge(result, july_df, on='Individual_UID', how='outer')
	result = pd.merge(result, sept_df, on='Individual_UID', how='outer')
	result = pd.merge(result, oct_df, on='Individual_UID', how='outer')

	#print(result)
	return result


def main():

	pd.options.mode.chained_assignment = None
	df_registration_blocks, df_registration_districts = process_file()

	blocks_merged = perform_merge(df_registration_blocks)
	districts_merged = perform_merge(df_registration_districts)

	blocks_merged = blocks_merged[['Individual_UID', 'Name_Baseline',
								   'district_name_baseline', 'block_name_baseline', 'Designation_Baseline',
								   'Name_April', 'district_name_april', 'block_name_april',
								   'Designation_April', 'Name_May',
								   'district_name_may', 'block_name_may', 'Designation_May',
								   'Name_July', 'district_name_july', 'block_name_july',
								   'Designation_July', 'Name_Sept',
								   'district_name_sept', 'block_name_sept', 'Designation_Sept',
								   'Name_Oct', 'district_name_oct', 'block_name_oct',
								   'Designation_Oct']]

	districts_merged = districts_merged[['Individual_UID', 'Name_Baseline',
								   'district_name_baseline', 'Designation_Baseline',
								   'Name_April', 'district_name_april',
								   'Designation_April', 'Name_May',
								   'district_name_may', 'Designation_May',
								   'Name_July', 'district_name_july',
								   'Designation_July', 'Name_Sept',
								   'district_name_sept', 'Designation_Sept',
								   'Name_Oct', 'district_name_oct',
								   'Designation_Oct']]

	print('BLOCKS MERGED')
	print(blocks_merged)
	print('DISTRICTS MERGED')
	print(districts_merged)
	#getting the district level officers and block level officers in different tabs
	with pd.ExcelWriter('./docs/mastersheet.xlsx') as writer:  # doctest: +SKIP
		blocks_merged.to_excel(writer, sheet_name='Block_Officials', index=False)
		districts_merged.to_excel(writer, sheet_name='District_Officials', index=False)
	print('\nA reformatted registration sheet has been outputted as mastersheet.xlsx...')
	print('The next step before going on to namematching is to manually create the two files mastersheet_edited_one and mastersheet_edited_two, and place these in the docs folder...')



#if __name__ == '__main__':
#	main()
