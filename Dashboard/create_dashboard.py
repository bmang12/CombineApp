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
from web_scrape import *

import base64

st.set_page_config(layout='wide')
st.title('Combine Report')

df_tm = None
df_comp = pd.read_csv('Dashboard/CompHist.csv')

# Add option for link
# player_data = scrape('https://mytrackman.com/system/dynamic-report?r=93798e80-8e0c-430e-8119-05926910e5bd&dm=c&nd=true&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=ClubSpeed&mp%5B%5D=BallSpeed&mp%5B%5D=LaunchAngle&mp%5B%5D=SpinRate&mp%5B%5D=Carry&mp%5B%5D=Total&mp%5B%5D=Height&mp%5B%5D=LaunchDirection&mp%5B%5D=SpinAxis&mp%5B%5D=SmashFactor&u=Us&v=dispersion&sgos%5B%5D=55603568-3444-4443-a0ae-40f8ec6c1828&sgos%5B%5D=a942535c-13d0-4b3f-b53e-6e96fcceea64&sgos%5B%5D=0383d609-030b-4535-a33d-811790da1111&sgos%5B%5D=5fe556ba-0ab5-4db2-8c90-2e06fb3087a6&sgos%5B%5D=59173216-a715-4615-85d9-ae74fcc37300&sgos%5B%5D=683f1244-c1ac-4a5d-aa21-6d6660adbc4f&sgos%5B%5D=6bb8c487-5769-4792-a4a1-7f2382f68830&sgos%5B%5D=8fbc55c3-a4d4-4885-ae48-f0c1b385d84d&sgos%5B%5D=aecfa4ac-e5fa-4b3a-b912-42aae85ba61c&sgos%5B%5D=c2ae487d-6d03-41b3-bd67-9d24e75d02f7&sgos%5B%5D=22559002-1984-4cfa-a0fc-361576f61616&sgos%5B%5D=487ff424-0d27-4ed8-989a-603544011f62&sgos%5B%5D=d8fbbd80-ef1f-46dd-8af9-f776b2b2447e&sgos%5B%5D=f34d03e9-1be5-4203-9b88-0e78b2d0bd57&sgos%5B%5D=cf7247a7-4a5f-470b-9e8f-f5faee1af5d5')
st.header('Import Data')

st.radio('Input Type',
         ['Trackman Excel', 'MyTrackman Link (not functional)'],
         key='input_type',
         horizontal=True)

if st.session_state.input_type == 'Trackman Excel':
    dis_upload = False
    dis_link = True
else:
    dis_upload = True
    dis_link = False

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader('Choose a file', disabled=dis_upload)

with col2:
    st.text_input('Enter MyTrackman Link and Press Enter', '', key='tm_link', disabled=dis_link)
    tm_link = st.session_state.tm_link

if not dis_upload:
    if uploaded_file is not None:
        df_tm, club_order = read_data(uploaded_file)
        df_filtered = df_tm.copy()
elif not dis_link:
    if tm_link != '':
        with col2:
            df_tm, club_order = scrape(tm_link)
            df_filtered = df_tm.copy()

if df_tm is not None:

    # players = df_tm['Player'].unique()
    # player_select = st.selectbox('Select Player',
    #                           list(players))

    # df_player_filter = df_tm.loc[df_tm['Player'] == player_select]
    # df_player_filter['Date'] = df_player_filter['Date'].astype(str)
 
    # gd = GridOptionsBuilder.from_dataframe(df_tm)
    # gd.configure_pagination(enabled=True)
    # gd.configure_default_column(editable=True, groupable=True)
    # # gd.configure_column('Date', type=['customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm')
    # gd.configure_selection(selection_mode="multiple", use_checkbox=True)
    # gridoptions = gd.build()
    # grid_table = AgGrid(
    #     df_tm,
    #     gridOptions=gridoptions,
    #     update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
    #     theme="streamlit",
    #     columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    # )
    # sel_row = grid_table['selected_rows']
    
    # test_data = grid_table['data']
    # drop_rows = [row['ShotNo'] for row in sel_row]
    # df_filtered = test_data.loc[~test_data['ShotNo'].isin(drop_rows)]

    # st.subheader('Raw data')
    st.header('Data Entry')

    col3, col4 = st.columns(2)
    with col3:
        st.subheader('Location')
        st.text_input(' ', '', key='location', label_visibility='collapsed')
    with col4:
        st.subheader('Golf Ball Used')
        st.text_input(' ', '', key='ball', label_visibility='collapsed')

    clubs = df_tm.sort_values('ClubIdx')['Club'].unique()
    df_specs_entry = pd.DataFrame({'Club': clubs})
    df_specs_entry[['Model Info', 'Loft', 'Lie', 'Length', 'Shaft', 'SW', 'Target\nCarry']] = None
    df_specs_entry.index = df_specs_entry.index + 1

    st.subheader('Club Specs')
    st.write('Enter Club Specs in each cell or copy and paste from an Excel file')
    # gd = GridOptionsBuilder.from_dataframe(df_specs_entry)
    # gd.configure_pagination(enabled=False)
    # gd.configure_default_column(editable=True)
    # gridoptions = gd.build()
    # grid_table_specs = AgGrid(
    #     df_specs_entry,
    #     gridOptions=gridoptions,
    #     update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
    #     theme="streamlit",
    #     columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    # )

    tbl_height = 37 + (len(clubs) * 35)
    df_specs = st.experimental_data_editor(df_specs_entry, height=tbl_height)

    # st.write(df_tm_filter)
    st.header('Trackman Data')
    # df_sel_row = pd.DataFrame(sel_row)
    # if not df_sel_row.empty:
    # st.write(df_tm)
 
    st.subheader('Select Rows to :red[Not] Include or Change Club Type')
    cols = ['ShotNo', 'Player', 'Club', 'ClubSpeed', 'AttackAngle', 'ClubPath', 'BallSpeed', 'LaunchAngle',
            'SpinRate', 'CarryDistance', 'CarryOffLine', 'ApexHeight']

    gd = GridOptionsBuilder.from_dataframe(df_tm[cols])
    gd.configure_pagination(enabled=False)
    gd.configure_default_column(editable=True)
    # gd.configure_column('Date', type=['customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm')
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    for col in cols:
        if col not in ['ShotNo', 'Player', 'Club', 'SpinRate']:
            gd.configure_column(col, type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision=1)
        if col != 'Club':
            gd.configure_column(col, editable=False)
    gd.configure_column('SpinRate', type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'], precision=0)
    gridoptions = gd.build()
    grid_table = AgGrid(
        df_tm,
        gridOptions=gridoptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        height=500
    )
    sel_row = grid_table['selected_rows']
    
    drop_rows = [row['ShotNo'] for row in sel_row]
    df_filtered = df_tm.loc[~df_tm['ShotNo'].isin(drop_rows)]

    # st.subheader('Filtered Data')
    # st.write(df_filtered[cols].style.format(precision=1, subset=cols[3:])\
    #                                 .format(precision=0, subset=['SpinRate']))

if df_tm is not None:

    # st.subheader('Filtered data')
    # club_select = st.multiselect(label=' ',
    #                             options=list(df_filtered.sort_values(by=['ClubIdx'])['Club'].unique()))

    player = df_filtered['Player'].unique()[0]
    date = str(df_filtered['Date'].unique()[0].strftime('%m-%d-%Y'))
    location = st.session_state.location
    ball = st.session_state.ball
    
    # if len(club_select) > 0:
    if st.button('Create Report'):

        # df_specs = grid_table_specs['data']

        progress_bar = st.progress(0)

        conversions = st.secrets.conversions
        pdf = make_pdf(df_filtered, df_specs, df_comp, club_order, player, date, location, ball, progress_bar, conversions)

        pdf_title = player + ' ' + str(date) + ' Combine Report.pdf'
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
