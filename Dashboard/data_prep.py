import pandas as pd
import numpy as np

def feet_to_yards(ft):
    return ft / 3

def read_data(file):
    excel = pd.ExcelFile(file)
    sheets = excel.sheet_names

    columns = ['Date', 'Shot No', 'TMD No', 'Player', 'Club', 'Ball',
            'Club Speed', 'Attack Angle', 'Club Path', 'Low Point',
            'Swing Plane', 'Swing Direction', 'Dyn. Loft', 'Face Angle',
            'Ball Speed', 'Smash Factor', 'Launch Angle', 'Launch Direction',
            'Spin Rate', 'Spin Rate Type', 'Spin Axis', 'Dist.', 'Height',
            'Side', 'Length', 'Side.1', 'Height.1', 'Time', 'Length.1',
            'Side.2', 'Vert. Angle', 'Ball Speed.1', 'Flight Time',
            'Length.2', 'Side.3', 'Use In Stat', 'Tags']

    if 'Report' in sheets:
        df_tm = pd.read_excel(excel, sheet_name='Report', header=1).drop(0, axis=0)
        df_tm.reset_index(drop=True, inplace=True)
        # rename columns to keep consistency
        df_tm.rename(columns={'Unnamed: 36': 'Tags', 'Club\nPath': 'Club Path', 'Dyn. \nLoft': 'Dyn. Loft',
                                'Spin\nRate': 'Spin Rate', 'Swing Direction ': 'Swing Direction'}, inplace=True)

    elif 'Result' in sheets:
        df_tm = pd.read_excel(excel, sheet_name='Result', header=1).drop([0, 1, 2, 3, 4], axis=0)
        df_tm = df_tm.drop(df_tm.columns[12], axis=1)
        df_tm.reset_index(drop=True, inplace=True)
        df_tm['TMD No'] = np.nan
        df_tm['Low Point'] = np.nan
        df_tm['Use In Stat'] = 'Yes'

        df_tm['Shot No'] = list(range(1, len(df_tm) + 1))
        
        # executing the function
        df_tm[['Height', 'Side', 'Side.1',
                    'Height.1', 'Side.2', 'Side.3']] = df_tm[['Height', 'Side', 'Side.1',
                                                                'Height.1', 'Side.2', 'Side.3']].apply(feet_to_yards)

        df_tm.rename(columns={'Unnamed: 13': 'Player',
                                'Spin\nRate': 'Spin Rate',
                                'Dynamic Loft': 'Dyn. Loft'}, inplace=True)

        if df_tm['Tags'].isnull().all():
            df_tm['Tags'] = df_tm['CustomClub']

        df_tm[columns] = df_tm[columns].replace({True: np.nan})

    df_tm.loc[df_tm['Club'] == 'Pitching Wedge', 'Club'] = 'PW'
    df_tm.loc[df_tm['Club'] == 'Sand Wedge', 'Club'] = 'SW'
    df_tm.loc[df_tm['Club'] == 'Lob Wedge', 'Club'] = 'LW'

    df_tm = df_tm[~df_tm['Player'].isna()]

    if df_tm['Club'].isnull().values.any():
        print('Please check that all Clubs types are not null for:')
        for player_null in df_tm[df_tm['Club'].isnull()]['Player'].unique():
            print(player_null)
        quit()

    df_tm['Tags'] = df_tm['Tags'].fillna('')

    df_tm['Tags'] = df_tm['Tags'].str.replace('&#46;', '.', regex=True)

    # drop the rows that were identified to not be kept by the trackman operator
    df_tm.drop(df_tm[df_tm['Use In Stat'].isna()].index, inplace=True)

    df_tm['Date'] = pd.to_datetime(df_tm['Date']).dt.date

    df_tm = df_tm[columns]

    df_tm = df_tm.loc[:, df_tm.columns.notna()]

    cols = []
    for column in df_tm.columns:
        if pd.isna(column):
            df_tm.drop(column, axis=1, inplace=True)
        cols.append(column.replace(' ', '').replace('-', ','))
    df_tm.columns = cols

    columns_num = ['ShotNo', 'ClubSpeed', 'AttackAngle', 'ClubPath', 'LowPoint', 'SwingPlane', 'SwingDirection',
                    'Dyn.Loft', 'FaceAngle', 'SmashFactor', 'BallSpeed', 'SmashFactor', 'LaunchAngle',
                    'LaunchDirection', 'SpinRate', 'SpinAxis', 'Dist.', 'Height', 'Side', 'Length',
                    'Side.1', 'Height.1', 'Time', 'Length.1', 'Side.2', 'Vert.Angle', 'BallSpeed.1',
                    'FlightTime', 'Length.2', 'Side.3']

    # convert the columns to numeric data types
    for col in columns_num:
        df_tm[col] = pd.to_numeric(df_tm[col])

    df_tm['SpinAxis'] = np.deg2rad(df_tm['SpinAxis'])


    # create roll distance variable (total distance - carry distance)
    df_tm['RollDistance'] = df_tm['Length.2'] - df_tm['Length.1']

    # calculate sidespin and backspin with given equations
    df_tm['Sidespin'] = np.sin(df_tm['SpinAxis']) * df_tm['SpinRate']
    df_tm['Backspin'] = np.cos(df_tm['SpinAxis']) * df_tm['SpinRate']

    # rename poorly named columns
    df_tm.rename(columns={'Vert.Angle': 'LandAngle',
                        'Dist.': 'ApexDownrange',
                        'Height': 'ApexHeight',
                        'Length.1': 'CarryDistance',
                        'Side.2': 'CarryOffLine',
                        'Length.2': 'TotalDistance',
                        'Side.3': 'TotalOffLine',
                        'Dyn.Loft': 'DynamicLoft'}, inplace=True)

    df_tm.loc[df_tm['Club'].replace(' ', '') == 'PitchingWedge', 'Club'] = 'PW'
    df_tm.loc[df_tm['Club'].replace(' ', '') == 'SandWedge', 'Club'] = 'SW'
    df_tm.loc[df_tm['Club'].replace(' ', '') == 'LobWedge', 'Club'] = 'LW'

    df_tm.loc[df_tm['Club'].str.contains('50'), 'Club'] = '50° Wedge'
    df_tm.loc[df_tm['Club'].str.contains('52'), 'Club'] = '52° Wedge'
    df_tm.loc[df_tm['Club'].str.contains('54'), 'Club'] = '54° Wedge'
    df_tm.loc[df_tm['Club'].str.contains('56'), 'Club'] = '56° Wedge'
    df_tm.loc[df_tm['Club'].str.contains('58'), 'Club'] = '58° Wedge'
    df_tm.loc[df_tm['Club'].str.contains('60'), 'Club'] = '60° Wedge'

    df_tm = df_tm.round(2)

    clubs_all = ['Driver', '2Wood', '3Wood', '4Wood', '5Wood', '6Wood', '7Wood',
                '8Wood', '9Wood', '1Hybrid', '2Hybrid', '3Hybrid', '4Hybrid',
                '5Hybrid', '6Hybrid', '7Hybrid', '8Hybrid', '9Hybrid', '1Iron',
                '2Iron', '3Iron', '4Iron', '5Iron', '6Iron', '7Iron', '8Iron',
                '9Iron', 'PW', 'SW', 'LW', '50°Wedge', '52°Wedge', '54°Wedge', 
                '56°Wedge', '58°Wedge', '60°Wedge']

    club_order = {key: i for i, key in enumerate(clubs_all)}

    df_tm['ClubIdx'] = df_tm['Club'].str.replace(' ', '').map(club_order)

    return df_tm, club_order


def summarize_data(df, club_order):
   
    df_groupby = df.groupby('Club', sort=False).mean().reset_index()
    df_groupby['Spin/LA'] = df_groupby['SpinRate'] / df_groupby['LaunchAngle']

    cols = ['Club', 'ClubSpeed', 'AttackAngle', 'ClubPath', 'BallSpeed', 'LaunchAngle',
            'SpinRate', 'Spin/LA', 'CarryDistance', 'CarryOffLine', 'ApexHeight', 'LandAngle']
    groupby_data = df_groupby[cols].values

    ## Creating table
    table_cols = ['Club', 'Club\nSpeed', 'Attack\nAngle', 'Club\nPath', 'Ball\nSpeed', 'Launch\nAngle',
                  'Spin\nRate', 'Spin/LA', 'Carry\nDistance', 'Carry\nOffLine', 'Apex\nHeight', 'Land\nAngle']
    df_avg = pd.DataFrame(groupby_data, columns=table_cols)
    df_avg[['Model', 'Loft', 'Lie', 'Length', 'Shaft', 'SW', 'Target\nCarry', 'Loft/Length']] = None
    df_avg = df_avg[['Club', 'Model', 'Loft', 'Lie', 'Length', 'Shaft', 'SW', 'Target\nCarry', 'Loft/Length'] + table_cols[1:]]
    # USER ENTRY HERE
    # df_avg['Model'] = ['Epic Speed Max LS', 'Mavrik', 'Apex Pro 19', 'Apex TCB', 'Apex TCB', 'Apex TCB', 'Apex TCB', 
    #                    'Apex TCB', 'Apex TCB', 'Apex TCB', 'Jaws MD5 raw', 'Jaws MD5 raw', 'Jaws MD5 raw']
    # df_avg['Loft'] = [10.5, 16.5, 20, 24, 26, 29.5, 33, 37, 41, 45, 50, 54, 60]
    # df_avg['Lie'] = [57.8, 56.4, 59.2, 59.7, 61.5, 62, 62.5, 63, 63.5, 64, 64, 64.3, 64.4]
    # df_avg['Length'] = [45, 42.75, 39.75, 38.5, 38, 37.5, 37, 36.5, 36, 35.75, 35.75, 35.5, 35.125]
    # df_avg['Shaft'] = ['Tensei White CK 70TTX', 'Fuji Ventus Black 8x', 'DG X100 X7', 'DG X100 TI', 'DG X100 TI', 
    #                    'DG X100 TI', 'DG X100 TI', 'DG X100 TI', 'DG X100 TI', 'DG X100 TI', 'DG X7', 'DG X7', 'DG X7']
    # df_avg['SW'] = ['D5', 'D3', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D2', 'D3.5', 'D4', 'D4.5']
    # df_avg['Model'] = 'Test Model'
    # df_avg['Loft'] = 10
    # df_avg['Lie'] = 60
    # df_avg['Length'] = 37
    # df_avg['Shaft'] = 'Test Shaft'
    # df_avg['SW'] = 'D2'
    # df_avg['Target\nCarry'] = ''
    # # df_avg['Loft/Length'] = 0
    # df_avg['Loft/Length'] = (df_avg['Loft'] / df_avg['Length'])
    # df_avg['Loft/Length'] = [0.5822, 0.6315, 0.7333, 0.7837, 0.9315, 1.0555]

    # num_cols = ['Loft/Length', 'Club\nSpeed', 'Attack\nAngle', 'Club\nPath', 'Ball\nSpeed', 'Launch\nAngle',
    #             'Spin\nRate', 'Spin/LA', 'Carry\nDistance', 'Carry\nOffLine', 'Apex\nHeight', 'Land\nAngle']
    num_cols = ['Club\nSpeed', 'Attack\nAngle', 'Club\nPath', 'Ball\nSpeed', 'Launch\nAngle', 'Spin\nRate', 
                'Spin/LA', 'Carry\nDistance', 'Carry\nOffLine', 'Apex\nHeight', 'Land\nAngle']
    
    df_avg[num_cols] = df_avg[num_cols].astype(float)

    df_avg['ClubIdx'] = df_avg['Club'].str.replace(' ', '').map(club_order)
    df_avg = df_avg.sort_values('ClubIdx')
    
    return df_avg



def agg_dfs(df, df_club_specs, club_order):
    # Overall df filtered by clubs selected for analysis
    clubs = df.sort_values(by=['ClubIdx'])['Club'].unique()

    df_clubs = df[df['Club'].isin(clubs)].sort_values(by=['ClubIdx'])
    df_clubs['CarryOffLine_plot'] = df_clubs['CarryOffLine'] * -1

    # create avg dfs
    df_avg = summarize_data(df_clubs, club_order)

    # club_cols = ['Club', 'Model', 'Loft', 'Lie', 'Length', 
    #             'Shaft', 'SW', 'Target\nCarry', 'Loft/Length']
    metric_cols = ['Club', 'Club\nSpeed', 'Attack\nAngle', 'Club\nPath',
                'Ball\nSpeed', 'Launch\nAngle', 'Spin\nRate', 'Spin/LA', 
                'Carry\nDistance', 'Carry\nOffLine', 'Apex\nHeight', 'Land\nAngle']

    # df_club_specs = df_avg[club_cols]

    for col in df_club_specs.columns:
        df_club_specs[col] = df_club_specs[col].replace('None', None)
    df_club_specs[['Loft', 'Lie', 'Length']] = df_club_specs[['Loft', 'Lie', 'Length']].astype(float)
    df_club_specs['Loft/Length'] = df_club_specs['Loft'] / df_club_specs['Length']

    df_avg = df_avg[metric_cols]
    df_specs_scatter = df_avg.copy()
    df_specs_scatter['Loft/Length'] = df_club_specs['Loft/Length'] 

    # gap table
    df_clubs.reset_index(inplace=True, drop=True)
    carry_club =  df_clubs.groupby('Club', sort=False).agg({'CarryOffLine': 'mean', 'CarryDistance': [np.std, 'min', 'max', 'mean']}).reset_index().round(1).values

    gap_table_cols = ['Club', 'Avg\nOffline', 'Carry\nStdev', 'Carry\nRange', 'Avg Carry\nDistance', 'Gap', 'Ideal']

    carry_gap_table = []

    for idx in range(len(carry_club)):
        this_row = list(carry_club[idx])
        
        range_ = round(this_row[4] - this_row[3], 1)
        this_row[4] = range_
        this_row.pop(3)

        this_row.append('')
        this_row.append('')
        carry_gap_table.append(this_row)

        if idx != len(carry_club) - 1:
            gap = round(this_row[4] - list(carry_club[idx + 1])[5], 1)
            
            if this_row[0] == 'Driver' or 'Wood' in this_row[0]:
                ideal = 25
            elif 'Iron' in this_row[0]:
                ideal = 15
            elif 'W' in this_row[0]:
                ideal = 10
            else: 
                ideal = 0

            gap_row = ['', '', '', '', '', gap, ideal]
            carry_gap_table.append(gap_row)

    df_gap = pd.DataFrame(carry_gap_table, columns=gap_table_cols)

    ### CHANGE ###
    df_gap['Theo\nDist'] = pd.Series([299.3, '', 269.3, '', 239.3, '', 224.3, '', 209.3, '', 194.3, '', 179.3, '', 164.3, '', 149.3, '', 134.3, '', 119.3, '', 104.3, '', 89.3])
    df_gap['Diff from\nActual'] = (df_gap['Avg Carry\nDistance'].replace('', 99999) - df_gap['Theo\nDist'].replace('', 0)).round(1)
    df_gap['Diff from\nActual'].replace(99999, '', inplace=True)

    df_gap['Bend\nLoft'] = 'OK'
    df_gap['Bend\nLie'] = 'OK'

    df_gap.loc[df_gap['Diff from\nActual'].replace('', 0) >= 5, 'Bend\nLoft'] = 'WEAKEN'
    df_gap.loc[df_gap['Diff from\nActual'].replace('', 0) <= -5, 'Bend\nLoft'] = 'STRENGTHEN'

    df_gap.loc[df_gap['Avg\nOffline'].replace('', 0) >= 5, 'Bend\nLie'] = 'MOVE UPRIGHT'
    df_gap.loc[df_gap['Avg\nOffline'].replace('', 0) <= -5, 'Bend\nLie'] = 'MOVE FLAT'

    df_gap.loc[df_gap['Club'] == '', ['Bend\nLoft', 'Bend\nLie']] = ''

    # df_gap = df_gap.style.apply(loft_lie_highlight, subset=['Bend\nLoft', 'Bend\nLie'], axis=1)

    gap_colors = []
    for _, row in df_gap.iterrows():
        colors_in_column = ['w'] * 10
        if row['Bend\nLoft'] in ['STRENGTHEN', 'WEAKEN']:
            colors_in_column[7] = '#bcbd22'
        if row['Bend\nLie'] in ['MOVE UPRIGHT', 'MOVE FLAT']:
            colors_in_column[9] = '#bcbd22'
        if row['Club'] == '':
            colors_in_column = ['#C5C5C5'] * 10
        colors_in_column[0] = '#AEAEAE'
        gap_colors.append(colors_in_column)

    gap_colors2 = []
    for _, row in df_gap.iterrows():
        colors_in_column2 = ['w'] * 6
        if row['Club'] == '':
            colors_in_column2 = ['#C5C5C5'] * 6
        if row['Gap'] != '':
            if float(row['Gap']) < 10:
                colors_in_column2[5] = '#bcbd22'
        colors_in_column2[0] = '#AEAEAE'
        gap_colors2.append(colors_in_column2)

    pga_carry = {'Driver': 283, 
                 '3Wood': 252, 
                 '4Wood': 259,
                 '5Wood': 235,
                 '2Hybrid': 244,
                 '3Hybrid': 222,
                 '2Iron': 248,
                 '3Iron': 222,
                 '4Iron': 216,
                 '5Iron': 201,
                 '6Iron': 190,
                 '7Iron': 173,
                 '8Iron': 163,
                 '9Iron': 147,
                 'PW': 138,
                 '50° Wedge': 122,
                 '52° Wedge': 119,
                 '54° Wedge': 112,
                 '56° Wedge': 105,
                 '58° Wedge': 104,
                 '60° Wedge': 96,
                 } 

    df_pga_comp = df_avg.loc[:, ['Club', 'Carry\nOffLine', 'Carry\nDistance']]
    df_pga_comp['PGA Avg\nCarry'] = df_pga_comp['Club'].map(pga_carry)
    df_pga_comp['Diff'] = (df_pga_comp['Carry\nDistance'] - df_pga_comp['PGA Avg\nCarry'])

    df_pga_plot = df_pga_comp[['Club', 'Carry\nDistance', 'PGA Avg\nCarry']].melt(id_vars='Club').rename(columns={'value': 'Carry Distance'})
    df_pga_plot['variable'] = df_pga_plot['variable'].str.replace('Carry\nDistance', 'Avg').str.replace('PGA Avg\nCarry', 'PGA Avg')

    df_var_agg = df_clubs.groupby('Club', sort=False).agg({'SpinRate': ['mean', np.std, 'min', 'max'], 
                                                           'LaunchAngle': ['mean', np.std, 'min', 'max'],
                                                           'ClubSpeed': ['mean', np.std, 'min', 'max'],
                                                           'BallSpeed': ['mean', np.std, 'min', 'max'],
                                                           'ApexHeight': ['mean', np.std, 'min', 'max'],
                                                           'LandAngle': ['mean', np.std, 'min', 'max']})

    return df_avg, df_club_specs, df_specs_scatter, df_clubs, df_gap, gap_colors, gap_colors2, df_pga_comp, df_pga_plot, df_var_agg
