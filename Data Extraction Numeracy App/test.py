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

BehavioralSettings: list[Union[Union[Path, str], Any]] = [(Path(filename) / 'data2'), (Path(filename) / 'Results'),
                                                          'Numeracy_Data.xlsx']
File = '101_Numeracy.txt'
DataUni = Numeracy_App_Script.numeracy_app_data_runner(join(BehavioralSettings[0], File))
print(DataUni)