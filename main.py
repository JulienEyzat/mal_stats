import argparse

import mal_stats as ms
import update_sheet as us


parser = argparse.ArgumentParser(description='Get statistics from MAL.')
parser.add_argument('--year', dest='year', type=int, help='The year of the season')
parser.add_argument('--season', dest='season', choices=['winter', 'spring', 'summer', 'fall'], help='The season')
args = parser.parse_args()

if not args.year or not args.season:
    year, season = ms.get_default_season()
else:
    year = args.year
    season = args.season

data = ms.get_stats(year, season)

us.update_sheet(year, season, data)
