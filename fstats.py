""" sports-metrics // fstats """
# Created 10-12-2016
# Last updated 15-12-2016

import pandas as pd

filepaths = {   'EPL 16/17': 'http://www.football-data.co.uk/mmz4281/1617/E0.csv',
                'EPL 15/16': 'http://www.football-data.co.uk/mmz4281/1516/E0.csv',
                'EPL 14/15': 'http://www.football-data.co.uk/mmz4281/1415/E0.csv',
                'EPL 13/14': 'http://www.football-data.co.uk/mmz4281/1314/E0.csv',
                'EPL 12/13': 'http://www.football-data.co.uk/mmz4281/1213/E0.csv',
                'EPL 11/12': 'http://www.football-data.co.uk/mmz4281/1112/E0.csv',
                'EPL 10/11': 'http://www.football-data.co.uk/mmz4281/1011/E0.csv',
                'EPL 09/10': 'http://www.football-data.co.uk/mmz4281/0910/E0.csv',
                'EPL 08/09': 'http://www.football-data.co.uk/mmz4281/0809/E0.csv',
                'EPL 07/08': 'http://www.football-data.co.uk/mmz4281/0708/E0.csv',
                'EPL 06/07': 'http://www.football-data.co.uk/mmz4281/0607/E0.csv',
                'EPL 05/06': 'http://www.football-data.co.uk/mmz4281/0506/E0.csv',
            }
date_parser_ = lambda date_str: pd.datetools.to_datetime(date_str, errors='coerce', dayfirst=True)

def data_(build=False):
    if build:
        Observations = pd.DataFrame()
        Responses = pd.Series()
        Dates = pd.Series()
        # Iterate through each .csv of a season and build observations and outcomes, then stick these together to form a big dataset
        for key, url in filepaths.items():
            raw_data = pd.read_csv(url, parse_dates=['Date'],
                                   date_parser=date_parser_)
            obs, resp, dates = _season(raw_data, season_str=key) # Get observations and responses
            Observations = Observations.append(obs)
            Responses = Responses.append(resp)
            Dates = Dates.append(dates)
        # Export data as .csv
        Observations.to_csv('./data/EPL_observations.csv')
        Responses.to_csv('./data/EPL_responses.csv')
        Dates.to_csv('./data/EPL_dates.csv')
    Observations = pd.read_csv('./data/EPL_observations.csv', index_col=0)
    Responses = pd.read_csv('./data/EPL_responses.csv', index_col=0, header=None, squeeze=True)
    Dates = pd.read_csv('./data/EPL_dates.csv', index_col=0, squeeze=True, header=None)
    # Format responses DataFrame
    Responses.name = 'outcome'
    Dates.name = 'date'
    return Observations, Responses, Dates

def _season(data, season_str):
    data.dropna(axis=0, inplace=True) # EPL 14/15 pulls in a NaN row
    fixtures = []
    season_data = pd.DataFrame()
    for fixture_index in data.index: # Go through each fixture
        home_str = data.loc[fixture_index,'HomeTeam']
        away_str = data.loc[fixture_index, 'AwayTeam']
        season_data = season_data.append(_match(data, fixture_index,
                                                home_str, away_str, season_str))
    observations = season_data.drop(['outcome','date'], axis=1)
    responses = season_data.loc[:, 'outcome']
    dates = season_data.loc[:, 'date']
    return observations, responses, dates


def _match(data, fixture_index, home_str, away_str, season_str=None):
    date = data.Date[(data.HomeTeam == home_str) & (data.AwayTeam == away_str)].values[0]
    recent_form = _recent_form(data, fixture_index, home_str, away_str, period=6)
    le = {'H':1, 'D':0, 'A':-1}
    outcome = le[data.FTR[(data.HomeTeam == home_str) & (data.AwayTeam == away_str)].values[0]]
    match = pd.Series([date, recent_form, outcome],['date','recent_form', 'outcome'],
                       name=season_str+'_'+home_str+'_vs_'+away_str)
    return match.transpose()

def _recent_form(data, fixture_index, home_str, away_str, period=6):
    # returns recent form score for a match (difference between team's previous matches goals scored)
    previous_matches = data.ix[:fixture_index, :].sort_values(by='Date', ascending=False) # Gets matches ordered with most recent first
    home_team_matches = previous_matches.ix[(previous_matches.HomeTeam==home_str) | (previous_matches.AwayTeam==home_str)]
    away_team_matches = previous_matches.ix[(previous_matches.HomeTeam==away_str) | (previous_matches.AwayTeam==away_str)]
    home_team_matches.reset_index(inplace=True)
    away_team_matches.reset_index(inplace=True)
    home_goals = 0
    away_goals = 0
    if (home_team_matches.shape[0] > period+1) & (away_team_matches.shape[0] > period+1):
        for i in range(period, 0, -1):
            home_status = int(home_team_matches.loc[i, 'HomeTeam']==home_str)
            away_status = int(away_team_matches.loc[i, 'HomeTeam']==away_str)
            home_goals = home_goals + home_team_matches.loc[i, 'FTHG']*home_status + home_team_matches.loc[i, 'FTAG']*(1-home_status)
            away_goals = away_goals + away_team_matches.loc[i, 'FTHG']*away_status + away_team_matches.loc[period, 'FTAG']*(1-away_status)
            recent_form_score = home_goals - away_goals
    else:
        recent_form_score = 'NaN'
    return recent_form_score

def odds_():
    # Parse home odds, away odds from raw data
    # Extract best odds (i.e. largest) from this set
    # Return a dataframe of best odds
    bookmakers = ['B365', 'BS', 'BW', 'GB', 'IW', 'LB', 'PS', 'SO', 'SB', 'SJ', 'SY', 'VC', 'WH']
    home_labels = [i+'H' for i in bookmakers]
    away_labels = [i+'A' for i in bookmakers]
    Odds = pd.DataFrame(columns=['Home', 'Away'])
    for key, url in filepaths.items():
        # Get all odds
        season = pd.read_csv(url, parse_dates=['Date'], date_parser=date_parser_)
        season.dropna(inplace=True)
        season_odds = season.loc[:, home_labels+away_labels]
        # Get indices
        fixture_index = [key+'_'+season.ix[i, 'HomeTeam']+'_vs_'+season.ix[i, 'AwayTeam'] for i in season.index]
        # Get best odds
        bo = pd.DataFrame({'Home': [max(odds) for _, odds in season_odds[home_labels].iterrows()],
                           'Away': [max(odds) for _, odds in season_odds[away_labels].iterrows()]},
                           index = fixture_index)
        # Append to big dataset
        Odds = Odds.append(bo)
    # Export data as .csv
    #Odds.to_csv('./data/EPL_odds.csv')
    return Odds
