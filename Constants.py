"""This module contains constants for individual adjusting of the program."""

# %%
###################################################################################################
# Local IP for use on local machine
LOKALE_IP = ''

# Path to remote database on local machine
Pfad_DB_lokal = ''

# Number of pages of the news website to be scraped per order
ANZAHL_SEITEN = 3

# Time to sleep between scraping of two pages of the news website
SCHLAFEN_SEKUNDEN = 4


##################################################
# Limiting number of pages which can be scraped in a specific timeframe (summed over all active 
# users of the web app)

# Timeframe in seconds
ZEITRAUM_FUER_LIMIT = 60

# Maximum number of pages which can be scraped in ZEITRAUM_FUER_LIMIT
N_FUER_LIMIT = 6