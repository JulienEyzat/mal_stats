import mal_stats as ms
import update_sheet as us

year = "2019"
season = "winter"

data = ms.get_stats(year, season)

us.update_sheet(year, season, data)
