import argparse
import socket
import time
import sys

import mal_scrapper as ms
import update_sheet as us

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
    print("No internet connexion found")
    sys.exit(1)

default_year, default_season = ms.get_default_season()

parser = argparse.ArgumentParser(description='Get statistics from MAL.')
parser.add_argument('--year', dest='year', default=default_year, type=int, help='The year of the season')
parser.add_argument('--season', dest='season', default=default_season, choices=['winter', 'spring', 'summer', 'fall'], help='The season')
parser.add_argument('--type', dest='type', default='TV', nargs='+', choices=['TV', 'ONA', 'OVA', 'Movie', 'Special', 'All'], help='The type(s) of animes to get from mal')
args = parser.parse_args()

data = ms.get_stats(args.year, args.season, args.type)

us.update_sheet(args.year, args.season, data)
