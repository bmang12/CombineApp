import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import io

from matplotlib import pyplot as plt
from fpdf import FPDF
from io import BytesIO

from st_aggrid import AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from data_prep import *
from plotting_functions import *
from design_pdf import *

import base64

import os

st.set_page_config(layout='wide')
st.title('Combine Report')

df_tm = None

uploaded_file = st.file_uploader('Choose a file')
if uploaded_file is not None:
    df_tm, club_order = read_data(uploaded_file)

if df_tm is not None:

    # players = df_tm['Player'].unique()
    # player_select = st.selectbox('Select Player',
    #                           list(players))

    # df_player_filter = df_tm.loc[df_tm['Player'] == player_select]
    # df_player_filter['Date'] = df_player_filter['Date'].astype(str)
 
    gd = GridOptionsBuilder.from_dataframe(df_tm)
    gd.configure_pagination(enabled=True)
    gd.configure_default_column(editable=True, groupable=True)
    # gd.configure_column('Date', type=['customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm')
    gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridoptions = gd.build()
    grid_table = AgGrid(
        df_tm,
        gridOptions=gridoptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    )
    sel_row = grid_table["selected_rows"]
    
    test_data = grid_table['data']
    drop_rows = [row['ShotNo'] for row in sel_row]
    df_filtered = test_data.loc[~test_data['ShotNo'].isin(drop_rows)]

    # st.subheader('Raw data')
    # st.write(df_tm_filter)
    st.subheader('Filtered data')
    # df_sel_row = pd.DataFrame(sel_row)
    # if not df_sel_row.empty:
    st.write(df_filtered)


if df_tm is not None:

    # st.subheader('Filtered data')
    # club_select = st.multiselect(label=' ',
    #                             options=list(df_filtered.sort_values(by=['ClubIdx'])['Club'].unique()))

    player = df_filtered['Player'].unique()[0]

    date = str(df_filtered['Date'].unique()[0].strftime('%m-%d-%Y'))

    files = [f for f in os.listdir('.') if os.path.isdir(f)]
    st.selectbox('test', files)
    
    # if len(club_select) > 0:
    if st.button('Create Report'):

        progress_bar = st.progress(0)

        pdf = make_pdf(df_filtered, club_order, player, date, progress_bar)

        pdf_title = player + ' ' + str(date) + ' ' + 'Report.pdf'
        # pdf.output(pdf_title)

        # with open(pdf_title, 'rb') as pdf_file:
        #     PDFbyte = pdf_file.read()

        st.download_button(label='Export Report',
                        data=bytes(str(pdf.output(), encoding='latin1'), encoding='latin1'),
                        file_name=pdf_title,
                        mime='application/octet-stream')


## Command line prompts 
# streamlit run create_dashboard.py
# ctrl c
