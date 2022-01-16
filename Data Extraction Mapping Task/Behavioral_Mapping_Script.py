import pandas as pd
import numpy as np

pd.set_option("display.max_columns", 10)


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


def check_groupby(df, index_ls, na_value=np.nan):
    for idx in index_ls:
        if idx not in df.index:
            df[idx] = na_value
    return df


def fix_misses(df, rt_col='RT', cor_col='Correct', check_val=0, replace_val=np.nan):
    # Fixes the missed responses to be NaN as to not skew the averages
    df.loc[df[cor_col] == check_val, rt_col] = replace_val

    # sets any negative RT to NaN
    df.loc[df[rt_col] <= 0, rt_col] = replace_val

    return df


def behavioral_mapping_runner(filename):
    # we look for the first row of the actual data using the "trial_Number" keyword
    data_start = check_lines(filename, 'Trial_Number')

    # extract the participant information from the file, this is always at the top
    # of the file, 6 rows before the data starts
    rows_to_keep = range(1, data_start - 6)

    # Import only those rows into a Dataframe
    info_df = pd.read_csv(filename, skiprows=lambda x: x not in rows_to_keep, header=None, sep=";")
    info_df = info_df.T  # transpose the dataframe so we can call on the info by column name

    # in order to call the information by name (Such as DF_Info['Participant']) we replace the headers
    new_header = info_df.iloc[0]  # grab the first row for the header
    info_df = info_df[1:]  # take the data less the header row
    info_df.columns = new_header  # set the header row as the df header

    # Now we can read in the data, we skip the rows until we get to the actual data
    # Columns are as follows:
    # 0) Block; 1) Trial_Number; 2) Number Shown; 3) Key Pressed;
    # 4) Correct; 5) RT; 6) Mirror
    data_df = pd.read_csv(filename, skiprows=data_start - 1, sep=";")

    # we create a new column telling us if the number they saw was larger than 5
    data_df['LowHigh'] = np.where(data_df['Number Shown'] >= 5, 1, 0)

    # First we fix the RT on missed responses to not drag down the averages
    data_df = fix_misses(data_df, check_val=-1)

    # Then we fix the response, correct is coded as 1, incorrect as -1, and misses as 0
    # This is coded separately in case we want to look at incorrect responses too
    # All that we need to do is replace the -1 with 0, since misses and incorrect are the same
    data_df['Correct'] = data_df['Correct'].replace(-1, 0)

    # then we calculate the average Accuracy and RT for Low and High
    rt_overall = data_df.groupby('LowHigh')['RT'].mean()

    # Lastly, we calculate the RTs on only correct responses for Low and High
    rt_correct = data_df[data_df['Correct'] == 1].groupby('LowHigh')['RT'].mean()
    acc_overall = data_df.groupby('LowHigh')['Correct'].mean()

    # Quick check to make sure the groups exist  in case there were no correct in high for example
    rt_correct = check_groupby(rt_correct, [0, 1])
    acc_overall = check_groupby(acc_overall, [0, 1])
    rt_overall = check_groupby(rt_overall, [0, 1])

    # Then we can create the output

    # in a multivariate format (1 row)
    data_mult = {'PP': info_df['Participant'],
                 'Options': info_df['Options'],
                 'Stimulus': info_df['Stimulus'],
                 'Acc_Overall': acc_overall.mean(),
                 'Acc_Low': acc_overall[0],
                 'Acc_High': acc_overall[1],
                 'RT_Overall': rt_overall.mean(),
                 'RT_Low': rt_overall[0],
                 'RT_High': rt_overall[1],
                 'RT_Cor_Overall': rt_correct.mean(),
                 'RT_Cor_Low': rt_correct[0],
                 'RT_Cor_High': rt_correct[1]
                 }

    behavioral_data_mult = pd.DataFrame(data_mult)
    # Here I recode the Options and Stimulus variables into numbers
    behavioral_data_mult['Options'] = behavioral_data_mult['Options'].map(
        {'Numbers': 1, 'Canonical': 2, 'Non-Canonical': 3})
    behavioral_data_mult['Stimulus'] = behavioral_data_mult['Stimulus'].map(
        {'Numbers': 1, 'Canonical': 2, 'Non-Canonical': 3})

    # and as a univariate format
    data_uni = {'PP': np.concatenate([np.repeat(info_df['Participant'], len(acc_overall))]),
                'Options': np.concatenate([np.repeat(info_df['Options'], len(acc_overall))]),
                'Stimulus': np.concatenate([np.repeat(info_df['Stimulus'], len(acc_overall))]),
                'Mean_Acc': acc_overall.mean(),
                'Mean_RT': rt_overall.mean(),
                'Mean_RT_Cor': rt_correct.mean(),
                'Range': [0, 1],
                'Acc': acc_overall,
                'RT_Overall': rt_overall,
                'RT_Correct': rt_correct
                }

    behavioral_data_uni = pd.DataFrame(data_uni)
    # Here I recode the Options and Stimulus variables into numbers
    behavioral_data_uni['Options'] = behavioral_data_uni['Options'].map(
        {'Numbers': 1, 'Canonical': 2, 'Non-Canonical': 3})
    behavioral_data_uni['Stimulus'] = behavioral_data_uni['Stimulus'].map(
        {'Numbers': 1, 'Canonical': 2, 'Non-Canonical': 3})

    return int(info_df['Participant']), behavioral_data_mult, behavioral_data_uni
