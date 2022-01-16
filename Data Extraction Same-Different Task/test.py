from os import path, listdir, remove
from os.path import isfile, join
from pathlib import Path
import inspect

import pandas as pd
import Behavioral_SameDiff_Script

filename = Path(path.dirname(path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)))

BehavioralSettings = [(Path(filename) / 'Data/'), ['3-Val_Uncrossed.csv'],
                      Path('Data/Results/'), 'SameDiff_Behavioral_Data.xlsx']

CurDir = Path(BehavioralSettings[0] / '3-Val_Uncrossed.csv')
#File = 'ppn108_ 4) 3-Val_Uncrossed_2021-06-15T10.06.28.dat'
File = 'ppn141_ 4) 3-Val_Uncrossed_2021-07-02T15.09.44.dat'

PPNum, DataMult, DataUni = Behavioral_SameDiff_Script.behavioral_samediff_runner(join(CurDir, File))

print(DataUni)