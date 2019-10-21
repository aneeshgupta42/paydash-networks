# Package for cleaning social networks data on the PayDash project

## Purpose

Cleaning and mapping the network responses of the MGNREGA employees surveyed. This code was built out for block-level officials from Madhya Pradesh. The end goal is to achieve a UID to UID mapping of survey respondents and the people they list in their networks. Amongst the major goals of this package is to address the widespread inconsistency in the spellings of official names and the spelling and format of their location names (block and district). A protocol consisting of case-wise division and fuzzy string matching was implemented to address this goal.

## Data

Datasets that are an input to the process of networks-cleaning include:

1. Block-level responses: A sheet with the respondents UID, the *response* designation, location, and official name. This is the sheet to be cleaned and mapped. (*block_level_responses_all.csv*)
1. A list of MP block names: File with MP block names, block codes, corresponding district and so on. This file gets used in location matching. (*mp_blocks_2017-2018.csv*)
1. A list of MP district names: File with MP district names and codes. This file gets used in location matching. (*mp_districts_2017-2018.csv*)
1. MP Registration Tracking sheet: Constructed from the MP Transfers and Registration tracking google sheet. This is used to provide a master sheet with the set of 'correct' official names and locations to be mapped to. The google sheet was transposed, so that it was indexed by UIDs. This transpose is carried out in the `registrationreconfigure` module to produce the master sheet. The two approaches within name matching use differently formatted versions of the master sheet. This editing is done manually on the output of `registrationreconfigure`. These two files are fed in separately in `approach_one.py` (name first) and `approach_two.py` (location first) within `namematching`. (Made from *20171113_MP_Transfers_Registration_Combined_April end.xlsx*. `registrationreconfigure` outputs *mastersheet.xlsx*, and this has two edited offspring, which are used in `namematching`)

Note: The 4 files above mentioned should be present in the *docs* directory within the paydash-networks folder.

## Routines

This package contains three different routines. They can be executed from the command line using the appropriate keywords.

1. `registrationreconfigure`: Transposing and cleaning the Registration sheet to be indexed on the officer's *UID*. Provides the master sheet of official names, designation and locations.

2. `locationmatching`: Correcting the input 'Location' field to a block and/or a district match, predicted using a combination of searching and fuzzy-matching.

3. `namematching`: This is the final step, that builds of `locationmatching` and produces the final output of a matched UID (based on the response name, designation and location). Consists of the two name-first and location-first approaches.

To run the code, follow these steps:

1. `cd` into the paydash-networks repository on your local machine.
2. Install the package and all the necessary modules:

   `pip install -e .`

   Now you should be able to run each of the routines on the command line using the appropriate keyword.

## To Do:

* Move to command line file path parameters instead of hard coded paths
* Silent/remove print commands from code so that there isn't too much of command line output cluttering

## Contributors to the process and protocol

In no particular order:
Jared Lieberman, Anisha Grover, Aneesh Gupta

Previous work on networks cleaning was carried out by:
Raul Duarte, Annanya Mahajan, Mahreen Khan
