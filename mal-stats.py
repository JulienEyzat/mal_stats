import argparse

import mal_scrapper as ms
import update_sheet as us

default_year, default_season = ms.get_default_season()

parser = argparse.ArgumentParser(description='Get statistics from MAL.')
parser.add_argument('--year', dest='year', default=default_year, type=int, help='The year of the season')
parser.add_argument('--season', dest='season', default=default_season, choices=['winter', 'spring', 'summer', 'fall'], help='The season')
parser.add_argument('--type', dest='type', default='TV', nargs='+', choices=['TV', 'ONA', 'OVA', 'Movie', 'Special', 'All'], help='The type(s) of animes to get from mal')
args = parser.parse_args()

data = ms.get_stats(args.year, args.season, args.type)

us.update_sheet(args.year, args.season, data)
