from os import path, listdir, remove
from os.path import isfile, join
from pathlib import Path
import inspect

import pandas as pd
import Behavioral_Mapping_Script

# -------------------------------------------------------------------------------
#       Behavioral Settings
# -------------------------------------------------------------------------------

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))

BehavioralSettings = [(Path(filename) / '07 - Raw Data/Mapping Task/'), ['Canonical','Non-Canonical'],
                      Path('07 - Raw Data/Mapping Task/Results/'), 'Mapping_Behavioral_Data.xlsx']

# make sure the results folder exists, if not it is created
BehavioralSettings[2].mkdir(parents=True, exist_ok=True)

for idx, LoopDir in enumerate(BehavioralSettings[1]):

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
            PPNum, DataMult, DataUni = Behavioral_Mapping_Script.behavioral_mapping_runner(join(CurDir, File))
            AllDataUni = AllDataUni.append(DataUni, ignore_index=True)
            AllDataMulti = AllDataMulti.append(DataMult, ignore_index=True)
        except:
            print('Error occurred at file: ' + File)
            NumberOfErrors += 1
            quit()

    if NumberOfErrors <= 5:

        if NumberOfErrors > 0:
            print('')
            print('***************************************')
            print('There were {} errors, but I am saving what I have'.format(NumberOfErrors))
            print('check the files and/or code for something strange')
            print('***************************************')

        ExcelFileName = join(BehavioralSettings[2], BehavioralSettings[3])

        BinData = {'Options': ['1: Numbers', '2: Canonical', '3: Non-Canonical'],
                   'Stimulus': ['1: Numbers', '2: Canonical', '3: Non-Canonical'],
                   'Low_High': ['0: Low', '1: High', '']
                   }

        Bins = pd.DataFrame(data=BinData)

        if isfile(ExcelFileName) and idx == 0:
            print('')
            print('***************************************')
            print('found existing excel file, removing it')
            print('***************************************')
            remove(ExcelFileName)

        if idx == 0:
            with pd.ExcelWriter(ExcelFileName, mode='w') as writer:
                Bins.to_excel(writer, sheet_name='Bins')
                AllDataUni.to_excel(writer, sheet_name=('Univariate_' + LoopDir))
                AllDataMulti.to_excel(writer, sheet_name=('Multivariate_' + LoopDir))
        else:
            with pd.ExcelWriter(ExcelFileName, mode='a') as writer:
                AllDataUni.to_excel(writer, sheet_name=('Univariate_' + LoopDir))
                AllDataMulti.to_excel(writer, sheet_name=('Multivariate_' + LoopDir))

        print('')
        print('***************************************')
        print('Successfully saved ' + LoopDir + ' to file: ' + BehavioralSettings[3])
        print('***************************************')

    else:
        print('')
        print('***************************************')
        print('There were {} errors, so I did not save just yet'.format(NumberOfErrors))
        print('check the files and/or code for something strange')
        print('***************************************')
