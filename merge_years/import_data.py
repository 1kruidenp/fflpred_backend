import pandas as pd
import numpy as np
import time


def get_full_data(raw_data_path, return_missing_column_list=False):
    """
    Receives the path of the raw-data folder (ending in /raw_data) and returns the dataset of all years combined.
    If return_missing_column_list is True, returns a  dictionary of missing columns of format:
    Key = missing column name, Value = year(s) in which it existed
    """

    # Read raw_data into individual dataframes
    df21 = pd.read_csv(raw_data_path + '/2020-21/gws/merged_gw.csv',
                       encoding='utf_8')
    df20 = pd.read_csv(raw_data_path + '/2019-20/gws/merged_gw.csv',
                       encoding='utf_8')
    df19 = pd.read_csv(raw_data_path + '/2018-19/gws/merged_gw.csv',
                       encoding='ISO-8859-1')
    df18 = pd.read_csv(raw_data_path + '/2017-18/gws/merged_gw.csv',
                       encoding='ISO-8859-1')
    df17 = pd.read_csv(raw_data_path + '/2016-17/gws/merged_gw.csv',
                       encoding='ISO-8859-1')

    # Add a column identifying the season to each dataframe
    df21['season'] = 21
    df20['season'] = 20
    df19['season'] = 19
    df18['season'] = 18
    df17['season'] = 17

    # Create a list of all dataframes
    dflist = [df17, df18, df19, df20, df21]

    # Create a list of all columns existing in each season
    consistent_columns = []
    for column in list(df21.columns):
        if  column in list(df20.columns) and \
            column in list(df19.columns) and \
            column in list(df18.columns) and \
            column in list(df17.columns):
            consistent_columns.append(column)

    # Create a dictionary with columns that are only in some years.
    # Key = column name, value = years for which the column exists.
    missing_columns = {}
    for df in dflist:
        for column in list(df.columns):
            if not column in consistent_columns:
                if column in missing_columns.keys():
                    missing_columns[column].append(df.loc[0, ['season']][0])
                else:
                    missing_columns[column] = [df.loc[0, ['season']][0]]

    # Concatenate seasons based on consistent columns
    frames_to_concat = [
        df21[consistent_columns], df20[consistent_columns],
        df19[consistent_columns], df18[consistent_columns],
        df17[consistent_columns]
    ]
    complete_data = pd.concat(frames_to_concat)

    # Remove trailing underscores and numbers from names
    complete_data.name = complete_data.name.str.rstrip('_1234567890')

    # Swap out underscores for spaces within names
    complete_data.name = complete_data.name.str.replace('_', ' ')

    # Drop column 'round' as it is the same as 'GW'
    complete_data.drop(columns=['round'], inplace=True)

    # Set names to lowercase
    complete_data.name = complete_data.name.apply(lambda n: n.lower())

    # Correct game weeks for 2020
    complete_data['GW'] = complete_data['GW'].apply(correct_2020)

    # Match player position
    complete_data, players_raw_seasons = match_position(complete_data, raw_data_path)

    # Add dreamteam count for each player for the last season
    complete_data = add_dreamteam_count(complete_data, players_raw_seasons)

    # Add team name for last two years to dataframe
    complete_data = add_team(complete_data, players_raw_seasons, raw_data_path)

    # Add opponent strength
    complete_data = add_opponent_strength(complete_data)

    # Add own team strength
    complete_data = add_team_strength(complete_data)

    # Sort ascending by player name and kickoff-date and separate kickoff-date and -time
    complete_data = sort_kickoff(complete_data)

    if return_missing_column_list:
        return complete_data, missing_columns
    return complete_data


# Function to correct gameweeks for 2020
def correct_2020(gw):
    if gw > 38:
        return gw - 9
    return gw


def match_position(df, raw_data_path):
    """ Function to match player positions to the full dataframe """

    # Import data about player positions
    players_raw21 = pd.read_csv(raw_data_path + '/2020-21/players_raw.csv',
                        encoding='utf_8')
    players_raw20 = pd.read_csv(raw_data_path + '/2019-20/players_raw.csv',
                        encoding='utf_8')
    players_raw19 = pd.read_csv(raw_data_path + '/2018-19/players_raw.csv',
                        encoding='utf-8')
    players_raw18 = pd.read_csv(raw_data_path + '/2017-18/players_raw.csv',
                        encoding='utf-8')
    players_raw17 = pd.read_csv(raw_data_path + '/2016-17/players_raw.csv',
                        encoding='utf-8')

    players_raw_seasons = [players_raw17, players_raw18, players_raw19, players_raw20, players_raw21]

    position_by_name = {  #Dictionary to map element_type to position
        1: 'GK',
        2: 'DEF',
        3: 'MID',
        4: 'FWD'
    }

    for season in players_raw_seasons:  #Iterate through the different raw files

        positions = map(lambda num: position_by_name[num],
                        season['element_type'])  #Map the positions
        season['position'] = list(positions)  #Assign the map to new columns
        season['name'] = season['first_name'] + ' '\
                            + season['second_name']  #Merge the first and second names of the raw players
        season['name'] = season['name'].str.lower()  #Set these names to lower
        for i, row in season.iterrows():  #Change caglar to çaglar
            if row['name'] == 'caglar söyüncü':
                season['name'].at[i] = 'çaglar söyüncü'


    #Change the position of the GK Danny Ward to MID so that we have duplicates that we can drop
    #We will change the position after dropping,
    #IMPORTANT DO NOT REMOVE THIS STEP WITHOUT REMOVING THE STEP OF CHANGING THE POSITION BACK AND VICE VERSA
    for i, row in players_raw19.iterrows():
        if row['name'] == 'Danny Ward' and row['position'] == 'GK':
            players_raw19['position'].at[i] = 'MID'

    #Here we split the data frame into the seasons and join the raw positions on the name
    df17 = df.loc[df['season'] == 17].copy()
    playerpositions = players_raw17[['name', 'position']]
    playerpositions.set_index('name', drop=True, inplace=True)
    df17 = df17.join(playerpositions, on=['name'])

    df18 = df.loc[df['season'] == 18].copy()
    playerpositions = players_raw18[['name', 'position']]
    playerpositions.set_index('name', drop=True, inplace=True)
    df18 = df18.join(playerpositions, on=['name'])

    df19 = df.loc[df['season'] == 19].copy()
    playerpositions = players_raw19[['name', 'position']]
    playerpositions.set_index('name', drop=True, inplace=True)
    df19 = df19.join(playerpositions, on=['name'])

    df20 = df.loc[df['season'] == 20].copy()
    playerpositions = players_raw20[['name', 'position']]
    playerpositions.set_index('name', drop=True, inplace=True)
    df20 = df20.join(playerpositions, on=['name'])

    df21 = df.loc[df['season'] == 21].copy()
    playerpositions = players_raw21[['name', 'position']]
    playerpositions.set_index('name', drop=True, inplace=True)
    df21 = df21.join(playerpositions, on=['name'])

    #Reconcatenate the data into a complete dataset
    complete_data = pd.concat([df17, df18, df19, df20, df21])

    complete_data.drop_duplicates(
        inplace=True)  #Drop the duplicates (Danny Ward and Ben Davies)

    for i, row in complete_data.iterrows(
    ):  #Change the goalkeeper Danny Ward to the correct position.
        if row['name'] == 'danny ward' and row['element'] == 105:
            complete_data['position'].at[i] = 'GK'

    return complete_data, players_raw_seasons


def sort_kickoff(df):
    """Turn kickoff date into datetime, sort dataframe by name and kickoff date"""
    df.kickoff_time = pd.to_datetime(df.kickoff_time)
    df = df.sort_values(by=['name', 'kickoff_time'],
                                              ascending=True)
    df.reset_index(drop=True, inplace=True)
    df['kickoff_date'] = df['kickoff_time']\
                                .apply(lambda d: d.date())
    df['kickoff_time'] = df['kickoff_time']\
                                .apply(lambda d: d.time())

    df.reset_index(drop=True)

    return df


def create_dreamteam_count_yearly(player, raw_list):
    """Create the average dreamteam count for an individual player"""
    num_seasons = 0
    yearly_dreamteam_count = 0
    for i, raw in enumerate(raw_list):
        if i == len(raw_list) - 1:
            break
        if player in raw['name'].values:
            num_seasons += 1
            yearly_dreamteam_count += raw[['dreamteam_count']][raw.name == player].values[0][0]
    if num_seasons == 0:
        return np.nan
    return yearly_dreamteam_count / num_seasons

def add_dreamteam_count(df, raw_seasons):
    """Add the average number of appearances in the dream team prior to the current season as feature in season 2021"""
    df17 = df.loc[df['season'] == 17].copy()
    df18 = df.loc[df['season'] == 18].copy()
    df19 = df.loc[df['season'] == 19].copy()
    df20 = df.loc[df['season'] == 20].copy()
    df21 = df.loc[df['season'] == 21].copy()

    dreamteam_count_yearly_average = []

    for _, row in df21.iterrows():
        dreamteam_count_yearly_average.append(create_dreamteam_count_yearly(row['name'], raw_seasons))
    df21['dreamteam_yearly_average'] = dreamteam_count_yearly_average

    complete_data = pd.concat([df17, df18, df19, df20, df21])

    return complete_data

def add_team(df, players_raw_seasons, raw_data_path):
    teams_raw_20 = pd.read_csv(raw_data_path + '/2019-20/teams.csv')
    teams_raw_21 = pd.read_csv(raw_data_path + '/2020-21/teams.csv')

    [players_raw17, players_raw18, players_raw19, players_raw20, players_raw21] = players_raw_seasons

    df17 = df.loc[df['season'] == 17].copy()

    df18 = df.loc[df['season'] == 18].copy()

    df19 = df.loc[df['season'] == 19].copy()

    df20 = df.loc[df['season'] == 20].copy()
    abc = players_raw20[['name', 'team']]
    abc.set_index('name', drop=True, inplace=True)
    df20 = df20.join(abc, on=['name'])
    df20.rename(columns={'team': 'team_id'}, inplace=True)

    xyz = teams_raw_20[['id', 'name']].copy()
    xyz.rename(columns={'name': 'team_name', 'id': 'team_id'}, inplace=True)
    xyz.set_index('team_id', drop=True, inplace=True)
    df20 = df20.join(xyz, on=['team_id'])

    df21 = df.loc[df['season'] == 21].copy()
    abc = players_raw21[['name', 'team']]
    abc.set_index('name', drop=True, inplace=True)
    df21 = df21.join(abc, on=['name'])
    df21.rename(columns={'team': 'team_id'}, inplace=True)

    xyz_2 = teams_raw_21[['id', 'name']].copy()
    xyz_2.rename(columns={'name': 'team_name', 'id': 'team_id'}, inplace=True)
    xyz_2.set_index('team_id', drop=True, inplace=True)
    df21 = df21.join(xyz_2, on=['team_id'])

    complete_data = pd.concat([df17, df18, df19, df20, df21])

    return complete_data

def add_opponent_strength(df):
    team_playing_home_20 = {
        1: 1180,
        2: 1020,
        3: 1020,
        4: 1050,
        5: 1110,
        6: 1220,
        7: 1130,
        8: 1100,
        9: 1210,
        10: 1340,
        11: 1330,
        12: 1220,
        13: 1090,
        14: 980,
        15: 1180,
        16: 1150,
        17: 1180,
        18: 1030,
        19: 1040,
        20: 1230
    }

    team_playing_away_20 = {
        1: 1240,
        2: 1050,
        3: 1020,
        4: 1010,
        5: 1180,
        6: 1230,
        7: 1120,
        8: 1240,
        9: 1160,
        10: 1350,
        11: 1340,
        12: 1300,
        13: 1100,
        14: 1020,
        15: 1200,
        16: 1040,
        17: 1240,
        18: 1140,
        19: 1030,
        20: 1190
    }

    team_playing_home_21 = {
        1: 1200,
        2: 1100,
        3: 1130,
        4: 1060,
        5: 1250,
        6: 1090,
        7: 1250,
        8: 1090,
        9: 1240,
        10: 1160,
        11: 1250,
        12: 1340,
        13: 1250,
        14: 1050,
        15: 1000,
        16: 1060,
        17: 1190,
        18: 1050,
        19: 1230,
        20: 1080
    }

    team_playing_away_21 = {
        1: 1250,
        2: 1160,
        3: 1130,
        4: 1070,
        5: 1280,
        6: 1110,
        7: 1130,
        8: 1100,
        9: 1260,
        10: 1170,
        11: 1210,
        12: 1360,
        13: 1320,
        14: 1070,
        15: 1040,
        16: 1100,
        17: 1250,
        18: 1040,
        19: 1260,
        20: 1110
    }

    df17 = df.loc[df['season'] == 17].copy()

    df18 = df.loc[df['season'] == 18].copy()

    df19 = df.loc[df['season'] == 19].copy()

    df20 = df.loc[df['season'] == 20].copy()
    level = []
    for _, row in df20.iterrows():
        if row.was_home == True:
            level.append(team_playing_away_20[row['opponent_team']])
        else:
            level.append(team_playing_home_20[row['opponent_team']])
    df20['opponent_level'] = level

    df21 = df.loc[df['season'] == 21].copy()
    level = []
    for _, row in df21.iterrows():
        if row.was_home == True:
            level.append(team_playing_away_21[row['opponent_team']])
        else:
            level.append(team_playing_home_21[row['opponent_team']])
    df21['opponent_level'] = level

    complete_data = pd.concat([df17, df18, df19, df20, df21])

    return complete_data

def add_team_strength(df):
    team_playing_home_20 = {
        1: 1180,
        2: 1020,
        3: 1020,
        4: 1050,
        5: 1110,
        6: 1220,
        7: 1130,
        8: 1100,
        9: 1210,
        10: 1340,
        11: 1330,
        12: 1220,
        13: 1090,
        14: 980,
        15: 1180,
        16: 1150,
        17: 1180,
        18: 1030,
        19: 1040,
        20: 1230
    }

    team_playing_away_20 = {
        1: 1240,
        2: 1050,
        3: 1020,
        4: 1010,
        5: 1180,
        6: 1230,
        7: 1120,
        8: 1240,
        9: 1160,
        10: 1350,
        11: 1340,
        12: 1300,
        13: 1100,
        14: 1020,
        15: 1200,
        16: 1040,
        17: 1240,
        18: 1140,
        19: 1030,
        20: 1190
    }

    team_playing_home_21 = {
        1: 1200,
        2: 1100,
        3: 1130,
        4: 1060,
        5: 1250,
        6: 1090,
        7: 1250,
        8: 1090,
        9: 1240,
        10: 1160,
        11: 1250,
        12: 1340,
        13: 1250,
        14: 1050,
        15: 1000,
        16: 1060,
        17: 1190,
        18: 1050,
        19: 1230,
        20: 1080
    }

    team_playing_away_21 = {
        1: 1250,
        2: 1160,
        3: 1130,
        4: 1070,
        5: 1280,
        6: 1110,
        7: 1130,
        8: 1100,
        9: 1260,
        10: 1170,
        11: 1210,
        12: 1360,
        13: 1320,
        14: 1070,
        15: 1040,
        16: 1100,
        17: 1250,
        18: 1040,
        19: 1260,
        20: 1110
    }

    df17 = df.loc[df['season'] == 17].copy()

    df18 = df.loc[df['season'] == 18].copy()

    df19 = df.loc[df['season'] == 19].copy()

    df20 = df.loc[df['season'] == 20].copy()
    level = []
    for _, row in df20.iterrows():
        if row.was_home == False:
            level.append(team_playing_away_20[row['team_id']])
        else:
            level.append(team_playing_home_20[row['team_id']])
    df20['team_level'] = level

    df21 = df.loc[df['season'] == 21].copy()
    level = []
    for _, row in df21.iterrows():
        if row.was_home == False:
            level.append(team_playing_away_21[row['team_id']])
        else:
            level.append(team_playing_home_21[row['team_id']])
    df21['team_level'] = level

    complete_data = pd.concat([df17, df18, df19, df20, df21])

    return complete_data


if __name__=="__main__":
    start = time.time()
    df, missing_columns = get_full_data('../raw_data', return_missing_column_list=True)
    print(df.head(5))
    print(missing_columns)
    end = time.time()
    print(end-start)
