import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np


# noinspection PyBroadException
def write_excel(filename, sheetname, dataframe):
    # function that checks if a worksheet exists, deletes it, and then writes the data to it
    with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
        work_book = writer.book
        try:
            work_book.remove(work_book[sheetname])
        except:
            print("Worksheet does not exist")
        finally:
            dataframe.to_excel(writer, sheet_name=sheetname, index=False)
            writer.save()


def check_lines(file_name, look_up):
    # Function to find the line number of a certain string
    with open(file_name) as DataFile:
        for num, line in enumerate(DataFile, 1):
            if look_up in line:
                DataFile.close()
                return num


def numeracy_app_data_runner(filename):
    # we look for the first row of the actual data using the "trial_Number" keyword
    data_start = check_lines(filename, 'Notes:')
    data_end = check_lines(filename, 'Score')



    # extract the participant information from the file, this is always at the top
    # of the file, 6 rows before the data starts
    rows_to_keep = range(0, data_start - 2)

    # Import only those rows into a Dataframe
    info_df = pd.read_csv(filename, skiprows=lambda x: x not in rows_to_keep, header=None, sep=":")
    info_df = info_df.T  # transpose the dataframe so we can call on the info by column name

    # in order to call the information by name (Such as DF_Info['Participant']) we replace the headers
    new_header = info_df.iloc[0]  # grab the first row for the header
    info_df = info_df[1:]  # take the data less the header row
    info_df.columns = new_header  # set the header row as the df header



    # Now we can read in the data
    # we skip the rows until we get to the actual data and stop before the scores given by the app

    rows_to_keep = range(data_start + 1, data_end - 2)

    data_df = pd.read_csv(filename,
                          skiprows=lambda x: x not in rows_to_keep,
                          header=None,
                          sep="\\.\\ | \\_\\ | Answer: | Response",
                          engine='python')


    data_df.columns = ['Trials', 'Component', 'Correct', 'Response']
    data_df['Component'] = data_df['Component'].str.replace('\\d+', '')  # removing the numbers from the labels
    data_df['Component'] = data_df['Component'].str.replace('_', '')  # removing the numbers from the Component labels

    # Total is the total number of times a component appears in the data
    score_total = data_df.groupby('Component').size()

    # The score is the number of components that is still there when we only look at correct responses
    score_correct = data_df[data_df['Correct'] == 1].groupby('Component').sum()

    # we can combine these in a single dataframe to make it easier
    scores = pd.concat([score_correct['Correct'], score_total], axis=1)
    scores.columns = ['Correct', 'Total']

    scores['Percentage'] = scores['Correct'] / scores['Total']

    data_uni = {'PP': np.concatenate([np.repeat(info_df['Child ID'], len(scores))]),
                'Grade': np.concatenate([np.repeat(info_df['Grade'], len(scores))]),
                'Birthday': np.concatenate([np.repeat(info_df['Date Of Birth'], len(scores))]),
                'Sex': np.concatenate([np.repeat(info_df['Sex'], len(scores))]),
                'Age': np.concatenate([np.repeat(info_df['Age'], len(scores))]),
                }

    behavioral_data_uni = pd.DataFrame(data_uni)
    behavioral_data_uni['Component'] = scores.index.values
    behavioral_data_uni['Correct'] = scores['Correct'].values
    behavioral_data_uni['Total'] = scores['Total'].values
    behavioral_data_uni['Percentage'] = scores['Percentage'].values

    # Fill in the zero correct values, which are N/As with actual zeros
    behavioral_data_uni['Correct'] = behavioral_data_uni['Correct'].fillna(0)
    behavioral_data_uni['Percentage'] = behavioral_data_uni['Percentage'].fillna(0)

    return behavioral_data_uni


