import pandas as pd
import numpy as np
import seaborn as sns
import io
import colorcet as cc
import matplotlib.transforms as transforms

from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Ellipse
from scipy import stats


def loft_lie_highlight(row):    

    highlight = 'background-color: #bcbd22;'
    default = ''

    # must return one string per cell in this row
    if row['Bend\nLoft'] in ['STRENGTHEN', 'WEAKEN'] and row['Bend\nLie'] in ['MOVE UPRIGHT', 'MOVE FLAT']:
        return [highlight, highlight]
    elif row['Bend\nLoft'] in ['STRENGTHEN', 'WEAKEN'] and row['Bend\nLie'] == 'OK':
        return [highlight, default]
    elif row['Bend\nLoft'] == 'OK' and row['Bend\nLie'] in ['MOVE UPRIGHT', 'MOVE FLAT']:
        return [default, highlight]
    else:
        return [default, default]


def make_table(df, size=(5, 10), title=None, scale=(1, 1.5), font=None, gap_colors=None):
    fig, ax = plt.subplots(figsize=size)

    fig.patch.set_visible(False)
    ax.axis('off')
    # ax.axis('tight')

    if 'Spin\nRate' in df.columns:
        df['Spin\nRate'] = df['Spin\nRate'].astype(int)
        df['Spin/LA'] = df['Spin/LA'].astype(int)

    if gap_colors is not None:
        table = ax.table(cellText=df.values, 
                        colLabels=df.columns, 
                        loc='upper center',
                        cellLoc='center',
                        cellColours=gap_colors, 
                        colColours=['#AEAEAE'] * len(df.columns)
                        #colWidths=[.25] * len(df_trends.columns)
                        )
    else:
        colors_in_column = ['w'] * len(df.columns)
        colors_in_column[0] = '#AEAEAE'
        header_colors = [colors_in_column] * len(df)

        table = ax.table(cellText=df.values, 
                colLabels=df.columns, 
                loc='upper center',
                cellLoc='center',
                cellColours=header_colors,
                colColours=['#AEAEAE'] * len(df.columns)
                #colWidths=[.25] * len(df_trends.columns)
                )

    if font is not None:
        table.set_fontsize(font)
    else:
        table.auto_set_font_size(True)

    for i in range(len(df.columns)):
        table.auto_set_column_width(i)
    
    table.scale(scale[0], scale[1])

    for (row, col), cell in table.get_celld().items():
        if (row == 0) or (col == 0):
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
            cell.set_fontsize(13)

    if title is not None:
        ax.set_title(title, fontsize=20, fontweight='bold')
    # fig.tight_layout()

    return fig, ax


def scatter_all(df, orientation='P'):
    # create ordering list for legend
    legend_order = list(df.sort_values(by='ClubIdx')['Club'].unique())

    if orientation == 'P':

        fig, ax = plt.subplots(figsize=(7, 10))

        # plot points and add legend
        sns.scatterplot(data=df, x='CarryOffLine', y='CarryDistance', hue='Club', hue_order=legend_order, s=75)
        plt.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0)

        # plot formatting
        xmax = max(abs(df['CarryOffLine']))
        ax.set_xlim(-xmax - 5, xmax + 5)
        ax.set_xlabel('Carry Offline (yds)')
        ax.set_ylabel('Carry Distance (yds)')
        
        plt.axvline(x=0, linestyle='--', color='grey')
    
    if orientation == 'L':
        
        fig, ax = plt.subplots(figsize=(15, 4))

        # plot points and add legend
        sns.scatterplot(data=df, x='CarryDistance', y='CarryOffLine_plot', hue='Club', hue_order=legend_order, s=75)
        plt.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0)

        # plot formatting
        ymax = max(abs(df['CarryOffLine_plot']))
        ax.set_ylim(-ymax - 5, ymax + 5)
        ax.set_ylabel('Carry Offline (yds)')
        ax.set_xlabel('Carry Distance (yds)')

        plt.axhline(y=0, linestyle='--', color='grey')

    # return plot
    return fig, ax


def scatter_means(df, club_order):
    # group by club and calculate the means
    df_means = df.groupby('Club').mean().reset_index()

    # create new index variable and sort
    df_means['ClubIdx'] = df_means['Club'].str.replace(' ', '').map(club_order)
    df_means.sort_values(by=['ClubIdx'], inplace=True)

    # create ordering list for legend
    legend_order = list(df_means.sort_values(by='ClubIdx')['Club'].unique())
    fig, ax = plt.subplots(figsize=(7, 10))

    # plot points and add legend
    sns.scatterplot(data=df_means, x='CarryOffLine', y='CarryDistance', hue='Club', hue_order=legend_order, s=75)
    plt.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0)

    # plot formatting
    xmax = max(abs(df['CarryOffLine']))
    ax.set_xlim(-xmax - 5, xmax + 5)

    plt.axvline(x=0, linestyle='--', color='grey')

    # return plot
    return fig, ax


def gap_steps(df, club_order, size=(5,10), title=None):
    # group by club and calculate the means
    df_means = df.groupby('Club').mean().reset_index().round(1)

    # create new index variable and sort
    df_means['ClubIdx'] = df_means['Club'].str.replace(' ', '').map(club_order)
    df_means.sort_values(by=['ClubIdx'], inplace=True)

    # create ordering list for legend
    legend_order = list(df_means.sort_values(by='ClubIdx')['Club'].unique())
    fig, ax = plt.subplots(figsize=size)

    # plot points and add legend
    sns.scatterplot(data=df_means, x='Club', y='CarryDistance', hue='Club', hue_order=legend_order, s=75, legend=False)
    sns.lineplot(data=df_means, x='Club', y='CarryDistance', sort=False, drawstyle='steps-pre')

    # label points on the plot
    for x, y in zip(df_means['Club'], df_means['CarryDistance']):
        plt.text(x = x,
                 y = y+3, 
                 s = '{:.0f}'.format(y),
                 fontsize=13,
                 weight='bold')
    for i in range(len(df_means)):
        if i != len(df_means) - 1:
            diff = df_means.iloc[i]['CarryDistance'] - df_means.iloc[i + 1]['CarryDistance']
            plt.text(x = df_means.iloc[i]['Club'], 
                     y = df_means.iloc[i]['CarryDistance'] - (diff / 2), 
                     s = ' {:.1f}'.format(diff),
                     fontsize=15,
                     style='italic')

    # plot formatting
    plt.xticks(rotation=45)

    ax.set_xlabel('Club', fontsize = 13, fontweight ='bold')
    ax.set_ylabel('Carry Distance (yds)', fontsize = 13, fontweight ='bold')

    ax.tick_params(axis='both', which='major', labelsize=13)
    ax.tick_params(axis='both', which='minor', labelsize=13)

    if title is not None:
        ax.set_title(title, fontsize=17, fontweight='bold')

    # return plot
    return fig, ax


def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', label_list=[], **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    facecolor: string
        The color of the ellipse

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)

    # Calculating the standard deviation of x from
    # the square root of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    label = np.pi * (scale_x * ell_radius_x) * (scale_y * ell_radius_y)
    label_list.append(label)

    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs, label=str(round(label)) + ' sqyd')

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)

    return ax.add_patch(ellipse)


def scatter_conf(df, title=None, incl_mean=True, conf_ell=True, df_bounds=None, size=(15,4), pga=False):
    colors = sns.color_palette(sns.color_palette(cc.glasbey_category10, n_colors=15)).as_hex()
    
    # # create ordering list for legend
    # legend_order = list(df.sort_values(by='ClubIdx')['Club'].unique())

    fig, ax = plt.subplots(figsize=size)

    clubs = df.sort_values(by=['ClubIdx'])['Club'].unique()
    for i in range(len(clubs)):
        carry = df[df['Club'] == clubs[i]]['CarryDistance']
        offline = df[df['Club'] == clubs[i]]['CarryOffLine']
        # plot points and add legend
        ax.scatter(x=offline, y=carry, label=clubs[i], color=colors[i])
        if incl_mean:
            ax.scatter(x=offline.mean(), y=carry.mean(), c=colors[i], s=100, marker='P', alpha=0.5, edgecolors='black', linewidths=1)
        if conf_ell:
            confidence_ellipse(offline, carry, ax, n_std=1.7941, edgecolor=colors[i], label_list=[])
        # plt.legend(bbox_to_anchor=(1.02, .75), loc='upper left', borderaxespad=0)

    handles, labels = ax.get_legend_handles_labels()
    # handles = handles[::-1]
    # labels = labels[::-1]
    # if conf_ell:
    #     for i in range(0, len(handles), 2):
    #         handles[i], handles[i+1] = handles[i+1], handles[i] 
    #         labels[i], labels[i+1] = labels[i+1], labels[i] 

    ax.legend(handles, labels, bbox_to_anchor=(1.01,0.5), loc='center left', borderaxespad=0, fontsize=15)
    
    # plot formatting
    if df_bounds is not None:
        xmax = max(abs(df_bounds['CarryOffLine']))
    else:
        xmax = max(abs(df['CarryOffLine']))
    ax.set_xlim(-xmax - 5, xmax + 5)
    ax.set_xlabel('Carry Offline (yds)', fontsize = 15, fontweight ='bold')
    
    plt.yticks(np.arange(round(min(df['CarryDistance']), -1), round(max(df['CarryDistance']), -1) + 20, 10))
    ax.set_ylabel('Carry Distance (yds)', fontsize = 15, fontweight ='bold')

    if incl_mean:
        plt.figtext(0.4, 0.001, '+ indicates mean', ha='center', fontsize = 13)

    plt.axvline(x=0, linestyle='--', color='grey')

    ax.tick_params(axis='both', which='major', labelsize=13)
    ax.tick_params(axis='both', which='minor', labelsize=13)

    if title is not None:
        ax.set_title(title, fontsize=17, fontweight ='bold')

    if pga:
        x = np.arange(-200, 200, 1)
        y1 = (8.2305070 * x) + 65.18387938
        y2 = (-8.2305070 * x) + 65.18387938

        ax.plot(x, y1, '-', color='green')
        ax.plot(x, y2, '-', color='green')
        ax.fill_between(x, y1, y2, color='black', alpha=0.15)

        ax.set_ylim(min(df['CarryDistance']) - 10, max(df['CarryDistance']) + 10) 

    # return plot
    return fig, ax


def scatter_trend(df, xcol, ycol, size=(7,5), title=None):

    fig, ax = plt.subplots(figsize=size)

    # plot points and add legend
    sns.scatterplot(data=df, x=xcol, y=ycol, hue='Club', s=75)
    plt.legend(bbox_to_anchor=(1.02, .5), loc='center left', borderaxespad=0, fontsize=13)

    ax.set_xlabel(xcol.replace('\n',' '), fontsize = 15, fontweight ='bold')
    ax.set_ylabel(ycol.replace('\n',' '), fontsize = 15, fontweight ='bold')

    ax.tick_params(axis='both', which='major', labelsize=13)
    ax.tick_params(axis='both', which='minor', labelsize=13)

    if title is not None:
        ax.set_title(title, fontsize=17, fontweight ='bold')

    return fig, ax


def barchart_bend(df, xcol, ycol, loft=True, size=(7,5), title=None):

    fig, ax = plt.subplots(figsize=size)

    if loft: 
        custom_palette = {}
        for club in df['Club'].unique():
            off = df[df['Club'] == club]['Bend\nLoft'].iloc[0]
            if (off == 'WEAKEN') or (off == 'STRENGTHEN'):
                custom_palette[club] = '#bcbd22'
            else:
                custom_palette[club] = '#1f77b4'

        # plot points and add legend
        sns.barplot(data=df, x=ycol, y=xcol, palette=custom_palette)

        ax.set_xlabel(ycol.replace('\n',' '), fontsize = 15, fontweight ='bold')
        ax.set_ylabel('Diff from Actual\nShort                         Long', fontsize = 15, fontweight ='bold')

        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.tick_params(axis='both', which='minor', labelsize=13)

        ymax = max(abs(df[xcol]))
        ax.set_ylim(-ymax - 1, ymax + 1)
        
        plt.xticks(rotation=45)
        
        plt.axhline(y=0, linestyle='--', color='grey')

        if title is not None:
            ax.set_title(title, fontsize=20, fontweight ='bold')

        for index, row in df.iterrows():
            if row['Diff from\nActual'] >= 5:
                ax.text(index/2, row['Diff from\nActual'], round(row['Diff from\nActual'], 1),
                        color='black', ha='center', fontsize = 13)
            elif row['Diff from\nActual'] <= -5:
                ax.text(index/2, row['Diff from\nActual'] - 1, round(row['Diff from\nActual'], 1),
                        color='black', ha='center', fontsize = 13)

    else: 
        custom_palette = {}
        for club in df['Club'].unique():
            off = df[df['Club'] == club]['Bend\nLie'].iloc[0]
            if (off == 'MOVE UPRIGHT') or (off == 'MOVE FLAT'):
                custom_palette[club] = '#bcbd22'
            else:
                custom_palette[club] = '#1f77b4'

        # plot points and add legend
        sns.barplot(data=df, x=xcol, y=ycol, palette=custom_palette)

        ax.set_xlabel(xcol.replace('\n',' '), fontsize = 15, fontweight ='bold')
        ax.set_ylabel(ycol.replace('\n',' '), fontsize = 15, fontweight ='bold')

        ax.tick_params(axis='both', which='major', labelsize=13)
        ax.tick_params(axis='both', which='minor', labelsize=13)

        xmax = max(abs(df[xcol]))
        ax.set_xlim(-xmax - 1, xmax + 1)

        plt.axvline(x=0, linestyle='--', color='grey')

        if title is not None:
            ax.set_title(title, fontsize=17, fontweight ='bold')

        for index, row in df.iterrows():
            if row['Avg\nOffline'] >= 5:
                ax.text(row['Avg\nOffline'] + 0.5, index/2, round(row['Avg\nOffline'], 1),
                        color='black', ha='center', fontsize = 13)
            elif row['Avg\nOffline'] <= -5:
                ax.text(row['Avg\nOffline'] - 0.5, index/2, round(row['Avg\nOffline'], 1),
                        color='black', ha='center', fontsize = 13)
            
    return fig, ax


def barchart_trend(df, metric, size=(7,5), title=None, buffer=0, sigfig=1):

    fig, ax = plt.subplots(figsize=size)

    df[metric] = df[metric].round(sigfig)

    # plot points and add legend
    sns.barplot(data=df, x='Club', y=metric, color='#1f77b4')

    ax.set_xlabel('Club', fontsize = 17, fontweight ='bold')
    ax.set_ylabel(metric.replace('\n',' '), fontsize = 15, fontweight ='bold')

    ax.tick_params(axis='both', which='major', labelsize=13)
    ax.tick_params(axis='both', which='minor', labelsize=13)

    ymax = max(abs(df[metric]))

    if min(df[metric]) > 0:
        ax.set_ylim(0, ymax + buffer)
    else:
        ax.set_ylim(-ymax - buffer, ymax + buffer)
        plt.axhline(y=0, linestyle='--', color='grey')

    plt.xticks(rotation=45)    

    if title is not None:
        ax.set_title(title, fontsize=17, fontweight ='bold')

    ax.bar_label(ax.containers[0], fontsize=15)
       
    return fig, ax


def barchart_grouped(df, metric, hue, size=(7,5), title=None, buffer=0, sigfig=1):

    fig, ax = plt.subplots(figsize=size)

    df[metric] = df[metric].round(sigfig)

    # plot points and add legend
    sns.barplot(data=df, x='Club', y=metric, hue=hue)

    ax.set_xlabel('Club', fontsize = 15, fontweight ='bold')
    ax.set_ylabel(metric.replace('\n',' '), fontsize = 15, fontweight ='bold')

    ax.tick_params(axis='both', which='major', labelsize=13)
    ax.tick_params(axis='both', which='minor', labelsize=13)

    ymax = max(abs(df[metric]))

    if min(df[metric]) > 0:
        ax.set_ylim(0, ymax + buffer)
    else:
        ax.set_ylim(-ymax - buffer, ymax + buffer)
        plt.axhline(y=0, linestyle='--', color='grey')

    plt.xticks(rotation=45)    

    if title is not None:
        ax.set_title(title, fontsize=17, fontweight ='bold')

    legend = ax.legend(fontsize=13)

    for index, row in df.iterrows():
        if row['variable'] == 'Avg':
            diff = row['Carry Distance'] - df[(df['Club'] == row['Club']) & (df['variable'] == 'PGA Avg')]['Carry Distance']
            ax.text( index, row['Carry Distance'] + 10, round(diff.iloc[0], 1),
                    color='black', ha='center', fontsize = 13)

    # ax.bar_label(ax.containers[0], fontsize=15)
       
    return fig, ax

def comp_hist(df, club, metric, avg, conversion, size=(7,5), xlabel=None, title=None, sigfig=1, color='#1f77b4'):

    df_plot = df.copy()

    fig, ax = plt.subplots(figsize=size)

    df_plot[metric] = df_plot[metric].round(sigfig) / conversion
    df_plot = df_plot[df_plot['var1'] == club]

    # plot points and add legend
    sns.histplot(data=df_plot, x=metric, color=color)

    ax.set_xlabel(xlabel, fontsize = 17, fontweight ='bold')
    ax.set_ylabel('Count', fontsize = 17, fontweight ='bold')

    ax.tick_params(axis='both', which='major', labelsize=15)
    ax.tick_params(axis='both', which='minor', labelsize=15)

    max_count = ax.get_ylim()[1]

    if title is not None:
        ax.set_title(title, fontsize=20, fontweight ='bold')

    plt.axvline(avg, color='orange')

    perc = round(stats.percentileofscore(df_plot[metric], avg), 1)
    print(perc)
    print(stats.percentileofscore(df_plot[metric], avg))
    if sigfig == 1:
        plt.text(x = avg,
                 y = max_count, 
                 s = '{:.1f}'.format(avg) + '\n' + str(perc) + 'th %ile',
                 fontsize=15,
                 weight='bold',
                 verticalalignment='top')
    elif sigfig == 0:
        plt.text(x = avg,
                 y = max_count, 
                 s = '{:.0f}'.format(avg) + '\n' + str(perc) + 'th %ile',
                 fontsize=15,
                 weight='bold',
                 verticalalignment='top')
    else:
        plt.text(x = avg,
                 y = max_count, 
                 s = avg,
                 fontsize=15,
                 weight='bold')
       
    return fig, ax
