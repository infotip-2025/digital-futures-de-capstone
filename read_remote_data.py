# example/st_app.py
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# # url = "https://docs.google.com/spreadsheets/d/
# 1Gc3Wi1vpTP4g5rnWuaRJDZWycZHvKO7F2xCv1ZGo0oU/edit?usp=sharing"
# # url = 'https://docs.google.com/spreadsheets/d/
# 1n3aDcsdgAMb17yXnmKZHUm4hK7P8exlkO6H0NdvLZZ8/edit?usp=edit'
# url = 'https://docs.google.com/spreadsheets/d/e/
# 2PACX-1vQnadO2nX23JArLFEhtOK60bmJ9JyHKqeqKL83KZn5gUCuZF
# -WXPyk-l9Mv-6E_VWzpatb9dbBpponf/pubhtml?gid=985363931&single=true'
# id = '1n3aDcsdgAMb17yXnmKZHUm4hK7P8exlkO6H0NdvLZZ8'
#
# Electricity_workbook_extraction (Linked to Main):
# https://docs.google.com/spreadsheets/d/
# 15LJer7zyH6wd_9qDHOl-PeU7FKx-neap9IwlCyCSSf4/edit?usp=sharing
# Apartment 93, Sprinkwell (Main):
# https://docs.google.com/spreadsheets/d/
# 1YfLQZM7W_Cbc7aWaGrYngLpRSVHjIT3BN4ubAb2JICM/edit?usp=sharing

conn = st.connection("gsheets", type=GSheetsConnection)


def read_google_sheets_id(
    source_url,
    first_column=0,
    last_column=0,
    number_of_rows=10**100,
    life_cycle_minutes=1
    ):

    data = conn.read(
        spreadsheet=source_url,
        ttl=life_cycle_minutes,
        usecols=range(first_column, last_column),
        nrows=number_of_rows,
    )

    return data


if __name__ == "__main__":
    source_id = '15LJer7zyH6wd_9qDHOl-PeU7FKx-neap9IwlCyCSSf4'
    source_url = \
        'https://docs.google.com/spreadsheets/d/' + \
        '15LJer7zyH6wd_9qDHOl-PeU7FKx-neap9IwlCyCSSf4' + \
        '/edit?usp=sharing'
    my_df = read_google_sheets_id(source_id, 1, 6, None, 1).iloc[303:, :]

    # drop total reading as one of the meters was not 
    # zeroed properly upon instalation so it differs
    # from the actual total sometimes
    my_df = my_df.drop(columns=my_df.columns[2])

    my_df.rename(columns={
        # 'Unnamed: 1' : 'date',
        my_df.columns[0]: 'date',
        my_df.columns[1]: 'time',
        my_df.columns[2]: 'day',
        my_df.columns[3]: 'night',
        },
                    inplace=True
                    )
    # add timestamp column
    my_df['date_time'] = \
        pd.to_datetime(
            my_df['date'] + \
            ' ' + my_df['time'],
            format='%d/%m/%Y %H:%M'
            )

    my_df = my_df.set_index('date_time')
    st.dataframe(my_df)


    # st.dataframe(my_df.isnull().sum())
    my_df.dropna(
        axis=0,       # default
        how='any',    # default
        # subset tells dropna which columns to consider
        subset=['day', 'night', 'time'],
        inplace=True  # makes change permanent
    )
    # st.dataframe(my_df.isnull().sum())
    # st.dataframe(my_df.dtypes.astype(str))

    st.dataframe(my_df)

    # !!!!! set dates here - start must be first medicines collection date
    start_datetime = my_df.index.min()
    end_datetime = my_df.index.max()
    st.write(f'start {type(start_datetime)}, end {type(end_datetime)}')
    # !!!!!

    # Create the full datetime index for required dates
    full_index = \
        pd.date_range(
            start=start_datetime,
            end=end_datetime,
            freq="min"
            )

    # df_full = pd.merge(full_index, how='outer', left_index=True, right='date_time')
    
    df_full = my_df.reindex(full_index)
    
    # df_full.sort_index(inplace=True)
    st.dataframe(df_full)
    