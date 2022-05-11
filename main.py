import sys
import pandas as pd
import time
from calendar import timegm

def parse_str(x):
    """
    Strip the two extreme characters in a piece of string.

    Example:
        `>>> parse_str('[my string]')`
        `'my string'`
    """
    return x[1:-1]

def parse_time(x):
    '''
    Parses time in this format:
        `[day/month/year:hour:minute:second zone]`
    and converts it to epoch time.

    Example:
        `>>> parse_time('31/Dec/2018:23:55:00 +0800')`
        `> 1546300500`
    '''
    dt = time.strptime(x[1:-7], '%d/%b/%Y:%H:%M:%S')
    return timegm(dt)

log_file = sys.argv[1]

data = pd.read_csv(
    log_file,
    sep=r'\s(?=(?:[^"]*"[^"]*")*[^"]*$)(?![^\[]*\])',
    engine='python',
    na_values='-',
    header=None,
    usecols=[0, 3, 4],
    names=['client', 'time', 'request'],
    converters={'time': parse_time,
                'request': parse_str})

endpoint = data.pop('request').str.split()
data['path'] = endpoint.str[1]

data = data.sort_values('time', ascending=True)
data_groups = data.groupby('client')#.count()#['time'].max()
groups = [g[1] for g in list(data_groups)[:2]]

# final data structure
output_data = []

for name, group in data_groups:
    group.reset_index(inplace=True)
    login_df = group[group['path'] == '/login']
    login_df.reset_index(inplace=True)
    
    # Initialize the values
    o = len(group)
    p = len(login_df)
    j = 40 # index of 40th request
    k = 100 # index of 100th request
    l = 20 # number of /login requests
    ban_20 = 0
    ban_40 = 0 # time to ban for 40 requests
    ban_100 = 0 # time to ban for 100 requests
    
    # Deal with calls to /login route
    for i, r in login_df.iterrows():
        if l == p:
            break
        
        time_for_20 = login_df.iloc[l]['time'] - login_df.iloc[i]['time']
        
        if time_for_20 < 600 and r['time'] >= ban_20: # ten minutes
            output_data.append({'time': login_df.iloc[l]['time'], 'action': 'BAN', 'client': name})
            output_data.append({'time': login_df.iloc[l]['time'] + 7200, 'action': 'UNBAN', 'client': name})
            ban_20 = r['time'] + 7200
    
    # Deal with number of generic requests    
    for i, r in group.iterrows():
        if j == o or k == o:
            break
        
        time_for_40 = group.iloc[j]['time'] - group.iloc[i]['time']
        time_for_100 = group.iloc[k]['time'] - group.iloc[i]['time']
        
        if time_for_40 < 60 and r['time'] >= ban_40: # one minute
            output_data.append({'time': group.iloc[j]['time'], 'action': 'BAN', 'client': name})
            output_data.append({'time': group.iloc[j]['time'] + 600, 'action': 'UNBAN', 'client': name})
            ban_40 = r['time'] + 600
        
        if time_for_100 < 600 and r['time'] >= ban_100: # ten minutes
            output_data.append({'time': group.iloc[j]['time'], 'action': 'BAN', 'client': name})
            output_data.append({'time': group.iloc[j]['time'] + 3600, 'action': 'UNBAN', 'client': name})
            ban_100 = r['time'] + 3600
        
        j += 1
        k += 1

output_df = pd.DataFrame(output_data)
output_df = output_df.sort_values('time', ascending=True).drop_duplicates()
output_df.reset_index(inplace=True)
output_df.drop('index', axis=1, inplace=True)
print(len(output_df))
output_df.to_csv('./firewall_rules.csv', header=False, index=False, encoding='utf-8')