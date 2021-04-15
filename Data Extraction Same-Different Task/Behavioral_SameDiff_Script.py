import pandas as pd
import numpy as np


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


def behavioral_samediff_runner(filename):

    # we look for the first row of the actual data using the "trial_Number" keyword
    data_start = check_lines(filename, 'Trial_Number')

    # extract the participant information from the file, this is always at the top
    # of the file, 6 rows before the data starts
    rows_to_keep = range(2, data_start - 3)

    # Import only those rows into a Dataframe
    info_df = pd.read_csv(filename, skiprows=lambda x: x not in rows_to_keep, header=None, sep=";")
    info_df = info_df.T  # transpose the dataframe so we can call on the info by column name

    # in order to call the information by name (Such as DF_Info['Participant']) we replace the headers
    new_header = info_df.iloc[0]  # grab the first row for the header
    info_df = info_df[1:]  # take the data less the header row
    info_df.columns = new_header.str.strip()  # set the header row as the df header (without whitespaces)

    # Now we can read in the data, we skip the rows until we get to the actual data
    # Columns are as follows:

    # 0) Block;
    # 1) Trial_Number;
    # 2) Trial Code;
    # 3) Symbol_Num;
    # 4) Hand_Num;
    # 5) Dominant Hand;
    # 6) Non Dominant Hand;
    # 7) Distance;
    # 8) Stim_Hand_Dom;
    # 9) Canonical;
    # 10) buttonPressed;
    # 11) Correct;
    # 12) fixationTime;
    # 13) StimOnset;
    # 14) SOA;
    # 15) responseTime;
    # 16) Buttonbox RT

    # We add the following columns in this script
    # 17) Can/Con Bins
    # 18) Low/High
    # 19) Low/High Can/Con bins

    data_df = pd.read_csv(filename, skiprows=data_start - 1, sep=";")

    # we create a new column for the canonicity and congruency bins
    data_df['Can/Con Bins'] = (data_df['Canonical'] + 1) + (2 * (data_df['Distance'] == 0))

    # we create a new column telling us if the number they saw was larger than 5
    data_df['Low/High'] = np.where(data_df['Symbol_Num'] >= 5, 1, 0)

    # we create a new column giving us the bins for the canonical/congruent bins for low and high
    data_df['Low/High Can/Con bins'] = data_df['Can/Con Bins'] + (5 * data_df['Low/High'])

    # then we calculate the average Accuracy and RT for the 8 conditions made by Range, Canonicity, and Congruency
    acc_overall = data_df.groupby('Low/High Can/Con bins')['Correct'].mean()
    rt_overall = data_df.groupby('Low/High Can/Con bins')['responseTime'].mean()

    # Lastly, we calculate the RTs on only correct responses
    rt_correct = data_df[data_df['Correct'] == 1].groupby('Low/High Can/Con bins')['responseTime'].mean()

    # Then we can create the output

    # in a multivariate format (1 row)

    # take the means and transpose them into a single line, then add the column names
    acc_overall_mult = acc_overall.reset_index().T
    acc_overall_mult = acc_overall_mult[1:]  # take the data less the header row
    acc_overall_mult.columns = ['acc_Low_Incon_NCan', 'acc_Low_Incon_Can', 'acc_Low_Con_Ncan', 'acc_Low_Con_Can',
                                'acc_High_Incon_NCan', 'acc_High_Incon_Can', 'acc_High_Con_Ncan', 'acc_High_Con_Can']

    rt_overall_mult = rt_overall.reset_index().T
    rt_overall_mult = rt_overall_mult[1:]  # take the data less the header row
    rt_overall_mult.columns = ['RT_Low_Incon_NCan', 'RT_Low_Incon_Can', 'RT_Low_Con_Ncan', 'RT_Low_Con_Can',
                               'RT_High_Incon_NCan', 'RT_High_Incon_Can', 'RT_High_Con_Ncan', 'RT_High_Con_Can']

    rt_correct_mult = rt_correct.reset_index().T
    rt_correct_mult = rt_correct_mult[1:]  # take the data less the header row
    rt_correct_mult.columns = ['RT_Cor_Low_Incon_NCan', 'RT_Cor_Low_Incon_Can', 'RT_Cor_Low_Con_Ncan', 'RT_Cor_Low_Con_Can',
                               'RT_Cor_High_Incon_NCan', 'RT_Cor_High_Incon_Can', 'RT_Cor_High_Con_Ncan', 'RT_Cor_High_Con_Can']

    # Add in the participant information and the overall means
    data_mult = {'PP': info_df['Participant'],
                 'Age': info_df['Age'],
                 'Sex': info_df['Sex'],
                 'Handedness': info_df['Handedness'],
                 'Acc_Overall': acc_overall.mean(),
                 'RT_Overall': rt_overall.mean(),
                 'RT_Cor_Overall': rt_correct.mean(),
                 }
    behavioral_data_mult = pd.DataFrame(data_mult)

    # merge the PP info with the data
    behavioral_data_mult.reset_index(drop=True, inplace=True)
    acc_overall_mult.reset_index(drop=True, inplace=True)
    rt_overall_mult.reset_index(drop=True, inplace=True)
    rt_correct_mult.reset_index(drop=True, inplace=True)

    behavioral_data_mult = pd.concat([behavioral_data_mult, acc_overall_mult, rt_overall_mult, rt_correct_mult], axis=1)

    # and as a univariate format
    data_uni = {'PP': np.concatenate([np.repeat(info_df['Participant'], len(acc_overall))]),
                'Age': np.concatenate([np.repeat(info_df['Age'], len(acc_overall))]),
                'Handedness': np.concatenate([np.repeat(info_df['Handedness'], len(acc_overall))]),
                'Bin': np.concatenate([range(1, 5), range(6, 10)]),
                'Range': np.concatenate([range(1, 5), range(6, 10)]),
                'Canonicity': np.concatenate([range(1, 5), range(6, 10)]),
                'Congruency': np.concatenate([range(1, 5), range(6, 10)]),
                'Acc': acc_overall,
                'RT_Overall': rt_overall,
                'RT_Correct': rt_correct
                }

    behavioral_data_uni = pd.DataFrame(data_uni)

    # Here I recode the Range, Canonicity, and Congruency variables based on Bin, also recode handedness
    behavioral_data_uni['Range'] = np.where(behavioral_data_uni['Bin'] >= 5, 1, 0)
    behavioral_data_uni['Canonicity'] = behavioral_data_uni['Canonicity'].map(
        {1: 0, 3: 0, 6: 0, 8: 0, 2: 1, 4: 1, 7: 1, 9: 1})
    behavioral_data_uni['Congruency'] = behavioral_data_uni['Congruency'].map(
        {1: 0, 2: 0, 3: 1, 4: 1, 6: 0, 7: 0, 8: 1, 9: 1})
    behavioral_data_uni['Handedness'] = behavioral_data_uni['Handedness'].map(
        {'Left': 0, 'Right': 1})

    return int(info_df['Participant']), behavioral_data_mult, behavioral_data_uni
