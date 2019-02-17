mal-stats - A tool to automatically make statistics from myanimelist.net seasonal animes on a google sheet.

- [INSTALLATION](#installation)
- [DESCRIPTION](#description)
- [USE](#use)
- [OPTIONS](#options)
- [FUTUR](#futur)

# INSTALLATION

To have the program working, you need to go on this page : https://developers.google.com/sheets/api/quickstart/python and click on the button "ENABLE THE GOOGLE SHEET API". Then, you just need to put the file `credentials.json` in a `GS_resources` directory.

To install all the libraries the program needs, launch this command :

    pip install -r requirements.txt

# DESCRIPTION

A scrapping program to get information (note and members) on seasonal animes on the site myanimelist.net.
Then, it puts the information in a google spreadsheet called `mal_stats`. It creates one sheet per season.

# USE

    python mal-stats.py [options]

# OPTIONS

- `-h, --help` : The help message.
- `--season {winter,spring,summer,fall}` : The season.
- `--year <year>` : This option allows you to select the year.
- `--type {TV,ONA,OVA,Movie,Special,All} [{TV,ONA,OVA,Movie,Special,All} ...]` : The type(s) of animes to get from mal.

# FUTUR

- Finish the README.md
- Better template
- Add automatic calculation of some stats (variation of members...)
