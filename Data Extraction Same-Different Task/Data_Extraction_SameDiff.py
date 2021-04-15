from os import path, listdir, remove
from os.path import isfile, join
from pathlib import Path
import inspect

import pandas as pd
import Behavioral_SameDiff_Script

# -------------------------------------------------------------------------------
#       Behavioral Settings
# -------------------------------------------------------------------------------

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))

BehavioralSettings = [(Path(filename) / 'data/'), ['4) 3-Val_Uncrossed.csv'],
                      Path('data/Results/'), 'SameDiff_Behavioral_Data.xlsx']

# make sure the results folder exists, if not it is created
BehavioralSettings[2].mkdir(parents=True, exist_ok=True)

dir_counter = 0
dir_append = ''

for LoopDir in BehavioralSettings[1]:

    if len(BehavioralSettings[1]) > 1:
        dir_counter += 1
        dir_append = str(dir_counter)

    print('==========================')
    print('processing Folder: ' + LoopDir)
    print('==========================')

    NumberOfErrors = 0  # Initialize error counter

    AllDataUni = pd.DataFrame()  # initialize dataframes
    AllDataMulti = pd.DataFrame()

    # Create the current directory
    CurDir = Path(BehavioralSettings[0] / LoopDir)

    # Load in all the .dat files in that directory
    Files = []
    for file in listdir(CurDir):
        if file.endswith(".dat"):
            Files.append(file)

    # Loop through the files and extract the data
    for File in Files:
        print('processing: ' + File)
        try:
            PPNum, DataMult, DataUni = Behavioral_SameDiff_Script.behavioral_samediff_runner(join(CurDir, File))
            AllDataUni = AllDataUni.append(DataUni, ignore_index=True)
            AllDataMulti = AllDataMulti.append(DataMult, ignore_index=True)
        except:
            print('Error occurred at file: ' + File)
            NumberOfErrors += 1

    if NumberOfErrors == 0:

        ExcelFileName = join(BehavioralSettings[2], BehavioralSettings[3])

        BinData = {'Bins': ['1: Low Incongruent Non-Canonical', '2: Low Incongruent Canonical',
                            '3: Low Congruent Non-Canonical', '4: Low Congruent Canonical',
                            '6: High Incongruent Non-Canonical', '7: High Incongruent Canonical',
                            '8: High Congruent Non-Canonical', '9: High Congruent Canonical'
                            ],
                   'Range': ['0: Low', '1: High', '', '', '', '', '', ''],
                   'Canonicity': ['0: Non-Canonical', '1: Canonical', '', '', '', '', '', ''],
                   'Congruency': ['0: Incongruent', '1: Congruent', '', '', '', '', '', ''],
                   'Handedness': ['0: Left', '1: Right', '', '', '', '', '', '']
                   }

        Bins = pd.DataFrame(data=BinData)

        if isfile(ExcelFileName):
            remove(ExcelFileName)

        with pd.ExcelWriter(ExcelFileName, mode='w') as writer:
            Bins.to_excel(writer, sheet_name='Bins')
            AllDataUni.to_excel(writer, sheet_name= ('Univariate' + dir_append))
            AllDataMulti.to_excel(writer, sheet_name=('Multivariate' + dir_append))

        print('')
        print('***************************************')
        print('Successfully saved ' + LoopDir + ' to file: ' + BehavioralSettings[3])
        print('***************************************')
