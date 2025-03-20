"""This module contains constants for individual adjusting of the program."""

# %%
###################################################################################################
# Local IP for use on local machine
LOKALE_IP = ''

# Path to remote database on local machine
PFAD_DB_LOKAL = ''

# Fixed number of pages of the news website to be scraped per order
ANZAHL_SEITEN = 3

# Average seconds to sleep between scraping of two pages of the news website
SCHLAFEN_SEKUNDEN = 4


##################################################
# Limiting the number of pages which can be scraped in a specific timeframe (summed over all active
# users of the web app), i. e. rate limit

# Timeframe for rate limit (in seconds)
ZEITRAUM_FUER_RATELIMIT = 180

# Maximum number of pages of the news website which can be scraped in ZEITRAUM_FUER_RATELIMIT
# (summed over all active users)
N_FUER_RATELIMIT = 9
