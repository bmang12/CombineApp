import time
import pandas as pd
import numpy as np

import os
import streamlit as st

from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class Ball:
    def __init__(self, name):
        self.name = name
        self.values = {}
        self.titles = []
        self.title_order = ['Club Speed', 'Ball Speed', 'Launch Ang.', 'Spin Rate', 'Carry', 'Total', 'Attack Ang.',
                            'Height', 'Land. Ang.', 'Curve', 'Club Path', 'Face Ang.', 'Smash Fac.', 'Launch Dir.',
                            'Dyn. Loft', 'Face To Path', 'Spin Axis', 'Spin Loft', 'Swing Dir.', 'Swing Pl.', 'Side',
                            'Side Tot.', 'Hang Time', 'Last Data', 'Low Point', 'From Pin', 'Target', 'Score',
                            'Eff. Stimp', 'Speed Drop', 'Roll %', 'Roll Speed', 'Skid Dist.', 'Total Break',
                            'Imp. Height', 'Imp. Offset', 'Backswing', 'Forw. Swing', 'Tempo', 'Stroke Len.',
                            'Dyn. Lie']
    def value_data(self, lines):
        titles = lines[2].split('\t')[1:]
        for row in lines[5:]:
            if row.split('\t')[0] == "":
                vals = row.split('\t')[1:]
                self.add_values(titles, vals)
        self.titles = sorted(self.titles, key=lambda x: self.title_order.index(x))
    def add_values(self, titles, vals):
        fix_nums = {'A': 1, 'B': -1, 'L':-1,'R':1}
        for i in range(len(titles)):
            if titles[i] not in self.values and titles[i] != "":
                self.values[titles[i]] = []
                self.titles.append(titles[i])
            if titles[i] != "":
                try:
                    self.values[titles[i]].append(float(vals[i]))
                except:
                    val = vals[i][0:len(vals[i])-1]
                    last = vals[i][len(vals[i])-1:]
                    if last in fix_nums:
                        self.values[titles[i]].append(float(val)*(float(fix_nums[last])))
                    else:
                        self.values[titles[i]].append('NA')
    def return_values(self, title):
        try:
            return self.values[title]
        except:
            return "NA"
    def return_vals_by_row(self, row):
        vals = []
        for x in self.titles:
            vals.append(self.values[x][row])
        return vals
    def set_club_name(self, name):
        self.club_name = name
        self.club_ball = '{0}-{1}'.format(self.club_name.strip(),self.name.strip())
    def get_title_by_col(self, col):
        try:
            return self.titles[col - 2]
        except:
            return "NA"
    def ball_num(self, num):
        self.number = num
class Club:
    def __init__(self, name):
        self.name = name
        self.balls = []
        self.ball_names = []
    def add_ball(self, ball_name):
        if ball_name not in self.ball_names:
            ball = Ball(ball_name)
            ball.set_club_name(self.name)
            ball.ball_num(len(self.balls))
            self.balls.append(ball)
            self.ball_names.append(ball_name)
    def get_ball(self, name):
        for x in self.balls:
            if x.name == name:
                return x
class Clubs:
    def __init__(self):
        self.clubs = []
        self.club_names = []
    def add_clubs(self,club_name):
        if club_name not in self.club_names:
            self.clubs.append(Club(club_name))
            self.club_names.append(club_name)
    def get_club(self, name):
        for x in self.clubs:
            if x.name == name:
                return x
class Player_Profile:
    def __init__(self, lines):
        self.name = camel_case(lines[0])
        self.date = lines[1]
        self.clubs = Clubs()
        self.add_data(lines)
    def add_data(self, lines):
        temp = []
        total = 0
        for i in range(len(lines)):
            if lines[i] == 'Hide':
                total += 1
        i = 0
        current = 0
        while i < len(lines):
            temp = []
            if lines[i + 1] == "Hide":
                current += 1
                while (lines[i].split('\t')[0].strip() != "Average"):
                    temp.append(lines[i])
                    i += 1
                self.club_data(temp)
            if current == total:
                break
            i += 1

    def club_data(self, lines):
        club_name = lines[0].split(' ')[0]
        try:
            ball_name = lines[0].split(' ', 1)[1]
        except:
            ball_name = ''
        if '-' in ball_name:
            ball_name = ball_name[ball_name.index('-')+1:]
        if club_name not in self.clubs.club_names:
            #club = Club(club_name)
            #club.add_ball(ball_name)
            self.clubs.add_clubs(club_name)
            self.clubs.get_club(club_name).add_ball(ball_name)
        else:
            for x in self.clubs.clubs:
                if x.name == club_name:
                    if ball_name not in x.ball_names:
                        x.add_ball(ball_name)
        try:
            self.clubs.get_club(club_name).get_ball(ball_name).value_data(lines)
        except:
            ''
    def titles(self):
        for x in self.clubs.clubs:
            for y in x.balls:
                return y.titles

def camel_case(word):
    words = word.split(' ')
    phrase = ""
    for x in words:
        phrase += x[0].upper()
        phrase += x[1:].lower() + ' '
    return phrase

def feet_to_yards(ft):
    return ft / 3

def delete_selenium_log():
    if os.path.exists('selenium.log'):
        os.remove('selenium.log')


def show_selenium_log():
    if os.path.exists('selenium.log'):
        with open('selenium.log') as f:
            content = f.read()
            st.code(content)

# def get_driver(options):
#     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

@st.experimental_singleton()
def scrape(url): #, _progress_bar):
    progress_bar = st.progress(0)
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')
    # chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--window-size=1920x1080')

    # options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-features=NetworkService")
    # options.add_argument("--window-size=1920x1080")
    # options.add_argument("--disable-features=VizDisplayCompositor")

    # driver = get_driver(chrome_options)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    progress = 15
    progress_bar.progress(progress)

    my_url = url
    
    if '&' not in my_url:
        main = my_url
    else:
        main = my_url[:my_url.index('&')]

    endings = []
    endings.append('&dm=c&nd=false&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=ClubSpeed&mp%5B%5D=AttackAngle&mp%5B%5D=BallSpeed&mp%5B%5D=LaunchAngle&mp%5B%5D=SpinRate&mp%5B%5D=Carry&mp%5B%5D=Total&mp%5B%5D=Height&mp%5B%5D=LandingAngle&mp%5B%5D=Curve&u=Us&v=dispersion')
    endings.append('&dm=c&nd=false&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=LaunchDirection&mp%5B%5D=ClubPath&mp%5B%5D=DynamicLoft&mp%5B%5D=FaceAngle&mp%5B%5D=FaceToPath&mp%5B%5D=SmashFactor&mp%5B%5D=SpinAxis&mp%5B%5D=SpinLoft&mp%5B%5D=SwingDirection&mp%5B%5D=SwingPlane&u=Us&v=dispersion')
    endings.append('&dm=c&nd=false&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=Side&mp%5B%5D=SideTotal&mp%5B%5D=HangTime&mp%5B%5D=LastData&mp%5B%5D=LowPointDistance&mp%5B%5D=DistanceToPin&mp%5B%5D=DistanceToTarget&mp%5B%5D=Score&mp%5B%5D=EffectiveStimp&mp%5B%5D=SpeedDrop&u=Us&v=dispersion')
    endings.append('&dm=c&nd=false&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=RollPercentage&mp%5B%5D=RollSpeed&mp%5B%5D=SkidDistance&mp%5B%5D=TotalBreak&mp%5B%5D=ImpactHeight&mp%5B%5D=ImpactOffset&mp%5B%5D=BackswingTime&mp%5B%5D=ForwardswingTime&mp%5B%5D=Tempo&mp%5B%5D=StrokeLength&u=Us&v=dispersion')
    endings.append('&dm=c&nd=false&op=true&sro=false&do=true&to=true&vo=true&cdo=true&ot=c&ov=d&mp%5B%5D=DynamicLie&u=Us&v=dispersion')

    clubData ={}
    clubTypes = []
    iter = 0

    while iter < len(endings):
        url = main + endings[iter]
        driver.get(url)
        time.sleep(2)
        text = driver.execute_script("return document.documentElement.innerText;")
        time.sleep(2)
        lines = []
        for i in text.split('\n'):
            if i != "":
                lines.append(i)
        if iter == 0:
            player_data = Player_Profile(lines)
        else:
            player_data.add_data(lines)
        iter += 1

        progress += 15
        progress_bar.progress(progress)

    df_scrape = pd.DataFrame(columns=['Club', 'Club Speed', 'Ball Speed', 'Launch Ang.', 'Spin Rate', 'Carry',
                                  'Total', 'Height', 'Attack Ang.', 'Land. Ang.', 'Curve', 'Launch Dir.',
                                  'Spin Axis', 'Smash Fac.', 'Club Path', 'Dyn. Loft', 'Face Ang.',
                                  'Face To Path', 'Spin Loft', 'Swing Dir.', 'Swing Pl.', 'Side',
                                  'Side Tot.', 'Hang Time', 'Last Data', 'Low Point', 'From Pin',
                                  'Target', 'Score', 'Eff. Stimp', 'Speed Drop', 'Roll %', 'Roll Speed',
                                  'Skid Dist.', 'Total Break', 'Imp. Height', 'Imp. Offset', 'Backswing',
                                  'Forw. Swing', 'Tempo', 'Stroke Len.', 'Dyn. Lie'])

    player = player_data.name
    date = player_data.date

    for club in player_data.clubs.clubs:
        for ball in club.balls:
            df_new = pd.DataFrame(ball.values)
            df_new['Club'] = ball.club_name
            df_scrape = pd.concat([df_scrape, df_new])

    df_scrape['Player'] = player
    df_scrape['Date'] = date
    df_scrape['Shot No'] = list(range(1, len(df_scrape) + 1))
    df_scrape['TMD No'] = None
    df_scrape['Ball'] = None

    df_scrape['Use In Stat'] = 'Yes'
    df_scrape['Tags'] = ''
    df_scrape['Spin Rate Type'] = ''
    df_scrape[['Dist.', 'Length', 'Side.1', 
            'Height.1', 'Time', 'Ball Speed.1']] = np.nan
    
    df_scrape[['Height', 'Side', 'Side Tot.']] = df_scrape[['Height', 'Side', 'Side Tot.']].apply(feet_to_yards)
    
    df_scrape.loc[df_scrape['Club'] == 'Pitching Wedge', 'Club'] = 'PW'
    df_scrape.loc[df_scrape['Club'] == 'Sand Wedge', 'Club'] = 'SW'
    df_scrape.loc[df_scrape['Club'] == 'Lob Wedge', 'Club'] = 'LW'

    df_scrape = df_scrape[~df_scrape['Player'].isna()]

    df_scrape.drop(df_scrape[df_scrape['Use In Stat'].isna()].index, inplace=True)

    df_scrape['Date'] = pd.to_datetime(df_scrape['Date']).dt.date

    df_scrape.rename(columns={'Attack Ang.': 'Attack Angle',
                            'Swing Pl.': 'Swing Plane',
                            'Swing Dir.': 'Swing Direction',
                            'Face Ang.': 'Face Angle',
                            'Smash Fac.': 'Smash Factor',
                            'Launch Ang.': 'Launch Angle',
                            'Launch Dir.': 'Launch Direction',
                            'Carry': 'Length.1',
                            'Side': 'Side.2',
                            'Land. Ang.': 'Vert. Angle',
                            'Hang Time': 'Flight Time',
                            'Total': 'Length.2',
                            'Side Tot.': 'Side.3'}, inplace=True)

    df_scrape['Side'] = np.nan

    cols = []
    for column in df_scrape.columns:
        if pd.isna(column):
            df_scrape.drop(column, axis=1, inplace=True)
        # if column == True:
        #     df_scrape.drop(column, axis=1, inplace=True)
        cols.append(column.replace(' ', '').replace('-', ','))
    df_scrape.columns = cols

    columns_num = ['ShotNo', 'ClubSpeed', 'AttackAngle', 'ClubPath', 'LowPoint', 'SwingPlane', 'SwingDirection',
                    'Dyn.Loft', 'FaceAngle', 'SmashFactor', 'BallSpeed', 'SmashFactor', 'LaunchAngle',
                    'LaunchDirection', 'SpinRate', 'SpinAxis', 'Dist.', 'Height', 'Side', 'Length',
                    'Side.1', 'Height.1', 'Time', 'Length.1', 'Side.2', 'Vert.Angle', 'BallSpeed.1',
                    'FlightTime', 'Length.2', 'Side.3']

    df_scrape.replace('NA', None, inplace=True)

    # convert the columns to numeric data types
    for col in columns_num:
        df_scrape[col] = pd.to_numeric(df_scrape[col])

    df_scrape['SpinAxis'] = np.deg2rad(df_scrape['SpinAxis'])


    # create roll distance variable (total distance - carry distance)
    df_scrape['RollDistance'] = df_scrape['Length.2'] - df_scrape['Length.1']

    # calculate sidespin and backspin with given equations
    df_scrape['Sidespin'] = np.sin(df_scrape['SpinAxis']) * df_scrape['SpinRate']
    df_scrape['Backspin'] = np.cos(df_scrape['SpinAxis']) * df_scrape['SpinRate']

    # rename poorly named columns
    df_scrape.rename(columns={'Vert.Angle': 'LandAngle',
                        'Dist.': 'ApexDownrange',
                        'Height': 'ApexHeight',
                        'Length.1': 'CarryDistance',
                        'Side.2': 'CarryOffLine',
                        'Length.2': 'TotalDistance',
                        'Side.3': 'TotalOffLine',
                        'Dyn.Loft': 'DynamicLoft'}, inplace=True)

    df_scrape.loc[df_scrape['Club'].replace(' ', '') == 'PitchingWedge', 'Club'] = 'PW'
    df_scrape.loc[df_scrape['Club'].replace(' ', '') == 'SandWedge', 'Club'] = 'SW'
    df_scrape.loc[df_scrape['Club'].replace(' ', '') == 'LobWedge', 'Club'] = 'LW'

    df_scrape.loc[df_scrape['Club'].str.contains('50'), 'Club'] = '50° Wedge'
    df_scrape.loc[df_scrape['Club'].str.contains('52'), 'Club'] = '52° Wedge'
    df_scrape.loc[df_scrape['Club'].str.contains('54'), 'Club'] = '54° Wedge'
    df_scrape.loc[df_scrape['Club'].str.contains('56'), 'Club'] = '56° Wedge'
    df_scrape.loc[df_scrape['Club'].str.contains('58'), 'Club'] = '58° Wedge'
    df_scrape.loc[df_scrape['Club'].str.contains('60'), 'Club'] = '60° Wedge'

    df_scrape = df_scrape.round(2)

    df_scrape['Club'] = df_scrape['Club'].str.replace(' ', '')

    clubs_all = ['Driver', '2Wood', '3Wood', '4Wood', '5Wood', '6Wood', '7Wood',
                '8Wood', '9Wood', '1Hybrid', '2Hybrid', '3Hybrid', '4Hybrid',
                '5Hybrid', '6Hybrid', '7Hybrid', '8Hybrid', '9Hybrid', '1Iron',
                '2Iron', '3Iron', '4Iron', '5Iron', '6Iron', '7Iron', '8Iron',
                '9Iron', 'PW', 'SW', 'LW', '50°Wedge', '52°Wedge', '54°Wedge', 
                '56°Wedge', '58°Wedge', '60°Wedge']

    club_order = {key: i for i, key in enumerate(clubs_all)}

    df_scrape['ClubIdx'] = df_scrape['Club'].str.replace(' ', '').map(club_order)

    progress_bar.progress(100)

    return(df_scrape, club_order)
