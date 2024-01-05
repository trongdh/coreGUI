from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
df = pd.read_csv(r'kpi/output/HOST02_pmresult_1693700401_5.csv')
new_df = df[['Start_time','NE','ULR-SR (LUSR EPS)']].copy()
new_df['Start_time'] = pd.to_datetime(new_df['Start_time'],format="%Y%m%d%H%M")

fig, ax = plt.subplots()
for name, group in new_df.groupby('NE'):
    group.plot(x='Start_time', y='ULR-SR (LUSR EPS)', ax=ax, marker='o', label=name)
ax.set_xticks(new_df.Start_time)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d:%H-%M'))
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))
plt.show()
