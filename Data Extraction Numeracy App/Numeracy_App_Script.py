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

def Numeracy_App_Data_Runner(filename):
    # we look for the first row of the actual data using the "trial_Number" keyword
    DataStart = CheckLines(filename, 'Notes:')
    DataEnd = CheckLines(filename, 'Score')

    #extract the participant information from the file, this is always at the top
    # of the file, 6 rows before the data starts
    rows_to_keep = range(3, DataStart-2)

    #Import only those rows into a Dataframe
    Info_DF = pd.read_csv(filename, skiprows = lambda x: x not in rows_to_keep, header=None, sep=":")
    Info_DF = Info_DF.T                         #transpose the dataframe so we can call on the info by column name

    # in order to call the information by name (Such as DF_Info['Participant']) we replace the headers
    new_header = Info_DF.iloc[0]        #grab the first row for the header
    Info_DF = Info_DF[1:]                       #take the data less the header row
    Info_DF.columns = new_header    #set the header row as the df header

    #Now we can read in the data, we skip the rows until we get to the actual data and stop before the scores given by the app
    rows_to_keep = range(DataStart+1, DataEnd-2)

    Data_DF = pd.read_csv(filename, 
                                            skiprows = lambda x: x not in rows_to_keep, 
                                            header=None, 
                                            sep="\\.\\ | \\_\\ | Answer: | Response", 
                                            engine='python')

    Data_DF.columns = ['Trials', 'Component', 'Correct', 'Response']
    Data_DF['Component'] = Data_DF['Component'].str.replace('\d+', '') #removing the numbers from the Component labels
    Data_DF['Component'] = Data_DF['Component'].str.replace('_', '') #removing the numbers from the Component labels

    #Total is the total number of times a component appears in the data
    ScoreTotal  = Data_DF.groupby('Component').size()

    #The score is the number of components that is still there when we only look at correct responses
    ScoreCorrect  = Data_DF[Data_DF['Correct']==1 ].groupby('Component').sum()

    #we can combine these in a single dataframe to make it easier 
    Scores = pd.concat([ScoreCorrect['Correct'], ScoreTotal], axis=1)
    Scores.columns = ['Correct', 'Total']

    Scores['Percentage'] = Scores['Correct']/Scores['Total']

    dataUni =  {'PP'                   : np.concatenate([np.repeat(Info_DF['Child ID'], len(Scores) )]), 
                        'Grade'               : np.concatenate([np.repeat(Info_DF['Grade'], len(Scores) )]),
                        'Birthday'               : np.concatenate([np.repeat(Info_DF['Date Of Birth'], len(Scores) )]),
                        'Sex'               : np.concatenate([np.repeat(Info_DF['Sex'], len(Scores) )]),
                        'Age'               : np.concatenate([np.repeat(Info_DF['Age'], len(Scores) )]),
                        }

    BehavioralDataUni = pd.DataFrame(dataUni)
    BehavioralDataUni['Component'] = Scores.index.values
    BehavioralDataUni['Correct'] = Scores['Correct'].values
    BehavioralDataUni['Total'] = Scores['Total'].values
    BehavioralDataUni['Percentage'] = Scores['Percentage'].values

    return BehavioralDataUni

Testfile = '/Users/fabian/Dropbox/Work/Python Tasks/Numeracy App/data/1_Numeracy.txt'
print(Numeracy_App_Data_Runner(Testfile))