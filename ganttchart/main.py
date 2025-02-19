#%%
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.patches import Patch

show_progress = True

c_dict = {
    'review':'#E64646', 
    'data collection':'#F9E2AF', 
    'data cleaning':'#A4BC92', 
    'data analysis':'#B3C99C', 
    'research design':'#3475D0',
    'preparation':'#F5F3C1',
    'model building':'#1A5F7A',
    'model test':'#002B5B',
    'result analysis':'#C7E9B0',
    'visualisation':'#009FBD',
    'writing':'#FF6000',
    'presentation':'#FFA559',
    'publication':'#7FAE42'
        }

data_path = 'metadata.csv'

#%%
df = pd.read_csv(data_path, index_col=0)

# convert start and end dates to datetime
df['start'] = pd.to_datetime(df['start'], format='%d/%m/%Y')
df['end'] = pd.to_datetime(df['end'], format='%d/%m/%Y')

# sort by start date; if start date is the same, sort by end date (descending)
df = df.sort_values(by=['start', 'end'], ascending=[True, True])
df.reset_index(drop=False, inplace=True)
#%%
# project start date
proj_start = df.start.min()

# number of days from project start to task start
df['start_num'] = (df.start-proj_start).dt.days
# number of days from project start to end of tasks
df['end_num'] = (df.end-proj_start).dt.days
# days between start and end of each task
df['days_start_to_end'] = df.end_num - df.start_num

# days between start and current progression of each task
df['current_num'] = (df.days_start_to_end * df.completion)

# get the unique value of df.category.unique()
categories = df.category.unique()

# randomly replace the key from c_dict with the value from categories
c_dict = {k: c_dict.popitem()[1] for k in categories}

# create a column with the color for each department
def color(row, c_dict=c_dict):
    return c_dict[row['category']]
df['color'] = df.apply(color, axis=1)

fig, ax = plt.subplots(1, figsize=(16,6))
ax.barh(df.task, df.current_num, left=df.start_num, color=df.color)

ax.barh(df.task, df.days_start_to_end, left=df.start_num, color=df.color, alpha=0.5)

# texts
for idx, row in df.iterrows():
    if show_progress:
        ax.text(row.end_num+0.2, idx, f"{int(row.completion*100)}%", va='center', ha='left')
    ax.text(row.start_num-0.2, idx, row.task, va='center', ha='right')

# grid lines
ax.set_axisbelow(True)
ax.xaxis.grid(color='gray', linestyle='dashed', alpha=0.2, which='both')

# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)

##### LEGENDS #####

legend_elements = [Patch(facecolor=c_dict[i], label=i)  for i in c_dict]

# move legend to the bottom middle
plt.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=5)
##### TICKS #####
xticks = np.arange(0, df.end_num.max()+1, 30)
xticks_labels = pd.date_range(proj_start, end=df.end.max()).strftime("%m/%d/%y")
#xticks_minor = np.arange(0, df.end_num.max()+1, 15)
ax.set_xticks(xticks)
#ax.set_xticks(xticks_minor, minor=True)
ax.set_xticklabels(xticks_labels[::30])
ax.set_yticks([])

# save figure as svg
plt.savefig('gantt_chart.svg', bbox_inches='tight')

# save figure as png
plt.savefig('gantt_chart.png', bbox_inches='tight')
# %%
