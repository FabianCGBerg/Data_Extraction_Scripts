from os import path, listdir, remove
from os.path import isfile, join
from pathlib import Path
import inspect

import pandas as pd
import Behavioral_Mapping_Script

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))
BehavioralSettings = [(Path(filename) / '07 - Raw Data/Mapping Task/'), ['Canonical', 'Non-Canonical'],
                      Path('07 - Raw Data/Mapping Task/Results/'), 'Mapping_Behavioral_Data.xlsx']

CurDir = Path(BehavioralSettings[0] / 'Canonical')
#File = 'ppn158_MappingTask_2021-07-08T10.37.43.dat'
#File = 'ppn105_MappingTask_2021-06-14T14.24.05.dat'
File = 'ppn159_MappingTask_2021-07-08T14.12.35.dat'
PPNum, DataMult, DataUni = Behavioral_Mapping_Script.behavioral_mapping_runner(join(CurDir, File))

#print(PPNum)
#print(DataMult)
print(DataUni)