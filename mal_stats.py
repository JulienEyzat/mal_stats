import requests as r
from bs4 import BeautifulSoup
from time import gmtime, strftime

def get_default_season():
    mal_site = "https://myanimelist.net/anime/season"
    mal_request = r.get(mal_site)
    soup = BeautifulSoup(mal_request.text, 'html.parser')
    title = soup.title.text.strip().split(' ')
    season = title[0].lower()
    year = title[1]
    return year, season

def get_stats(year, season):
    now = strftime("%a, %Y-%m-%d %H:%M:%S", gmtime())
    mal_site = "https://myanimelist.net/anime/season/%s/%s" %(year, season)

    mal_request = r.get(mal_site)
    soup = BeautifulSoup(mal_request.text, 'html.parser')
    animes_names = []
    animes_members = []
    animes_scores = []
    animes_type = []
    for i in soup.find_all("a", attrs={"class":"link-image"}):
        animes_names.append(i.text)
    for i in soup.find_all("span", attrs={"title":"Members"}):
        animes_members.append(i.text.strip())
    for i in soup.find_all("span", attrs={"title":"Score"}):
        animes_scores.append(i.text.strip())
    for i in soup.find_all("div", attrs={"class":"info"}):
        animes_type.append(i.text.strip().split("-")[0])

    now_tab = [ now for i in range(len(animes_names))]
    animes = zip(animes_names, animes_members, animes_scores, animes_type, now_tab)

    return list(animes)
