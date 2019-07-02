import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np

import update_sqlite as us
import mal_scrapper as ms

#===============================================================================
# Preprocess

def database_to_dataframe(year, season):
    # Get the data
    conn, c = us.init_connection()
    anime_season = '%s_%s' %(year, season)
    df_global = pd.read_sql("SELECT * FROM '%s'" %(anime_season), conn)

    return df_global

def format_dataframe(df):
    df.replace(to_replace='N/A', value=np.nan, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df['anime_members'] = pd.to_numeric(df['anime_members'])
    df['anime_score'] = pd.to_numeric(df['anime_score'].str.replace(',', '.'))
    return df

def get_new_seasonal_animes_only(df, year, season):
    mal_data = ms.get_stats(year, season, 'TV')
    new_anime_names = [ x['anime_name'] for x in mal_data if x['anime_seasonal_type'] == 'New' ]
    df = df[ df['anime_name'].isin(new_anime_names) ]
    return df

def get_first_date_with_members(df):
    anime_groups = df.groupby(by='anime_name')
    # Create the dictionnary which will contains the first dates
    dict_first_dates_with_members = {'anime_name':[], 'first_date':[], 'anime_members':[]}
    for anime, group in anime_groups:
        members_dates = group[ group['anime_members'].notnull() ]['date']
        first_date_with_members = members_dates.min()
        members_at_first_date = group[ group['date']==members_dates.min() ]['anime_members'].item()
        # Add the data to the dictionnary
        dict_first_dates_with_members['anime_name'].append(anime)
        dict_first_dates_with_members['first_date'].append(first_date_with_members)
        dict_first_dates_with_members['anime_members'].append(members_at_first_date)

    df_first_dates_with_members = pd.DataFrame(dict_first_dates_with_members)

    return df_first_dates_with_members

def get_most_popular_animes_only(df, members_limit):
    # Get the first date when each anime had members in the season
    df_first_dates_with_members = get_first_date_with_members(df)

    # Limit of members needed to be taken in the future statistic calculations
    # members_limit = df_first_dates_with_members['anime_members'].quantile(0.7)

    # List of anime names to keep
    anime_names_to_take = df_first_dates_with_members[ df_first_dates_with_members['anime_members']>=members_limit ]['anime_name']
    df = df[ df['anime_name'].isin(anime_names_to_take) ]

    return df

#===============================================================================
# Stats by anime

def init_dict_variation_by_anime(type):
    dict_variation = {'anime_name':[], 'min_%s' %(type):[], 'max_%s' %(type):[], 'variation_%s' %(type):[], 'relative_variation_%s' %(type):[]}
    return dict_variation

def get_variation_by_anime(dict_variation, anime_name, df_anime, type):
    # Get the list of dates where "type" is not null for this anime
    dates = df_anime[ df_anime['anime_%s' %(type)].notnull() ]['date']
    # Get the first and last date when the data where taken
    first_date = dates.min()
    last_date = dates.max()
    # The first days for the score are relatively random so we pass them
    if type == 'score':
        first_date = first_date + timedelta(days=7)

    # Get the min, max and variation of "type"
    if first_date >= last_date or pd.isnull(first_date):
        min_value = np.nan
        max_value = np.nan
        variation = np.nan
        relative_variation = np.nan
    else:
        min_value = df_anime.loc[ df_anime['date']==first_date, 'anime_%s' %(type) ].item()
        max_value = df_anime.loc[ df_anime['date']==last_date, 'anime_%s' %(type) ].item()
        variation = max_value - min_value
        relative_variation = variation/min_value

    # Add the data of the anime to the dictionnary
    dict_variation['anime_name'].append(anime_name)
    dict_variation['min_%s' %(type)].append(min_value)
    dict_variation['max_%s' %(type)].append(max_value)
    dict_variation['variation_%s' %(type)].append(variation)
    dict_variation['relative_variation_%s' %(type)].append(relative_variation)

    return dict_variation

def get_stats_by_anime(df):
    groups_by_anime = df.groupby(by='anime_name')

    # Dictionnaries that will contains the statistics
    dict_variation_members = init_dict_variation_by_anime('members')
    dict_variation_score = init_dict_variation_by_anime('score')

    # Get the statistics for each anime
    for anime_name, group in groups_by_anime:
        dict_variation_members = get_variation_by_anime(dict_variation_members, anime_name, group, type='members')
        dict_variation_score = get_variation_by_anime(dict_variation_score, anime_name, group, type='score')

    # Put the data about variations in dataframes
    df_variation_members = pd.DataFrame(dict_variation_members)
    df_variation_score = pd.DataFrame(dict_variation_score)

    return {'members':df_variation_members, 'score':df_variation_score}

def plot_stats_by_anime(df_variation, type):
    df_variation.plot(x='anime_name', y='variation_%s' %(type), kind='bar', title='Variation of %s' %(type))
    df_variation.plot(x='anime_name', y='relative_variation_%s' %(type), kind='bar', title='Relative variation of %s' %(type))

def get_limit_variation_anime(df_variation, type, limit_variation):
    limit_variation_anime = df_variation[ df_variation['variation_%s' %(type)]==limit_variation ]
    return limit_variation_anime

def print_limit_variation_anime_stats(limit_variation_anime, type, stat_type):
    print('%s variation of %s' %(stat_type, type))
    print('Anime name : %s' %(limit_variation_anime['anime_name'].item()))
    print('Min %s : %s' %(type, limit_variation_anime['min_%s' %(type)].item()))
    print('Max %s : %s' %(type, limit_variation_anime['max_%s' %(type)].item()))
    print('Variation of %s : %s' %(type, limit_variation_anime['variation_%s' %(type)].item()))
    print('Relative variation of %s : %s' %(type, limit_variation_anime['relative_variation_%s' %(type)].item()))

def print_stats_by_anime(df_variation, type):
    # Get stats
    max_variation = df_variation['variation_%s' %(type)].max()
    min_variation = df_variation['variation_%s' %(type)].min()
    median_variation = df_variation['variation_%s' %(type)].quantile(0.5, interpolation='lower')

    # Get the anime corresponding to the previous stats
    max_variation_anime = get_limit_variation_anime(df_variation, type, max_variation)
    min_variation_anime = get_limit_variation_anime(df_variation, type, min_variation)
    median_variation_anime = get_limit_variation_anime(df_variation, type, median_variation)

    # Print the statistics
    print_limit_variation_anime_stats(max_variation_anime, type, 'Max')
    print_limit_variation_anime_stats(min_variation_anime, type, 'Min')
    print_limit_variation_anime_stats(median_variation_anime, type, 'Median')

#===============================================================================
# Stats by date

def init_dict_variation_by_date(type):
    dict_variation = {'date':[], 'mean_%s' %(type):[], 'std_%s' %(type):[], 'max_%s' %(type):[], 'min_%s' %(type):[]}
    return dict_variation

def get_variation_by_date(dict_variation, date, df_date, type):

    # Get the stats of "type"
    mean_value = df_date['anime_%s' %(type)].mean()
    std_value = df_date['anime_%s' %(type)].std()
    min_value = df_date['anime_%s' %(type)].min()
    max_value = df_date['anime_%s' %(type)].max()

    # Add the stats to the dictionnary
    dict_variation['date'].append(date)
    dict_variation['mean_%s' %(type)].append(mean_value)
    dict_variation['std_%s' %(type)].append(std_value)
    dict_variation['min_%s' %(type)].append(min_value)
    dict_variation['max_%s' %(type)].append(max_value)

    return dict_variation

def get_stats_by_date(df):
    groups_by_date = df.groupby(by='date')

    # Dictionnaries that will contains the statistics
    dict_variation_members = init_dict_variation_by_date('members')
    dict_variation_score = init_dict_variation_by_date('score')

    # Get the statistics for each date
    for date, group in groups_by_date:
        dict_variation_members = get_variation_by_date(dict_variation_members, date, group, type='members')
        dict_variation_score = get_variation_by_date(dict_variation_score, date, group, type='score')

    # Put the data about variations in dataframes
    df_variation_members = pd.DataFrame(dict_variation_members)
    df_variation_score = pd.DataFrame(dict_variation_score)

    return {'members':df_variation_members, 'score':df_variation_score}

def plot_stats_by_date(df_variation, type):
    df_variation.plot(x='date', y=['mean_%s' %(type), 'std_%s' %(type), 'min_%s' %(type), 'max_%s' %(type)], kind='line', title='Mean, Std, Min and Max of %s' %(type))


#===============================================================================
# Main

def main(year, season, new_seasonal_animes, members_limit):
    # Get the data in a dataframe
    df_global = database_to_dataframe(year, season)
    # Format the columns of the dataframe
    df_global = format_dataframe(df_global)
    # Get the new seasonal only
    if new_seasonal_animes:
        df_global = get_new_seasonal_animes_only(df_global, year, season)
    # Get the most popular shows only
    df_global = get_most_popular_animes_only(df_global, members_limit)

    # Get the stats by anime
    df_variations = get_stats_by_anime(df_global)
    print('Number of animes compared : %s' %(len(df_variations['members'].index)))
    for type in ['members', 'score']:
        plot_stats_by_anime(df_variations[type], type)
        print_stats_by_anime(df_variations[type], type)

    # Get the stats by date
    df_variations = get_stats_by_date(df_global)
    print('Number of dates used : %s' %(len(df_variations['members'].index)))
    for type in ['members', 'score']:
        plot_stats_by_date(df_variations[type], type)

    # Show the plots
    plt.show()

if __name__ == '__main__':
    main('2019', 'spring', True, 1000)
