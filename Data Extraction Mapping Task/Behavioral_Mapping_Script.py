import csv
import pandas as pd
import numpy as np

def write_excel(filename,sheetname,dataframe):
    #function that checks if a worksheet exists, deletes it, and then writes the data to it
    with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer: 
        workBook = writer.book
        try:
            workBook.remove(workBook[sheetname])
        except:
            print("Worksheet does not exist")
        finally:
            dataframe.to_excel(writer, sheet_name=sheetname,index=False)
            writer.save()

def CheckLines(FileName, LookUp):
    # Fucntion to find the line number of a certain string
    with open(FileName) as DataFile:
        for num, line in enumerate(DataFile, 1):
            if LookUp in line:
                DataFile.close
                return num
                break


def Behavioral_Mapping_Runner(filename):
    #filename = "/Users/fabian/Dropbox/Work/Python Tasks/Mapping Task/Python Scripts/07 - Raw Data/Mapping Task/Canonical/ppn002_MappingTask_2021-02-10T10.28.40.dat"

    # we look for the first row of the actual data using the "trial_Number" keyword
    DataStart = CheckLines(filename, 'Trial_Number')

    #e xtract the participant information from the file, this is always at the top
    # of the file, 6 rows before the data starts
    rows_to_keep = range(1, DataStart-6)

    #Import only those rows into a Dataframe
    Info_DF = pd.read_csv(filename, skiprows = lambda x: x not in rows_to_keep, header=None, sep=";")
    Info_DF = Info_DF.T                         #transpose the dataframe so we can call on the info by column name

    # in order to call the information by name (Such as DF_Info['Participant']) we replace the headers
    new_header = Info_DF.iloc[0]        #grab the first row for the header
    Info_DF = Info_DF[1:]                       #take the data less the header row
    Info_DF.columns = new_header    #set the header row as the df header

    #Now we can read in the data, we skip the rows until we get to the actual data
    # Columns are as follows:
    # 0) Block; 1) Trial_Number; 2) Number Shown; 3) Key Pressed;
    # 4) Correct; 5) RT; 6) Mirror
    Data_DF = pd.read_csv(filename, skiprows = DataStart-1, sep=";")

    #we create a new column telling us if the number they saw was larger than 5
    Data_DF['LowHigh'] = np.where(Data_DF['Number Shown']>= 5, 1, 0)

    # then we calculate the average Accuracy and RT for Low and High
    AccOverall = Data_DF.groupby('LowHigh')['Correct'].mean()
    RTOverall = Data_DF.groupby('LowHigh')['RT'].mean()

    #Lastly, we calculate the RTs on only correct responses for Low and High
    RTCorrect  = Data_DF[Data_DF['Correct']==1 ].groupby('LowHigh')['RT'].mean()


    #Then we can create the output

    # in a multivariate format (1 row)
    dataMult = {'PP'                   : Info_DF['Participant'], 
                    'Options'               : Info_DF['Options'],
                    'Stimulus'              : Info_DF['Stimulus'],
                    'Acc_Overall'         : AccOverall.mean(),
                    'Acc_Low'              :AccOverall[0],
                    'Acc_High'             :AccOverall[1],
                    'RT_Overall'           :RTOverall.mean(),
                    'RT_Low'               :RTOverall[0],
                    'RT_High'              :RTOverall[1],
                    'RT_Cor_Overall'   :RTCorrect.mean(),
                    'RT_Cor_Low'        :RTCorrect[0],
                    'RT_Cor_High'       :RTCorrect[1]
                    } 

    BehavioralDataMult = pd.DataFrame(dataMult)

    # and as a univariate format
    dataUni =  {'PP'                   : np.concatenate([np.repeat(Info_DF['Participant'], len(AccOverall) )]), 
                    'Options'               : np.concatenate([np.repeat(Info_DF['Options'], len(AccOverall) )]),
                    'Stimulus'              : np.concatenate([np.repeat(Info_DF['Stimulus'], len(AccOverall) )]),
                    'Mean_Acc'           : AccOverall.mean(),
                    'Mean_RT'             : RTOverall.mean(),
                    'Mean_RT_Cor'      : RTCorrect.mean(),
                    'Range'                 : [0, 1],
                    'Acc'                       : AccOverall,
                    'RT_Overall'           : RTOverall,
                    'RT_Correct'          : RTCorrect
                    }

    BehavioralDataUni = pd.DataFrame(dataUni)
    
    return int(Info_DF['Participant']), BehavioralDataMult, BehavioralDataUni

