import pandas as pd
import numpy as np
import seaborn as sns
import colorcet as cc

from fpdf import FPDF
from fpdf import Align
from matplotlib import pyplot as plt
from io import BytesIO

from data_prep import *
from plotting_functions import *


def make_pdf(df, df_specs, df_comp, club_order, player, date, location, ball, progress_bar, conversions):

    df = df[df['Club'].notnull()]

    df_avg, df_club_specs, df_specs_scatter, df_clubs, df_gap, gap_colors, gap_colors2, df_pga_comp, df_pga_plot, df_var_agg = agg_dfs(df, df_specs, club_order)
    df_club_specs.fillna('', inplace=True)


    sns.set_palette(sns.color_palette(cc.glasbey_category10, n_colors=15))

    # plot set up
    sns.set_theme()
    sns.set_palette(sns.color_palette(cc.glasbey_category10, n_colors=15))

    ######## PDF ########
    pdf = FPDF()

    progress_bar.progress(10)
    # pdf.oversized_images = "WARN"

    ### Title Page ###
    pdf.set_page_background('Dashboard/Background_full.jpg')
    pdf.add_page('L')

    pdf.image('Dashboard/logo.png', w=25, x=Align.R)

    pdf.set_font('Helvetica', 'B', 55)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(55)
    pdf.cell(txt='Tour Combine Report', w=pdf.epw, align='C')
    pdf.ln(25)

    pdf.set_font('Helvetica', 'B', 45)  
    pdf.cell(txt=player, w=pdf.epw, align='C')
    pdf.ln(20)

    pdf.set_font('Helvetica', 'B', 30)
    pdf.cell(txt=date, w=pdf.epw, align='C')
    pdf.ln(15)
    pdf.cell(txt='Location: ' + location, w=pdf.epw, align='C')
    pdf.ln(15)
    pdf.cell(txt='Golf Ball: ' + ball, w=pdf.epw, align='C')
    # pdf.ln(15)
    # pdf.cell(txt='Condition', w=pdf.epw, align='C')
    # pdf.ln(15)
    # pdf.cell(txt='Golf Ball', w=pdf.epw, align='C')

    pdf.set_page_background('Dashboard/Background.jpg')
    pdf.set_top_margin(3)

    ### Club Page ### 
    pdf.add_page('L')

    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='Club Specs', w=pdf.epw, align='C')
    pdf.ln(10)

    current_y = pdf.get_y()

    fig, ax = make_table(df_club_specs.round(1), size=(10, 10), scale=(1, 2.5), font=13)
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=pdf.epw/1.75, x=Align.L)
    img_buf.close()
    plt.close('all')
    pdf.ln(7)

    fig, ax = scatter_trend(df_specs_scatter, xcol='Loft/Length', ycol='Launch\nAngle', size=(8,5), title='Loft/Length vs LA')
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, w=pdf.epw/2.5, x=Align.R, y=current_y)
    img_buf.close()
    plt.close('all')

    fig, ax = scatter_trend(df_specs_scatter, xcol='Loft/Length', ycol='Spin\nRate', size=(8,5), title='Loft/Length vs Spin')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, w=pdf.epw/2.5, x=Align.R, y=current_y + 80) 
    img_buf.close()
    plt.close('all')

    progress_bar.progress(20)

    ### Ovr Avg Page ###
    pdf.add_page('L')

    # 1st page title
    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='Overall Averages', w=pdf.epw, align='C')
    pdf.ln(10)

    # pdf.set_font('Helvetica', 'B', 12)
    # pdf.set_text_color(0, 0, 0)
    # pdf.cell(txt=' ', w=pdf.epw / 2, align='C')
    # pdf.cell(txt='Carry Distance vs Offline', w=pdf.epw / 2, align='C')
    # pdf.ln(7)
    current_y = pdf.get_y()

    # create table for pdf
    fig, ax = make_table(df_avg.round(1), size=(10,10), scale=(1, 2.5))
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=pdf.epw/1.75, x=Align.L, y=current_y)
    img_buf.close()
    plt.close('all')
    pdf.ln(7)

    # add scatter plot

    fig, ax = scatter_conf(df_clubs, size=(6,10), title='Carry Distance vs Offline')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, h=pdf.eph - 10, x=Align.R, y=current_y)
    img_buf.close()
    plt.close('all')

    progress_bar.progress(30)
    
    if len(df['Club'].unique()) > 1:
        ### Gapping Page ###
        pdf.add_page('L')

        pdf.set_font('Helvetica', 'BU', 15)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(txt='Club Gapping', w=pdf.epw, align='C')
        pdf.ln(10)

        current_y = pdf.get_y()

        # gap table
        fig, ax = make_table(df_gap[df_gap.columns[:-5]], size=(6,12), scale=(1,2.5), font=13, gap_colors=gap_colors2)
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, h=pdf.eph - 10, x=Align.L)
        img_buf.close()
        plt.close('all')

        fig, ax = gap_steps(df_clubs, club_order, size=(9,9), title='Carry Distance Gaps')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200)
        pdf.image(img_buf, w=pdf.epw/1.6, x=Align.R, y=current_y)
        img_buf.close()
        plt.close('all')

        progress_bar.progress(40)

        ### Bend Rec Page ###
        pdf.add_page('L')

        pdf.set_font('Helvetica', 'BU', 15)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(txt='Bend Recommendations', w=pdf.epw, align='C')
        pdf.ln(15)

        current_y = pdf.get_y()

        # bend table
        gap_cols = ['Club','Carry\nStdev', 'Carry\nRange', 'Avg Carry\nDistance', 'Gap', 'Theo\nDist',
                    'Diff from\nActual', 'Bend\nLoft', 'Avg\nOffline', 'Bend\nLie']

        fig, ax = make_table(df_gap[gap_cols], size=(7,12), scale=(1,2.5), font=13, gap_colors=gap_colors)
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, h=pdf.eph - 10, x=Align.L, y=current_y)
        img_buf.close()
        plt.close('all')

        fig, ax = barchart_bend(df_gap[df_gap['Club'] != ''], 'Diff from\nActual', 'Club', loft=True, size=(7,6), title='Theoretical - Actual Carry')
        plt.tight_layout()
        img_buf = BytesIO()  
        plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
        pdf.image(img_buf, w=pdf.epw/2.6, x=Align.R, y=current_y)
        img_buf.close()
        plt.close('all')

        fig, ax = barchart_bend(df_gap[df_gap['Club'] != ''], 'Avg\nOffline', 'Club', loft=False, size=(7,6), title='Average Offline')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
        pdf.image(img_buf, w=pdf.epw/2.7, x=Align.R, y=current_y + 85) 
        img_buf.close()
        plt.close('all')

    progress_bar.progress(50)

    ### Variable Trends Page 1 ###
    pdf.add_page('L')

    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='Variable Trends', w=pdf.epw, align='C')
    pdf.ln(10)

    current_y = pdf.get_y()

    df_var = df_var_agg['SpinRate'].reset_index().rename({'mean': 'Mean', 'std': 'StDev',
                                                        'min': 'Min','max': 'Max'}, axis=1).astype({'Mean':'int', 'StDev':'int', 'Min':'int', 'Max':'int'})
    df_var['Range'] = df_var['Max'] - df_var['Min']  

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Spin Rate')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=20)
    img_buf.close()
    plt.close('all')

    df_var = df_var_agg['LaunchAngle'].reset_index().rename({'mean': 'Mean', 'std': 'StDev','min': 'Min','max': 'Max'}, axis=1).round(1)
    df_var['Range'] = (df_var['Max'] - df_var['Min']).round(1)

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Launch Angle')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=165, y=current_y)
    img_buf.close()
    plt.close('all')

    fig, ax = scatter_trend(df_avg, xcol='Launch\nAngle', ycol='Spin\nRate', size=(10,5), title=None)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=75, x=Align.C, y=current_y + 115)
    img_buf.close()
    plt.close('all')

    progress_bar.progress(60)

    ### Variable Trends Page 2 ###
    pdf.add_page('L')

    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='Variable Trends', w=pdf.epw, align='C')
    pdf.ln(10)

    current_y = pdf.get_y()

    df_var = df_var_agg['ClubSpeed'].reset_index().rename({'mean': 'Mean', 'std': 'StDev','min': 'Min','max': 'Max'}, axis=1).round(1)
    df_var['Range'] = (df_var['Max'] - df_var['Min']).round(1)    

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Club Speed')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=20)
    img_buf.close()
    plt.close('all')

    fig, ax = barchart_trend(df_avg, 'Club\nSpeed', size=(8,5), buffer=10, sigfig=0)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=75, x=Align.L, y=current_y + 115)
    img_buf.close()
    plt.close('all')

    df_var = df_var_agg['BallSpeed'].reset_index().rename({'mean': 'Mean', 'std': 'StDev','min': 'Min','max': 'Max'}, axis=1).round(1)
    df_var['Range'] = (df_var['Max'] - df_var['Min']).round(1)

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Ball Speed')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=165, y=current_y)
    img_buf.close()
    plt.close('all')

    fig, ax = barchart_trend(df_avg, 'Ball\nSpeed', size=(8,5), buffer=25, sigfig=0)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=75, x=Align.R, y=current_y + 115)
    img_buf.close()
    plt.close('all')

    progress_bar.progress(70)

    ### Variable Trends Page 3 ###
    pdf.add_page('L')

    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='Variable Trends', w=pdf.epw, align='C')
    pdf.ln(10)

    current_y = pdf.get_y()

    df_var = df_var_agg['ApexHeight'].reset_index().rename({'mean': 'Mean', 'std': 'StDev','min': 'Min','max': 'Max'}, axis=1).round(1)
    df_var['Range'] = (df_var['Max'] - df_var['Min']).round(1)

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Apex Height')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=20)
    img_buf.close()
    plt.close('all')

    fig, ax = barchart_trend(df_avg, 'Apex\nHeight', size=(8,5), buffer=10, sigfig=1)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=75, x=Align.L, y=current_y + 115)
    img_buf.close()
    plt.close('all')

    df_var = df_var_agg['LandAngle'].reset_index().rename({'mean': 'Mean', 'std': 'StDev','min': 'Min','max': 'Max'}, axis=1).round(1)
    df_var['Range'] = (df_var['Max'] - df_var['Min']).round(1)

    fig, ax = make_table(df_var, size=(6,6), scale=(1,2.5), font=13, title='Landing Angle')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=165, y=current_y)
    img_buf.close()
    plt.close('all')

    fig, ax = barchart_trend(df_avg, 'Land\nAngle', size=(8,5), buffer=10, sigfig=1)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=75, x=Align.R, y=current_y + 115)
    img_buf.close()
    plt.close('all')

    progress_bar.progress(80)

    ### PGA Comp ###
    pdf.add_page('L')

    pdf.set_font('Helvetica', 'BU', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(txt='PGA Comparison', w=pdf.epw, align='C')
    pdf.ln(10)

    current_y = pdf.get_y()

    fig, ax = make_table(df_pga_comp.round(1), size=(6,6), scale=(1,2.5), font=15)
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, dpi=200, bbox_inches='tight')
    pdf.image(img_buf, w=115, x=20, y=current_y)
    img_buf.close()
    plt.close('all')

    fig, ax = barchart_grouped(df_pga_plot, 'Carry Distance', 'variable', size=(10,5), title=None, buffer=25, sigfig=1)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, w=130, x=Align.L, y=current_y + 120)
    img_buf.close()
    plt.close('all')

    fig, ax = scatter_conf(df_clubs, title=None, incl_mean=False, conf_ell=False, df_bounds=None, size=(6,10), pga=True)
    plt.tight_layout()
    img_buf = BytesIO()  
    plt.savefig(img_buf, dpi=200, bbox_inches='tight') 
    pdf.image(img_buf, h=pdf.eph-10, x=Align.R, y=current_y)
    img_buf.close()
    plt.close('all')

    progress_bar.progress(90)

    if all(x in df_avg['Club'].unique() for x in ['Driver', '6Iron', '9Iron']):
        ### PGA Comp pg2###
        pdf.add_page('L')

        pdf.set_font('Helvetica', 'BU', 15)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(txt='PGA Comparison', w=pdf.epw, align='C')
        pdf.ln(10)
        
        avg = df_avg[df_avg['Club'] == 'Driver']['Ball\nSpeed'].values[0]
        fig, ax = comp_hist(df_comp, 1, 'var2', avg, conversions[0], sigfig=1, xlabel='Ball Speed', 
                            color='#084472', title='Driver, Ball Speed')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.L, y=current_y)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == 'Driver']['Launch\nAngle'].values[0]
        fig, ax = comp_hist(df_comp, 1, 'var3', avg, conversions[1], sigfig=1, xlabel='Launch Angle', 
                            color='#1f77b4', title='Driver, Launch Angle')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=105, y=current_y)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == 'Driver']['Spin\nRate'].values[0]
        fig, ax = comp_hist(df_comp, 1, 'var4', avg, conversions[2], sigfig=0, xlabel='Spin Rate', 
                            color='#5EB8FD', title='Driver, Spin Rate')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.R, y=current_y)
        img_buf.close()
        plt.close('all')

        pdf.line(x1=0, y1=current_y+64, x2=300, y2=current_y+64)

        avg = df_avg[df_avg['Club'] == '6Iron']['Ball\nSpeed'].values[0]
        fig, ax = comp_hist(df_comp, 2, 'var2', avg, conversions[0], sigfig=1, xlabel='Ball Speed', 
                            color='#084472', title='6 Iron, Ball Speed')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.L, y=current_y + 65)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == '6Iron']['Launch\nAngle'].values[0]
        fig, ax = comp_hist(df_comp, 2, 'var3', avg, conversions[1], sigfig=1, xlabel='Launch Angle', 
                            color='#1f77b4', title='6 Iron, Launch Angle')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=105, y=current_y + 65)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == '6Iron']['Spin\nRate'].values[0]
        fig, ax = comp_hist(df_comp, 2, 'var4', avg, conversions[2], sigfig=0, xlabel='Spin Rate', 
                            color='#5EB8FD', title='6 Iron, Spin Rate')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.R, y=current_y + 65)
        img_buf.close()
        plt.close('all')

        pdf.line(x1=0, y1=current_y+129, x2=300, y2=current_y+129)

        avg = df_avg[df_avg['Club'] == '9Iron']['Ball\nSpeed'].values[0]
        fig, ax = comp_hist(df_comp, 3, 'var2', avg, conversions[0], sigfig=1, xlabel='Ball Speed', 
                            color='#084472', title='9 Iron, Ball Speed')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.L, y=current_y + 130)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == '9Iron']['Launch\nAngle'].values[0]
        fig, ax = comp_hist(df_comp, 3, 'var3', avg, conversions[1], sigfig=1, xlabel='Launch Angle', 
                            color='#1f77b4', title='9 Iron, Launch Angle')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=105, y=current_y + 130)
        img_buf.close()
        plt.close('all')

        avg = df_avg[df_avg['Club'] == '9Iron']['Spin\nRate'].values[0]
        fig, ax = comp_hist(df_comp, 3, 'var4', avg, conversions[2], sigfig=0, xlabel='Spin Rate', 
                            color='#5EB8FD', title='9 Iron, Spin Rate')
        plt.tight_layout()
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        pdf.image(img_buf, w=90, x=Align.R, y=current_y + 130)
        img_buf.close()
        plt.close('all')

    progress_bar.progress(100)

    return pdf
