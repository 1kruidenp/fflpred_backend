import pandas as pd
from sklearn.preprocessing import LabelEncoder


def split_positions(df):
    fwd_df = df[(df.position=='FWD')]
    mid_df = df[(df.position=='MID')]
    def_df = df[(df.position=='DEF')]
    gk_df = df[(df.position=='GK')]
    return fwd_df,mid_df,def_df,gk_df


fwd_features=['name', 'assists', 'bps', 'creativity', 'goals_scored', 
              'ict_index', 'influence','kickoff_time','minutes',
              'penalties_missed','red_cards','selected','threat','total_points','transfers_balance',
              'value','was_home','yellow_cards','GW','season','opponent_level','team_level']

mid_features=['name','assists','bps','clean_sheets','creativity','goals_conceded','goals_scored','ict_index',
              'influence','kickoff_time','minutes','penalties_missed','red_cards','selected',
              'threat','total_points','transfers_balance','value','was_home','yellow_cards','GW',
              'season','opponent_level','team_level']

def_features=['name','assists','bps','clean_sheets','creativity','goals_conceded','goals_scored',
              'ict_index','influence','kickoff_time','minutes','penalties_missed','red_cards',
              'selected','threat','total_points','transfers_balance','value','was_home',
              'yellow_cards','GW','season','opponent_level','team_level']

gk_features=['name','assists','bps','clean_sheets','creativity','goals_conceded','ict_index','influence',
             'kickoff_time','minutes','penalties_saved','red_cards','saves','selected','threat','total_points',
            'transfers_balance','value','was_home','yellow_cards','GW','season','opponent_level','team_level']
fwd_features=['name', 'assists', 'bps', 'creativity', 'goals_scored', 
              'ict_index', 'influence','kickoff_time','minutes',
              'penalties_missed','red_cards','selected','threat','total_points','transfers_balance',
              'value','was_home','yellow_cards','GW','season','opponent_level','team_level']


def preprocess_fwd(df,ra):
    df=df[fwd_features]
    
    df['cards'] = df['yellow_cards'] + df['red_cards']
    
    rolling_features=['name','assists','bps','goals_scored','ict_index',
                  'minutes','selected','total_points','transfers_balance','value','penalties_missed','cards']

    static_features=['kickoff_time','was_home','GW','season','opponent_level','team_level','value']

    total_points_df=df['total_points']
    
    rolling_df=df[rolling_features].groupby('name').rolling(ra,closed = 'left').mean()
    
    rolling_df.rename(columns={'total_points':'rolling_points'},inplace=True)
    rolling_df.rename(columns={'value':'rolling_value'})
    
    result = map(lambda position:position, total_points_df)
    rolling_df['total_points']=list(result)
    
    for i in static_features:
        result = map(lambda position:position, df[i])
        rolling_df[i]=list(result)
        
    rolling_df.dropna(inplace=True)
    
    time=[]
    for row in rolling_df['kickoff_time']:
        time.append(row.hour)
    rolling_df['time']=time

    rolling_df.drop(columns='kickoff_time',inplace=True)
    
    encoder = LabelEncoder()
    encoder.fit(rolling_df[['was_home']])
    rolling_df['was_home'] = encoder.transform(rolling_df[['was_home']])
    
    rolling_df=rolling_df.reset_index()
    
    hold=rolling_df[['name','GW','season','value']]
    
    X=rolling_df.drop(columns=['name','GW','season','level_1','total_points','goals_scored','value'])
    y=rolling_df['total_points']
    
    return X,y,hold
        
        
def preprocess_mid(df,ra):
    df=df[mid_features]
    
    df['cards'] = df['yellow_cards'] + df['red_cards']
    
    rolling_features=['name','assists','bps','clean_sheets','goals_conceded','goals_scored','ict_index',
                  'minutes','selected','total_points','transfers_balance','value','penalties_missed','cards']

    static_features=['kickoff_time','was_home','GW','season','opponent_level','team_level','value']

    total_points_df=df['total_points']
    
    rolling_df=df[rolling_features].groupby('name').rolling(ra,closed = 'left').mean()
    
    rolling_df.rename(columns={'total_points':'rolling_points'},inplace=True)
    rolling_df.rename(columns={'value':'rolling_value'})
    
    result = map(lambda position:position, total_points_df)
    rolling_df['total_points']=list(result)
    
    for i in static_features:
        result = map(lambda position:position, df[i])
        rolling_df[i]=list(result)
        
    rolling_df.dropna(inplace=True)
    
    time=[]
    for row in rolling_df['kickoff_time']:
        time.append(row.hour)
    rolling_df['time']=time

    rolling_df.drop(columns='kickoff_time',inplace=True)
    
    encoder = LabelEncoder()
    encoder.fit(rolling_df[['was_home']])
    rolling_df['was_home'] = encoder.transform(rolling_df[['was_home']])
    
    rolling_df=rolling_df.reset_index()
    
    hold=rolling_df[['name','GW','season','value']]
    
    X=rolling_df.drop(columns=['name','GW','season','level_1','total_points','value'])
    y=rolling_df['total_points']
    
    return X,y,hold

def preprocess_def(df,ra):
    df=df[def_features]
    
    df['cards'] = df['yellow_cards'] + df['red_cards']
    
    rolling_features=['name','assists','bps','clean_sheets','goals_conceded','goals_scored','ict_index',
                  'minutes','selected','total_points','transfers_balance','value','cards']

    static_features=['kickoff_time','was_home','GW','season','opponent_level','team_level','value']

    total_points_df=df['total_points']
    
    rolling_df=df[rolling_features].groupby('name').rolling(ra,closed = 'left').mean()
    
    rolling_df.rename(columns={'total_points':'rolling_points'},inplace=True)
    rolling_df.rename(columns={'value':'rolling_value'})
    
    result = map(lambda position:position, total_points_df)
    rolling_df['total_points']=list(result)
    
    for i in static_features:
        result = map(lambda position:position, df[i])
        rolling_df[i]=list(result)
        
    rolling_df.dropna(inplace=True)
    
    time=[]
    for row in rolling_df['kickoff_time']:
        time.append(row.hour)
    rolling_df['time']=time

    rolling_df.drop(columns='kickoff_time',inplace=True)
    
    encoder = LabelEncoder()
    encoder.fit(rolling_df[['was_home']])
    rolling_df['was_home'] = encoder.transform(rolling_df[['was_home']])
    
    rolling_df=rolling_df.reset_index()
    
    hold=rolling_df[['name','GW','season','value']]
    
    X=rolling_df.drop(columns=['name','GW','season','level_1','total_points','value'])
    y=rolling_df['total_points']
    
    return X,y,hold

def preprocess_gk(df,ra):
    df=df[gk_features]
    
    df['cards'] = df['yellow_cards'] + df['red_cards']
    
    rolling_features=['name','bps','clean_sheets','goals_conceded','ict_index',
                    'minutes','saves','selected','total_points','transfers_balance','value','cards']

    mean_features=['name','penalties_saved']
    
    static_features=['kickoff_time','was_home','GW','season','opponent_level','team_level','value']

    total_points_df=df['total_points']
    
    rolling_df=df[rolling_features].groupby('name').rolling(ra,closed = 'left').mean()
    
    rolling_df.rename(columns={'total_points':'rolling_points'},inplace=True)
    rolling_df.rename(columns={'value':'rolling_value'})
    
    mean_saves=df[mean_features].groupby('name').mean()
    
    rolling_df = rolling_df.reset_index()
    
    ls=[]
    for i,player in enumerate(rolling_df['name']):
        ls.append(mean_saves.loc[player][0])
        
    rolling_df['penalty_saves']=ls
    
    result = map(lambda position:position, total_points_df)
    rolling_df['total_points']=list(result)
    
    for i in static_features:
        result = map(lambda position:position, df[i])
        rolling_df[i]=list(result)
        
    rolling_df.dropna(inplace=True)
    
    time=[]
    for row in rolling_df['kickoff_time']:
        time.append(row.hour)
    rolling_df['time']=time

    rolling_df.drop(columns='kickoff_time',inplace=True)
    
    encoder = LabelEncoder()
    encoder.fit(rolling_df[['was_home']])
    rolling_df['was_home'] = encoder.transform(rolling_df[['was_home']])
    
    rolling_df=rolling_df.reset_index()
    
    hold=rolling_df[['name','GW','season','value']]
    
    X=rolling_df.drop(columns=['name','GW','season','level_1','total_points','value'])
    y=rolling_df['total_points']
    
    return X,y,hold
