import pandas as pd
from namematching.helpers.approach_one import approach_one
from namematching.helpers.approach_two import approach_two
import datetime
import time

def main():
    print('\nBeginning approach one (name first matching)...')
    approach_one()
    time.sleep(2)
    print('\nBeggining approach two (location first matching)...')
    approach_two()
    print('\nName matching also completed. Check docs for final output...')
