"""This module contains the classes which do the actual work for
seperate task areas. They communicate via the class Eventmanager
which is in a seperate module.

Classes:\n
    SQL_Worker -- An instance of this class can handle all SQL related
    actions in the web app.\n
    Scraper_Worker -- An instance of this class can handle all scraping
    related actions in the web app.\n
    Analyzer_Worker -- An instance of this class can handle all
    analyzing related actions in the web app.
"""

# %%
###################################################################################################
import streamlit

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
import Constants
import Helpers

from SQL_Schema import SQL_Basis
from SQL_Schema import SQL_Klasse_Tracker

from Eventmanager import Eventmanager

from User_Interface import User_Interface


# %%
###################################################################################################
class SQL_Worker:
    """An instance of this class can handle all SQL related actions in
    the web app.
    
    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        UI -- Instance of User_Interface to work with\n
        Engine_erstellt -- Engine for postgreSQL database\n
        SQL_Session_Macher -- Instance of sessionmaker which works with
        attribute Engine_erstellt\n
        SQL_Session_erstellt -- Active SQL Session of the instance to
        work with\n
        Tracker_Objekt -- Object from database query which holds
        information about the current workload of the web app
        caused by all users
        
    Public methods:\n
        Funk_SQL_Tracker_updaten -- Checks if a scraping order is
        allowed to be executed.\n
        Funk_SQL_add_und_commit_all -- Adds and commits all (changed)
        objects from a list to the database.\n
        Funk_SQL_commit -- Executes a controlled commit to the database
        with rollback if failed.\n
        Funk_SQL_neue_Session_erstellen -- Renews the SQL Session in
        attribute SQL_Session_erstellt.\n
        Funk_SQL_Session_close -- Closes the SQL Session in attribute
        SQL_Session_erstellt.\n
        Funk_SQL_Schema_erstellen -- Creates the SQL database schema.

    Private methods:\n
        _Funk_SQL_Engine_erstellen -- Returns a created engine for a
        postgreSQL database.\n
        _Funk_DB_Pfad_erstellen -- Returns path of postgreSQL database
        on local machine.
    """

    def __init__(
            self,
            Init_UI: User_Interface
            ):
        """Inits SQL_Worker.

        Keyword arguments:\n
        Init_UI -- Active instance of class User_Interface
        """
        self.UI = Init_UI
        
        self.Engine_erstellt = SQL_Worker._Funk_SQL_Engine_erstellen()

        self.SQL_Session_Macher = sessionmaker(bind=self.Engine_erstellt)
        self.SQL_Session_erstellt = self.SQL_Session_Macher() 

        self.Funk_SQL_Schema_erstellen()


    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _Funk_SQL_Engine_erstellen():
        """Returns a created engine for a postgreSQL database."""
        if socket.gethostbyname(socket.gethostname()) == Constants.LOKALE_IP:
            DB_Pfad = SQL_Worker._Funk_DB_Pfad_erstellen()
        else:
            DB_Pfad = str(os.environ['DATABASE_URL']).replace('postgres', 'postgresql')

        SQL_Engine = create_engine(
            DB_Pfad,
            echo=False,
            poolclass=sqlalchemy.pool.NullPool
            )

        return(SQL_Engine)
    
    
    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _Funk_DB_Pfad_erstellen():
        """Returns path of postgreSQL database on local machine."""
        Pfad_aktuell = subprocess.Popen(
            Constants.Pfad_DB_lokal,
            shell=True,
            stdout=subprocess.PIPE
        ).stdout.read()
        
        Pfad_aktuell_formatiert = copy.deepcopy(
            Pfad_aktuell. \
            decode(). \
            split('\n')[1]. \
            split(' ')[1]. \
            replace('postgres', 'postgresql')
            )

        return(Pfad_aktuell_formatiert)
        
        
    def Funk_SQL_Tracker_updaten(
            self,
            Arg_Anzahl_Seiten: int
            ):
        """Returns 'Ja' if a scraping order is allowed to be executed,
        otherwise returns 'Nein'.
        
        Keyword arguments:\n
        Arg_Anzahl_Seiten -- Number of pages that should be scraped
        """
        Zeit_jetzt = datetime.datetime.now()
        Zeit_jetzt_stamp = int(Zeit_jetzt.timestamp())
        Flagge_Ausfuehren = 'Ja'

        # The following two constants limit the number of pages to be scraped in one minute
        # (considering all active users)
        ZEITRAUM_FUER_LIMIT = Constants.ZEITRAUM_FUER_LIMIT
        N_FUER_LIMIT = Constants.N_FUER_LIMIT

        # SQL query to get current status of limit
        self.Tracker_Objekt = self.SQL_Session_erstellt.query(SQL_Klasse_Tracker).first()
        
        # Create new object Tracker_Object if there is no tracker object in the database
        if self.Tracker_Objekt == None:
            self.Tracker_Objekt=SQL_Klasse_Tracker(
                Tracker_ID='Tracker_00',
                Letzter_Job_Zeit=str(Zeit_jetzt),
                Letzter_Job_Zeit_stamp=Zeit_jetzt_stamp,
                Summe_n_aktuell_in_Zeitraum=Arg_Anzahl_Seiten,
                Letzte_Nullung_stamp=Zeit_jetzt_stamp
                )
        
        # Check if the incoming order suceeds the limit for simultaneously processed orders over
        # all users
        elif self.Tracker_Objekt != None:
            Letzte_Nullung_vor_Sek = Zeit_jetzt_stamp - self.Tracker_Objekt.Letzte_Nullung_stamp
            Naechste_Nullung_in_Sek = ZEITRAUM_FUER_LIMIT - Letzte_Nullung_vor_Sek

            if Letzte_Nullung_vor_Sek > ZEITRAUM_FUER_LIMIT:
                setattr(self.Tracker_Objekt, 'Summe_n_aktuell_in_Zeitraum', 0)
                setattr(self.Tracker_Objekt, 'Letzte_Nullung_stamp', Zeit_jetzt_stamp)
                self.Funk_SQL_add_und_commit_all([self.Tracker_Objekt])

            Zeit_Diff_letzter_Job = Zeit_jetzt_stamp - self.Tracker_Objekt.Letzter_Job_Zeit_stamp
            
            if Zeit_Diff_letzter_Job > ZEITRAUM_FUER_LIMIT:
                pass

            elif Zeit_Diff_letzter_Job <= ZEITRAUM_FUER_LIMIT:
                Kontingent_offen = N_FUER_LIMIT - self.Tracker_Objekt.Summe_n_aktuell_in_Zeitraum
                if Kontingent_offen >= Arg_Anzahl_Seiten:
                    pass
                else:
                    Flagge_Ausfuehren = 'Nein'

            # If the limit is not reached, allow the processing of the order
            if Flagge_Ausfuehren == 'Ja':
                setattr(self.Tracker_Objekt, 'Summe_n_aktuell_in_Zeitraum',
                        self.Tracker_Objekt.Summe_n_aktuell_in_Zeitraum + Arg_Anzahl_Seiten)
                setattr(self.Tracker_Objekt, 'Letzter_Job_Zeit', str(Zeit_jetzt))
                setattr(self.Tracker_Objekt, 'Letzter_Job_Zeit_stamp', Zeit_jetzt_stamp)

        self.Funk_SQL_add_und_commit_all([self.Tracker_Objekt])

        # If the limit is reached, do not allow the processing of the order and stop script from
        # running
        if Flagge_Ausfuehren == 'Nein':            
            with self.UI.Platzhalter_Ausgabe_Warnung:
                streamlit.warning(f'ACHTUNG!: In den letzten {ZEITRAUM_FUER_LIMIT} Sekunden \
                                  haben bereits zu viele Personen einen Auftrag an \
                                  diese Web App gesendet. Bitte versuche es in \
                                  {Naechste_Nullung_in_Sek} Sekunden erneut!')
                
            self.UI.Funk_Aufraeumen()
        
        return(Flagge_Ausfuehren)
    
    
    def Funk_SQL_add_und_commit_all(
            self,
            Arg_Liste_Objekte: list
            ):
        """Adds and commits all (changed) objects in list
        Arg_Liste_Objekte to the database.
        
        Keyword arguments:\n
        Arg_Liste_Objekte -- List of (changed) objects to commit
        """
        self.SQL_Session_erstellt.add_all(Arg_Liste_Objekte)
        self.Funk_SQL_commit()


    def Funk_SQL_commit(self):
        """Executes a controlled commit to the database with rollback
        if failed.
        """
        try:
            self.SQL_Session_erstellt.commit()
        except IntegrityError as Integrity_Fehler:
            try:
                self.SQL_Session_erstellt.rollback()
                Helpers.Funk_Drucken('BESTAETIGUNG!: Rollback nach IntegrityError erfolgreich')                
            except Exception as Fehler:
                pass
                Helpers.Funk_Drucken('ACHTUNG!: Fehler bei rollback nach IntegrityError')
                
        except Exception as Fehler:
            pass
            Fehler_Name = str(type(Fehler).__name__)
            Helpers.Funk_Drucken(f'BESTAETIGUNG!: Rollback nach {Fehler_Name} erfolgreich')  
            try:
                self.SQL_Session_erstellt.rollback()
                Helpers.Funk_Drucken(f'ACHTUNG!: Fehler bei rollback nach {Fehler_Name}')
            except:
                pass


    def Funk_SQL_neue_Session_erstellen(self):
        """Renews the SQL Session in attribute SQL_Session_erstellt."""
        self.Funk_SQL_Session_close()
        self.SQL_Session_Macher = sessionmaker(bind=self.Engine_erstellt)
        self.SQL_Session_erstellt = self.SQL_Session_Macher()   
        
    
    def Funk_SQL_Session_close(self):
        """Closes the SQL Session in attribute SQL_Session_erstellt."""
        try:
            self.SQL_Session_erstellt.close()
        except Exception as Fehler:
            Helpers.Funk_Drucken('ACHTUNG!: Fehler in SQL_Worker.Funk_SQL_Session_close')
            Helpers.Funk_Drucken('Exception:', str(type(Fehler).__name__))
            Helpers.Funk_Drucken('Fehler:', Fehler)


    def Funk_SQL_Schema_erstellen(self):
        """Creates the SQL database schema."""
        SQL_Basis.metadata.create_all(self.Engine_erstellt)



# %%
###################################################################################################
class Scraper_Worker:
    """An instance of this class can handle all scraping related
    actions in the web app.
    
    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        Eventmanager -- Instance of Eventmanager to work with\n
        UI -- Instance of User_Interface to work with\n
        Suchbegriff -- Current search term\n
        Anzahl_Seiten -- Current number of pages that should be
        scraped\n
        Liste_Ueberschriften -- Current list of scraped article
        headlines\n
        Liste_Vorschautexte -- Current list of scraped article preview
        texts\n
        Gesammelte_Texte -- Dict containing data of attributes
        Liste_Ueberschriften and Liste_Vorschautexte\n
        Cookies -- Cookies to work with while scraping\n
        HTMLObjekt -- Current HTML to work with\n
        Link_naechste_Seite -- Link to next news page relative to the
        current one
        
    Public methods:\n
        Funk_Auftrag_annehmen -- This function receives the scraping
        order from the Eventmanager. It returns the dict of the scraped
        texts.

    Private methods:\n
        _Funk_Arbeiten -- Scrapes the news with the help of the other
        private methods.\n
        _Funk_HTMLObjekt_erste_Seite_bearbeiten -- Updates attribute
        HTMLObjekt to HTML of the first news page for the current
        search term.\n
        _Funk_HTMLObjekt_naechste_Seite_bearbeiten -- Updates attribute
        HTMLObjekt to HTML of the next news page following the current
        one.\n
        _Funk_Link_naechste_Seite_updaten -- Updates attribute
        Link_naechste_Seite to URL of the next news page following the
        current one.\n
        _Funk_Liste_Ueberschriften_erweitern -- Appends all article
        headlines from current news page to list in attribute
        Liste_Ueberschriften.\n
        _Funk_Liste_Vorschautexte_erweitern -- Appends all article
        preview texts from current news page to list in attribute
        Liste_Vorschautexte.\n
        _Funk_HTMLObjekt_erstellen -- Returns HTML.
    """

    def __init__(
            self,
            Init_Eventmanager: Eventmanager,
            Init_UI: User_Interface,
            Init_Suchbegriff: str = '',
            Init_Anzahl_Seiten: int = Constants.ANZAHL_SEITEN
            ):
        """Inits Scraper_Worker.

        Keyword arguments:\n
        Init_Eventamanager -- Active instance of class Eventmanager\n
        Init_UI -- Active instance of class User_Interface\n
        Init_Suchbegriff -- Current search term\n
        Init_Anzahl_Seiten -- Current number of pages that should be
        scraped
        """
        self.Eventmanager = Init_Eventmanager
        self.UI = Init_UI
        self.Suchbegriff = Init_Suchbegriff
        self.Anzahl_Seiten = Init_Anzahl_Seiten
        
        self.Liste_Ueberschriften = []
        self.Liste_Vorschautexte = []
        self.Gesammelte_Texte = {}
        
        self.Cookies = streamlit.session_state['Cookies']

    def Funk_Auftrag_annehmen(
            self,
            Arg_Worker: SQL_Worker,
            Arg_Auftrag_Suchbegriff: str,
            Arg_Auftrag_Anzahl_Seiten: int):
        """This function receives the scraping order from the
        Eventmanager. It returns the dict of the scraped texts.
        
        Keyword arguments:\n
        Arg_Worker -- Active instance of class SQL_Worker to work
        with\n
        Arg_Auftrag_Suchbegriff -- Search term of incoming order\n
        Arg_Auftrag_Anzahl_Seiten -- Number of news pages that should
        be scraped for incoming order\n
        """ 
        if Arg_Auftrag_Anzahl_Seiten > Constants.ANZAHL_SEITEN:
            Seiten = 3
            Helpers.Funk_Drucken(f'ACHTUNG!: Auftrag hatte {Arg_Auftrag_Anzahl_Seiten} Seiten \
                                 in Arg_Auftrag_Anzahl_Seiten.\
                                 Es werden daher nur {Seiten} Seiten durchsucht.')
        else:
            Seiten = Arg_Auftrag_Anzahl_Seiten
            
        # If the limit is not reached, allow the processing of the order
        if Arg_Worker.Funk_SQL_Tracker_updaten(Arg_Anzahl_Seiten = Seiten) == 'Ja':
            self.Suchbegriff = Arg_Auftrag_Suchbegriff         
            self.Anzahl_Seiten = Arg_Auftrag_Anzahl_Seiten

            self.Liste_Ueberschriften = []
            self.Liste_Vorschautexte = []
            self.Gesammelte_Texte = {}
            
            with self.UI.Platzhalter_Ausgabe_Spinner_02:
                with streamlit.spinner('Deine Daten werden gerade gesammelt.'):
                    self._Funk_Arbeiten()
            
            # Tell the Eventmanager that the scraping is done
            self.Eventmanager.Funk_Event_eingetreten(
                Arg_Event_Name='Fertig_gescraped',
                Arg_Argumente_von_Event={
                    'Arg_Auftrag_Suchbegriff': self.Suchbegriff,
                    'Arg_Auftrag_Liste_Ueberschriften': self.Liste_Ueberschriften,
                    'Arg_Auftrag_Liste_Vorschautexte': self.Liste_Vorschautexte,
                    'Arg_Auftrag_Sentiment_Flagge': 'Ja'
                    }
                )


    def _Funk_Arbeiten(self):   
        """Scrapes the news with the help of the other private
        methods.
        """   
        self._Funk_HTMLObjekt_erste_Seite_bearbeiten()
        self._Funk_Liste_Ueberschriften_erweitern()
        self._Funk_Liste_Vorschautexte_erweitern()
        
        if self.Anzahl_Seiten > 1:
            for i in range(0, self.Anzahl_Seiten - 1):
                Helpers.Funk_Schlafen(Arg_Sekunden=Constants.SCHLAFEN_SEKUNDEN)
                self._Funk_Link_naechste_Seite_updaten()
                self._Funk_HTMLObjekt_naechste_Seite_bearbeiten()
                self._Funk_Liste_Ueberschriften_erweitern()
                self._Funk_Liste_Vorschautexte_erweitern()

        self.Gesammelte_Texte['Ueberschriften'] = self.Liste_Ueberschriften
        self.Gesammelte_Texte['Vorschautexte'] = self.Liste_Vorschautexte

    
    def _Funk_HTMLObjekt_erste_Seite_bearbeiten(self):
        """Updates attribute HTMLObjekt to HTML of the first news page
        for the current search term. 
        """
        self.HTMLObjekt = self._Funk_HTMLObjekt_erstellen(
            Arg_Link=None,
            Arg_Suchbegriff=self.Suchbegriff
            )
    
    
    def _Funk_HTMLObjekt_naechste_Seite_bearbeiten(self):
        """Updates attribute HTMLObjekt to HTML of the next news page
        following the current one.
        """
        self.HTMLObjekt = self._Funk_HTMLObjekt_erstellen(
            Arg_Link=self.Link_naechste_Seite,
            Arg_Suchbegriff=None
            )        
    
    
    def _Funk_Link_naechste_Seite_updaten(self):
        """Updates attribute Link_naechste_Seite to URL of the next
        news page following the current one.
        """
        Element_naechste_Seite = self.HTMLObjekt.cssselect('a.nBDE1b.G5eFlf')[-1]
        String_naechste_Seite = Element_naechste_Seite.attrib['href']
        self.Link_naechste_Seite = 'https://www.google.com' + String_naechste_Seite
        
    
    def _Funk_Liste_Ueberschriften_erweitern(self):
        """"Appends all article headlines from current news page to
        list in attribute Liste_Ueberschriften.
        """
        Liste_Elemente_Ueberschriften = self.HTMLObjekt. \
            cssselect('h3.zBAuLc.l97dzf > div.BNeawe.vvjwJb.AP7Wnd')
        
        for x in Liste_Elemente_Ueberschriften:
            Text = x.text_content()
            self.Liste_Ueberschriften.append(Text)
            

    def _Funk_Liste_Vorschautexte_erweitern(self):
        """Appends all article preview texts from current news page to
        list in attribute Liste_Vorschautexte.
        """
        Liste_Elemente_Vorschautexte = self.HTMLObjekt. \
            cssselect('div.BNeawe.s3v9rd.AP7Wnd > div:nth-child(1)')
        
        for x in Liste_Elemente_Vorschautexte:
            Text = x.text_content()            
            self.Liste_Vorschautexte.append(Text)


    def _Funk_HTMLObjekt_erstellen(
            self,
            Arg_Link: str = None,
            Arg_Suchbegriff: str = None
            ):
        """Returns HTML."""
        with requests.Session() as Sitzung:
            Sitzung.headers.update({'Accept-Language': 'de;q=1.0, en;q=0.0, *;q=0.0'})

            if Arg_Link != None:
                Link = Arg_Link
            elif Arg_Suchbegriff != None:
                Link = f'https://www.google.com/search?q={Arg_Suchbegriff}&tbm=nws&\
                    tbs=lr:lang_1de&lr=lang_de'
            
            Antwort = Sitzung.get(
                Link,
                cookies = self.Cookies
                )

            Helpers.Funk_Drucken('Antwort:', Antwort)
            Antwort_HTML = Antwort.content.decode('ISO-8859-1')
            Baum_HTML = html.fromstring(Antwort_HTML)
          
            return(Baum_HTML)
    


# %%
###################################################################################################
class Analyzer_Worker:
    """An instance of this class can handle all analyzing related
    actions in the web app.

    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        Eventmanager -- Instance of Eventmanager to work with\n
        UI -- Instance of User_Interface to work with\n
        Suchbegriff -- Current search term\n
        Liste_Ueberschriften -- Current list of scraped article
        headlines\n
        Liste_Vorschautexte -- Current list of scraped article preview
        texts\n
        Sentiment_Flagge -- Flag to signal whether sentiment analysis
        should be performed\n
        Mittelwert_Sentiment -- Current value for coloring of the word
        cloud, relevant for private method _Funk_Wordcloud_zeigen\n
        Liste_fuer_Wordcloud -- Current list with data for word cloud
        object to create\n
        Liste_fuer_Sentiment -- Current list with data for mean
        sentiment calculation\n
        Modell_Sentiment -- Model for sentiment analysis\n
        Tagger -- Tagger for sentiment analysis\n
        Liste_Ueberschriften_clean -- Current list with cleaned data
        from article headlines\n
        Liste_Vorschautexte_clean -- Current list with cleaned data
        from article preview texts\n
        Liste_Gesamter_Text_clean -- Current lsit with cleaned data
        from attributes Liste_Ueberschriften_clean and
        Liste_Vorschautexte_clean
    
    Public methods:\n
        Funk_Auftrag_annehmen -- This function receives the analyzing
        order from the Eventmanager. It returns the word cloud array
        object of the scraped texts.\n

    Private methods:\n
        _Funk_Modell_Sentiment_erstellen -- Returns model for sentiment
        analysis.\n
        _Funk_Tagger_erstellen -- Returns tagger for sentiment
        analysis.\n
        _Funk_Arbeiten -- Analyzes the texts with the help of the other
        private methods.\n
        _Funk_Texte_verarbeiten -- Processes the texts in attributes
        Liste_Ueberschriften und Liste_Vorschautexte.\n
        _Funk_Sentiment_analysieren -- Analyzes the sentiment and store
        results in attribute Buch_fuer_Wordcloud.\n
        _Funk_Wordcloud_erstellen -- Creates word cloud object in
        attribute Wordcloud_Objekt from data in attribute
        Buch_fuer_Wordcloud.\n
        _Funk_Wordcloud_konvertieren -- Converts attribute
        Wordcloud_Objekt to word cloud array object and stores it in
        attributeWordcloud_Objekt_Array.\n
        _Funk_Wordcloud_faerben -- Calculates the color of the word
        cloud and returns it.\n
        """
    
    def __init__(
            self,
            Init_Eventmanager: Eventmanager,
            Init_UI: User_Interface,
            Init_Suchbegriff: str = '',
            Init_Liste_Ueberschriften: list = [],
            Init_Liste_Vorschautexte: list = [], 
            Init_Sentiment_Flagge: str = 'Nein'):
        """Inits Analyzer_Worker.

        Keyword arguments:\n
        Init_Eventamanager -- Active instance of class Eventmanager\n
        Init_UI -- Active instance of class User_Interface\n
        Init_Suchbegriff -- Current search term\n
        Init_Liste_Ueberschriften -- Current list of scraped article
        headlines\n
        Init_Liste_Vorschautexte -- Current list of scraped article
        preview texts\n
        Init_Sentiment_Flagge -- Flag to signal whether sentiment
        analysis should be performed\n
        """
        self.Eventmanager = Init_Eventmanager
        self.UI = Init_UI
        self.Suchbegriff = Init_Suchbegriff
        self.Liste_Ueberschriften = Init_Liste_Ueberschriften
        self.Liste_Vorschautexte = Init_Liste_Vorschautexte
        self.Sentiment_Flagge = Init_Sentiment_Flagge
        
        self.Mittelwert_Sentiment = 99.0
        self.Liste_fuer_Wordcloud = []
        self.Liste_fuer_Sentiment = []

        self.Modell_Sentiment = Analyzer_Worker._Funk_Modell_Sentiment_erstellen()
        self.Tagger = Analyzer_Worker._Funk_Tagger_erstellen()
    

    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _Funk_Modell_Sentiment_erstellen():
        """Returns model for sentiment analysis."""
        Modell_Sentiment = SentimentModel() 
        return(Modell_Sentiment)
    

    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _Funk_Tagger_erstellen():
        """Returns tagger for sentiment analysis."""
        Tagger = HanoverTagger.HanoverTagger('morphmodel_ger.pgz') 
        return(Tagger)


    def Funk_Auftrag_annehmen(
            self,
            Arg_Auftrag_Suchbegriff: str,
            Arg_Auftrag_Liste_Ueberschriften: list,
            Arg_Auftrag_Liste_Vorschautexte: list,
            Arg_Auftrag_Sentiment_Flagge: str = 'Nein'):
        """This function receives the analyzing order from the
        Eventmanager. It returns the word cloud array object of the
        scraped texts.
        
        Keyword arguments:\n
        Arg_Auftrag_Suchbegriff -- Search term of incoming order\n
        Arg_Auftrag_Liste_Ueberschriften -- List of scraped article
        headlines of incoming order\n
        Arg_Auftrag_Liste_Vorschautexte -- List of scraped article
        preview texts of incoming order\n
        Arg_Auftrag_Sentiment_Flagge -- Flag to signal whether
        sentiment analysis should be performed for incoming order\n
        """ 
        self.Suchbegriff = Arg_Auftrag_Suchbegriff
        self.Liste_Ueberschriften = Arg_Auftrag_Liste_Ueberschriften
        self.Liste_Vorschautexte = Arg_Auftrag_Liste_Vorschautexte
        self.Sentiment_Flagge = Arg_Auftrag_Sentiment_Flagge

        self.Mittelwert_Sentiment = 99.0
        self.Liste_fuer_Wordcloud = []
        self.Liste_fuer_Sentiment = []
        
        with self.UI.Platzhalter_Ausgabe_Spinner_02:
            with streamlit.spinner('Deine Daten werden gerade analysiert.'):
                self._Funk_Arbeiten()
        
        # Tell the Eventmanager that the analyzing is done
        self.Eventmanager.Funk_Event_eingetreten(
            Arg_Event_Name='Fertig_analysiert',
            Arg_Argumente_von_Event={'Arg_Objekt_zum_Einfuegen': self.Wordcloud_Objekt_Array}
            )

    
    def _Funk_Arbeiten(self):
        """Analyzes the texts with the help of the other private
        methods.\n
        """
        self._Funk_Texte_verarbeiten()
        self._Funk_Wordcloud_erstellen()
        self._Funk_Wordcloud_konvertieren()
        
        streamlit.session_state['Arrays_fuer_Clouds'][self.Suchbegriff] = {
            'Array': self.Wordcloud_Objekt_Array,
            'Rohdaten_Ueberschriften': self.Liste_Ueberschriften,
            'Rohdaten_Vorschautexte': self.Liste_Vorschautexte,
            'Verarbeitete_Ueberschriften': self.Liste_Ueberschriften_clean,
            'Verarbeitete_Vorschautexte': self.Liste_Vorschautexte_clean
            }
        
        # If there are more than 3 tabs with different search terms, delete the oldest one
        if len(streamlit.session_state['Arrays_fuer_Clouds'].keys()) > 3:
            Liste_Suchbeggriffe_in_state = list(streamlit.session_state['Arrays_fuer_Clouds'].\
                                                keys())
            Liste_Suchbeggriffe_in_state.reverse()
            
            for i, x in enumerate (Liste_Suchbeggriffe_in_state):
                if i > 2:
                    del(streamlit.session_state['Arrays_fuer_Clouds'][x])

        streamlit.session_state['Neues_Array_erstellt'] = True


    def _Funk_Texte_verarbeiten(self):
        """Processes the texts in attributes Liste_Ueberschriften und
        Liste_Vorschautexte.\n
        """
        self.Liste_Ueberschriften_clean = []
        for x in self.Liste_Ueberschriften:
            if Import_Funk_Detektieren(x) == 'de':
                self.Liste_Ueberschriften_clean.append(x) 
        
        self.Liste_Vorschautexte_clean = []
        for x in self.Liste_Vorschautexte:
            Index = (x.find('vor', len(x)-20))
            Clean_x = x[:Index]
            if Import_Funk_Detektieren(Clean_x) == 'de':
                self.Liste_Vorschautexte_clean.append(Clean_x)
        
        self.Liste_Gesamter_Text_clean = self.Liste_Ueberschriften_clean \
            + self.Liste_Vorschautexte_clean

        if len(self.Liste_Gesamter_Text_clean) < 1:
            with self.UI.Platzhalter_Ausgabe_Warnung:
                streamlit.warning(f'ACHTUNG!: Die gesammelte Textmenge ist zu gering. \
                                  Wahscheinlich waren zu viele Suchergebnisse nicht in \
                                  deutscher Sprache. Bitte versuche es mit einem anderen \
                                  Suchbegriff erneut!')
                
            self.UI.Funk_Aufraeumen()

        self._Funk_Sentiment_analysieren(Arg_Liste=self.Liste_Ueberschriften_clean)
        self._Funk_Sentiment_analysieren(Arg_Liste=self.Liste_Vorschautexte_clean)
    
            
    def _Funk_Sentiment_analysieren(
            self,
            Arg_Liste: list
            ):
        """Analyzes the sentiment and stores the results in attribute
        Buch_fuer_Wordcloud.\n
        """
        # Analyze the sentiment for each text in the argument Arg_Liste
        for i, x in enumerate(Arg_Liste.copy()):
            if self.Sentiment_Flagge == 'Ja':
                Klassifizierung_x, Wahrscheinlichkeiten_x = self.Modell_Sentiment.\
                    predict_sentiment([x],
                    output_probabilities = True)

                # Weight and label sentiment of analyzed text
                if Klassifizierung_x[0] == 'neutral':
                    Sentiment = 0
                    Sentiment_Wort = 'neutral'
                elif Klassifizierung_x[0] == 'positive':
                    Sentiment = 1
                    Sentiment_Wort = 'positiv'
                elif Klassifizierung_x[0] == 'negative':
                    Sentiment = -1
                    Sentiment_Wort = 'negativ'

                self.Liste_fuer_Sentiment.append(Sentiment)

                Arg_Liste[i] = [x, f' ### Sentiment: {Sentiment_Wort}']
            
            x_ohne_Bindestriche = x.replace('-', ' ')
    
            Liste_Tokens = nltk.tokenize.word_tokenize(x_ohne_Bindestriche, language='german')

            for Wort_x in Liste_Tokens:
                Tuple_Tag = self.Tagger.analyze(Wort_x)

                # Only use verbs and nouns for the word cloud
                if True in (y in Tuple_Tag[1] for y in ['VV']) or Tuple_Tag[1][0] == 'N':
                    self.Liste_fuer_Wordcloud.append(Tuple_Tag[0])
            
            if self.Sentiment_Flagge == 'Ja':
                self.Mittelwert_Sentiment = float(mean(self.Liste_fuer_Sentiment))
            
            # Count how often each word occured
            self.Buch_fuer_Wordcloud = Counter(self.Liste_fuer_Wordcloud)

            for Key_x in self.Buch_fuer_Wordcloud.copy().keys():
                Wert_x = self.Buch_fuer_Wordcloud[Key_x]

                if Wert_x < 4:
                    del(self.Buch_fuer_Wordcloud[Key_x])


    def _Funk_Wordcloud_erstellen(self):
        """Creates word cloud object in attribute Wordcloud_Objekt from
        data in attribute Buch_fuer_Wordcloud.
        """
        self.Wordcloud_Objekt = WordCloud(
            width=1280,
            height=720
            ).generate_from_frequencies(self.Buch_fuer_Wordcloud)
        

    def _Funk_Wordcloud_konvertieren(self):
        """Converts attribute Wordcloud_Objekt to word cloud array
        object and stores it in attributeWordcloud_Objekt_Array.
        """
        self.Wordcloud_Objekt.recolor(
            color_func=Analyzer_Worker._Funk_Wordcloud_faerben,
            random_state=self.Mittelwert_Sentiment
            )
        
        self.Wordcloud_Objekt_Array = self.Wordcloud_Objekt.to_array()


    @staticmethod
    def _Funk_Wordcloud_faerben(
            font_size,
            position,
            orientation,
            random_state: float,
            **kwargs
            ):
        """Calculates the color of the word cloud and returns it."""
        if random_state == 99.0:
            return('hsl(0, 100%, 100%)')
        
        elif random_state != 99.0:
            Wert_hsl = 60 + random_state*3*60

            if Wert_hsl < 0:
                Wert_hsl = 0
            elif Wert_hsl > 120:
                Wert_hsl = 120

            return(f'hsl({Wert_hsl}, 100%, 50%)')
