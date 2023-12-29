"""This file is the main script for the Newscloud web app. It runs 
from top to bottom every time the user presses the button.
"""

# %%
###################################################################################################
import streamlit
streamlit.set_page_config(page_title='Newscloud', layout='wide', page_icon='💭')


###################################################################################################
with streamlit.spinner('Bitte warte einen Moment, bis der Server aufgewacht ist. \
                        Dieser ist bei längerer Zeit ohne Nutzung der Web App im Stand-by.'):
    import datetime
    import time
    import random
    import pickle
    from collections import Counter
    from statistics import mean
    import socket
    import subprocess
    import copy
    import os
    import http

    import psycopg2
    from psycopg2.errors import ProgrammingError
    from psycopg2.errors import UndefinedTable
    import sqlalchemy
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import Mapped
    from sqlalchemy.orm import mapped_column
    from sqlalchemy.orm import sessionmaker
    
    import requests
    from lxml import html
    from lxml import etree

    from wordcloud import WordCloud
    import nltk
    import HanTa
    from HanTa import HanoverTagger
    from germansentiment import SentimentModel
    from langdetect import detect as Import_Funk_Detektieren
    from langdetect import DetectorFactory as Import_Detektions_Fabrik
    Import_Detektions_Fabrik.seed = 0

    ##################################################
    # Import modules from folder
    import Helpers
    import Constants

    from SQL_Schema import SQL_Basis
    from SQL_Schema import SQL_Klasse_Tracker

    from Workers import SQL_Worker
    from Workers import Scraper_Worker
    from Workers import Analyzer_Worker

    from Eventmanager import Eventmanager

    from User_Interface import User_Interface


# %%
###################################################################################################
# Create Eventmanager object
Eventmanager_A = Eventmanager()

# Create objects for each distinct task (e. g. displaying UI or scraping).
# These objects interact with each other.
User_Interface_A = User_Interface(Init_Eventmanager=Eventmanager_A)
User_Interface_A.Funk_Einrichten()

with User_Interface_A.Platzhalter_Ausgabe_Spinner_01:
    with streamlit.spinner('Bitte warte, bis ich verschwinde, bevor du weitermachst!'):
        SQL_Worker_A = SQL_Worker(Init_UI=User_Interface_A)

        Scraper_A = Scraper_Worker(
            Init_Eventmanager=Eventmanager_A,
            Init_UI=User_Interface_A
            )

        Analyzer_A = Analyzer_Worker(
            Init_Eventmanager=Eventmanager_A,
            Init_UI=User_Interface_A
            )

        # Add different events and subscriber functions to the Eventmanager object 
        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Button_gedrueckt',
            Arg_aufzurufende_Funktion=Scraper_A.Funk_Auftrag_annehmen,
            Arg_Argumente={'Arg_Worker': SQL_Worker_A,
                           'Arg_Auftrag_Anzahl_Seiten': Constants.ANZAHL_SEITEN
                           }
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_gescraped',
            Arg_aufzurufende_Funktion=Analyzer_A.Funk_Auftrag_annehmen,
            Arg_Argumente={}
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_analysiert',
            Arg_aufzurufende_Funktion=User_Interface_A.Funk_Platzhalter_bestuecken,
            Arg_Argumente={'Arg_Objekt_zum_Einfuegen':
                                '<span style="color: hsl(0, 100%, 50%)">Rot </span>'
                                + 'steht für ein negatives, '
                                + '<span style="color: hsl(60, 100%, 50%)">gelb </span>'
                                + 'für ein neutrales und '
                                + '<span style="color: hsl(120, 100%, 50%)">grün </span>'
                                + 'für ein positives Sentiment.',
                           'Arg_Platzhalter': User_Interface_A.Platzhalter_Ausgabe_01
                           }
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_analysiert',
            Arg_aufzurufende_Funktion=User_Interface_A.Funk_Platzhalter_Tabs_bestuecken,
            Arg_Argumente={}
            )
        
        # Check whether there are open jobs
        User_Interface_A.Funk_Jobs_pruefen()

        # Clean up
        User_Interface_A.Funk_Aufraeumen()


# %%
# Stop script from running
streamlit.stop()
