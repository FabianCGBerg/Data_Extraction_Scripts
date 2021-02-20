from os import path, listdir
from os.path import isfile, join
from pathlib import Path
import inspect
from typing import Any, Union
import pandas as pd
import Numeracy_App_Script

# -------------------------------------------------------------------------------
#       Behavioral Settings
# -------------------------------------------------------------------------------

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))

BehavioralSettings: list[Union[Union[Path, str], Any]] = [(Path(filename) / 'data'), (Path(filename) / 'Results'),
                                                          'Numeracy_Data.xlsx']

# make sure the results folder exists, if not it is created
BehavioralSettings[1].mkdir(parents=True, exist_ok=True)

NumberOfErrors = 0  # Initialize error counter
AllDataUni = pd.DataFrame()  # initialize dataframes

# Load in all the .dat files in that directory
Files = []
for file in listdir(Path(BehavioralSettings[0])):
    if file.endswith(".txt"):
        Files.append(file)

# Loop through the files and extract the data
for File in Files:
    print('processing: ' + File)
    try:
        DataUni = Numeracy_App_Script.numeracy_app_data_runner(join(BehavioralSettings[0], File))
        AllDataUni = AllDataUni.append(DataUni, ignore_index=True)
    except:
        print('Error occurred at file: ' + File)
        NumberOfErrors += 1


if NumberOfErrors == 0:

    ExcelFileName = join(BehavioralSettings[1], BehavioralSettings[2])

    Measures = [
        ['NumCncpt', 'CountSub', 'Pattern', 'MatchNum', 'WordProb', 'NumLine', 'Subit', 'SpMeas', 'OrdPos', 'Equat'],
        ['Early Numerical Concepts and Language',
         'Counting a Subset',
         'Discerning & Completing Patterns',
         'Matching Digit & Quantity',
         'Numerical Word Problems',
         'Completing Number Line',
         'Conceptual Subitizing',
         'Early Spatial & Measurement Concepts',
         'Ordinal Position',
         'Number Comparison']
    ]

    Measures = pd.DataFrame(data=Measures).T

    if isfile(ExcelFileName):
        Numeracy_App_Script.write_excel(ExcelFileName, 'Numeracy Data', AllDataUni)
    else:
        with pd.ExcelWriter(ExcelFileName, mode='w') as writer:
            Measures.to_excel(writer, sheet_name='Measures')
            AllDataUni.to_excel(writer, sheet_name='Numeracy Data')

print('')
print('***************************************')
print('Successfully saved Numeracy Data to file: ' + BehavioralSettings[2])
print('***************************************')
