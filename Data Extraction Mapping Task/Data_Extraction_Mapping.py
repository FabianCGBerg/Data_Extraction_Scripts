
from os import path, listdir
from os.path import isfile, join
from pathlib import Path
import inspect

import pandas as pd
import Behavioral_Mapping_Script 

#-------------------------------------------------------------------------------
#       Behavioral Settings
#-------------------------------------------------------------------------------

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))

BehavioralSettings = []

BehavioralSettings.append( (Path(filename) / '07 - Raw Data/Mapping Task/')); #0 LoadPath
BehavioralSettings.append(['Canonical', 'Non-Canonical']); #1 Folders
BehavioralSettings.append(Path(BehavioralSettings[0] / 'Results/')); #2 SavePath
BehavioralSettings.append('Mapping_Behavioral_Data.xlsx'); #3 ExcelFile

#make sure the results folder exists, if not it is created
BehavioralSettings[2].mkdir(parents=True, exist_ok=True)

for LoopDir in BehavioralSettings[1]:
    
    print('==========================')
    print('processing Folder: ' + LoopDir)
    print('==========================')
    
    NumberOfErrors = 0 #Initialize error counter
    
    AllDataUni = pd.DataFrame()  #initialize dataframes
    AllDataMulti= pd.DataFrame()
    
    #Create the current directory
    CurDir = Path(BehavioralSettings[0] / LoopDir)
    
    #Load in all the .dat files in that directory
    Files = []
    for file in listdir(CurDir):
        if file.endswith(".dat"):
            Files.append(file)
    
    #Loop through the files and extract the data
    for File in Files: 
        print('processing: ' + File)
        try:
            PPNum, DataMult, DataUni = Behavioral_Mapping_Script.Behavioral_Mapping_Runner(join(CurDir, File))
            AllDataUni = AllDataUni.append(DataUni, ignore_index = True)
            AllDataMulti = AllDataMulti.append(DataMult, ignore_index = True)
        except:
             print('Error occured at file: ' + File)
             NumberOfErrors += 1
    
    if NumberOfErrors == 0:
        
        ExcelFileName = join(BehavioralSettings[2], BehavioralSettings[3])
        
        BinData = {'Options': ['1: Numbers', '2: Canonical', '3: Non-Canonical'],
                    'Stimulus': ['1: Numbers', '2: Canonical', '3: Non-Canonical'],
                    'Low_High': ['0: Low', '1: High', '']
                    };
        
        Bins = pd.DataFrame(data=BinData)
        
        if isfile(ExcelFileName):
            Behavioral_Mapping_Script.write_excel(ExcelFileName,('Univariate_' + LoopDir),AllDataUni)
            Behavioral_Mapping_Script.write_excel(ExcelFileName,('Multivariate_' + LoopDir),AllDataMulti)
        else:
            with pd.ExcelWriter(ExcelFileName, mode='w' ) as writer: 
                Bins.to_excel(writer, sheet_name='Bins') 
                AllDataUni.to_excel(writer, sheet_name=('Univariate_' + LoopDir))
                AllDataMulti.to_excel(writer, sheet_name=('Multivariate_' + LoopDir)) 
        
        print('')
        print('***************************************')
        print('Succesfully saved ' + LoopDir + ' to file: ' + BehavioralSettings[3])
        print('***************************************')




