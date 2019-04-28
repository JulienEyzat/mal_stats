import argparse
import socket
import time
import sys

import mal_scrapper as ms
import update_sheet as ush
import update_sqlite as usq
import transfert_database as td

# Check if there is an internet connexion for 1 minute.
def is_internet(host="8.8.8.8", port=53, timeout=3, testing_time=60, sleep_time=1):
    start = time.time()
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception as ex:
            if time.time() - start > testing_time:
                return False
            else:
                time.sleep(sleep_time)

if not is_internet():
    print("No internet connexion found", file=sys.stderr)
    sys.exit(1)

# Parse the arguments given to the application
parser = argparse.ArgumentParser(description='Get statistics from MAL.')
parser.add_argument('--year', dest='year', default=None, type=int, help='The year of the season')
parser.add_argument('--season', dest='season', default=None, choices=['winter', 'spring', 'summer', 'fall'], help='The season')
parser.add_argument('--type', dest='type', default='TV', nargs='+', choices=['TV', 'ONA', 'OVA', 'Movie', 'Special', 'All'], help='The type(s) of animes to get from mal')
parser.add_argument('--database', dest='database', default='google', choices=['google', 'sqlite'], help='The type of database to use to store the data.')
parser.add_argument('--transfert', dest='transfert', nargs=2, choices=['sqlite', 'google'], required=False, help='Transfert the data from the first given database to the second one. Be very careful with this command !')
args = parser.parse_args()

# Get default year and season if not given in argument
if not args.year or not args.season:
    default_year, default_season = ms.get_default_season()
    if not args.year:
        args.year = default_year
    if not args.season:
        args.season = default_season

# If transfert, we transfert the database
if args.transfert:
    src = args.transfert[0]
    dest = args.transfert[1]
    td.transfert_database(source=src, destination=dest, year=args.year, season=args.season)
    print('Transfered %s database to %s database.' %(src, dest))
    sys.exit(0)

print('Getting the stats from MAL')
# Get the data from MAL
data = ms.get_stats(args.year, args.season, args.type)

print('Putting the stats in the database')
# We put the data in the wanted database
if args.database == 'google':
    ush.update_sheet(args.year, args.season, data)
elif args.database == 'sqlite':
    usq.update_sqlite(args.year, args.season, data)
