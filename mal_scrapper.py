import requests as r
from bs4 import BeautifulSoup
from time import gmtime, strftime
import sys

def get_default_season():
    # The url of the site
    mal_site = "https://myanimelist.net/anime/season"

    # We get the source code of the default season page of MAL
    mal_request = r.get(mal_site)
    if mal_request.status_code != r.codes.ok:
        print("Myanimelist is down", file=sys.stderr)
        sys.exit(1)
    soup = BeautifulSoup(mal_request.text, 'html.parser')

    # We get the year and season in the web page
    title = soup.title.text.strip().split(' ')
    season = title[0].lower()
    year = title[1]
    
    return year, season

def get_stats(year, season, type):
    # The url of the site where we take the data
    mal_site = "https://myanimelist.net/anime/season/%s/%s" %(year, season)

    # Get the source code of the web page
    mal_request = r.get(mal_site)
    if mal_request.status_code != r.codes.ok:
        print("Myanimelist is down", file=sys.stderr)
        sys.exit(1)
    soup = BeautifulSoup(mal_request.text, 'html.parser')

    # Get the data from the web page
    animes_stats = []
    for tag in soup.find_all("a", attrs={"class":"link-image"}):
        animes_stats.append({'anime_name':tag.text})
    for index, tag in enumerate(soup.find_all("span", attrs={"title":"Members"})):
        animes_stats[index]['anime_members'] = tag.text.strip().replace(',', '')
    for index, tag in enumerate(soup.find_all("span", attrs={"title":"Score"})):
        animes_stats[index]['anime_score'] = tag.text.strip().replace('.', ',')
    for index, tag in enumerate(soup.find_all("div", attrs={"class":"info"})):
        animes_stats[index]['anime_type'] = tag.text.strip().split("-")[0].strip()
        seasonal_type = tag.parent.parent.parent.find('div', attrs={'class':'anime-header'}).text
        if seasonal_type.startswith('TV'):
            animes_stats[index]['anime_seasonal_type'] = seasonal_type.split()[1][1:-1]
        else:
            animes_stats[index]['anime_seasonal_type'] = 'None'

    # Add the date to the data
    now = strftime("%Y-%m-%d", gmtime())
    for anime_stat in animes_stats:
        anime_stat['date'] = now

    # Only keep the anime of the type that interested us
    if 'All' not in type:
        animes = [ anime for anime in animes_stats if anime['anime_type'] in type ]

    return animes
