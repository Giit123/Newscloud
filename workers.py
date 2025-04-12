"""This module contains the classes which do the actual work for
seperate task areas. They communicate via the class Eventmanager which
is in a seperate module.

Classes:\n
    sqlWorker -- An instance of this class can perform all SQL related
    actions in the web app.\n
    ScraperWorker -- An instance of this class can perform all scraping
    related actions in the web app.\n
    AnalyzerWorker -- An instance of this class can perform all
    analyzing related actions in the web app.
"""

# %%
###################################################################################################
import streamlit

import datetime
from collections import Counter
from statistics import mean
import socket
import subprocess
import copy
import os

import psycopg2
from psycopg2.errors import ProgrammingError
from psycopg2.errors import UndefinedTable
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

import requests
from lxml import html

from wordcloud import WordCloud
import nltk
import HanTa
from HanTa import HanoverTagger
from germansentiment import SentimentModel
from langdetect import detect as import_funk_detektieren
from langdetect import DetectorFactory as import_detektions_fabrik
import_detektions_fabrik.seed = 0

##################################################
# Import modules from folder
import helpers
import constants
from sql_schema import sql_basis
from sql_schema import sqlKlasseTracker
from eventmanager import Eventmanager
from user_interface import UserInterface


# %%
###################################################################################################
class sqlWorker:
    """An instance of this class can perform all SQL related actions in
    the web app.
    
    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        eventmanager -- Instance of Eventmanager to work with\n
        user_interface -- instance of UserInterface to work with\n
        engine_erstellt -- Engine for postgreSQL database\n
        sql_session_macher -- Instance of sessionmaker which works with
        attribute engine_erstellt\n
        sql_session_erstellt -- Active SQL Session of the instance to
        work with\n
        tracker_objekt -- Object from database query which holds
        information about the current workload of the web app
        caused by all users
        
    Public methods:\n
        funk_sql_tracker_updaten -- Checks if a scraping order is
        allowed to be executed.

    Private methods:\n
        _funk_sql_engine_erstellen -- Returns a created engine for a
        postgreSQL database.\n
        _funk_db_pfad_erstellen -- Returns the path of the postgreSQL
        database on the local machine.\n
        _funk_sql_add_und_commit_all -- Adds and commits all (changed)
        objects from a list to the database.\n
        _funk_sql_commit -- Executes a controlled commit to the
        database with rollback if failed.\n
        _funk_sql_neue_session_erstellen -- Renews the SQL Session in
        attribute sql_session_erstellt.\n
        _funk_sql_session_schliessen -- Closes the SQL Session in
        attribute sql_session_erstellt.\n
        _funk_sql_schema_erstellen -- Creates the SQL database schema.
    """

    def __init__(
            self,
            init_eventmanager: Eventmanager,
            init_user_interface: UserInterface
            ):
        """Inits SQLWorker.

        Keyword arguments:\n
        init_eventmanager -- Active instance of class Eventmanager\n
        init_user_interface -- Active instance of class UserInterface
        """
        self.eventmanager = init_eventmanager
        self.user_interface = init_user_interface
        
        self.engine_erstellt = sqlWorker._funk_sql_engine_erstellen()
        self.sql_session_macher = sessionmaker(bind=self.engine_erstellt)
        self.sql_session_erstellt = self.sql_session_macher() 
        self.tracker_objekt = None

        self._funk_sql_schema_erstellen()


    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _funk_sql_engine_erstellen():
        """Returns a created engine for a postgreSQL database."""
        if socket.gethostbyname(socket.gethostname()) == constants.LOKALE_IP:
            db_pfad = sqlWorker._funk_db_pfad_erstellen()
        else:
            db_pfad = str(os.environ['DATABASE_URL']).replace('postgres', 'postgresql')

        sql_engine = create_engine(
            db_pfad,
            echo=False,
            poolclass=sqlalchemy.pool.NullPool
            )

        return(sql_engine)
    
    
    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _funk_db_pfad_erstellen():
        """Returns the path of the postgreSQL database on the local
        machine.
        """
        pfad_aktuell = subprocess.Popen(
            constants.PFAD_DB_LOKAL,
            shell=True,
            stdout=subprocess.PIPE
        ).stdout.read()
        
        pfad_aktuell_formatiert = copy.deepcopy(
            pfad_aktuell.\
                decode().\
                split('\n')[1].\
                split(' ')[1].\
                replace('postgres', 'postgresql')
            )

        return(pfad_aktuell_formatiert)
        
        
    def funk_sql_tracker_updaten(
            self,
            arg_anzahl_seiten: int
            ):
        """Returns True if a scraping order is allowed to be executed,
        otherwise returns False.
        
        Keyword arguments:\n
        Arg_Stichprobe -- Number of offers that should be scraped
        """
        zeit_jetzt = datetime.datetime.now()
        zeit_jetzt_stamp = int(zeit_jetzt.timestamp())
        flagge_ausfuehren = True

        # SQL query to get current status of the tracker_objekt
        self.tracker_objekt = self.sql_session_erstellt.query(sqlKlasseTracker).first()
        
        # Create new object tracker_objekt if there is none in the database
        if self.tracker_objekt == None:
            self.tracker_objekt=sqlKlasseTracker(
                tracker_id='Tracker_00',
                letzter_job_zeit=str(zeit_jetzt),
                letzter_job_zeit_stamp=zeit_jetzt_stamp,
                summe_n_aktuell_in_zeitraum=arg_anzahl_seiten,
                letzte_nullung_stamp=zeit_jetzt_stamp
                )
        
        # Check if the incoming order suceeds the limit for simultaneously processed orders over
        # all users
        elif self.tracker_objekt != None:
            letzte_nullung_vor_sek = zeit_jetzt_stamp - self.tracker_objekt.letzte_nullung_stamp
            naechste_nullung_in_sek = constants.ZEITRAUM_FUER_RATELIMIT - letzte_nullung_vor_sek

            if letzte_nullung_vor_sek > constants.ZEITRAUM_FUER_RATELIMIT:
                setattr(self.tracker_objekt, 'summe_n_aktuell_in_zeitraum', 0)
                setattr(self.tracker_objekt, 'letzte_nullung_stamp', zeit_jetzt_stamp)
                self._funk_sql_add_und_commit_all([self.tracker_objekt])

            zeit_diff_letzter_job = zeit_jetzt_stamp - self.tracker_objekt.letzter_job_zeit_stamp

            if zeit_diff_letzter_job <= constants.ZEITRAUM_FUER_RATELIMIT:
                kontingent_offen = (constants.N_FUER_RATELIMIT
                                    - self.tracker_objekt.summe_n_aktuell_in_zeitraum)

                if kontingent_offen < arg_anzahl_seiten:
                    flagge_ausfuehren = False

            # If the rate limit is not reached, allow the processing of the order
            if flagge_ausfuehren == True:
                setattr(self.tracker_objekt, 'summe_n_aktuell_in_zeitraum',
                        self.tracker_objekt.summe_n_aktuell_in_zeitraum + arg_anzahl_seiten)
                setattr(self.tracker_objekt, 'letzter_job_zeit', str(zeit_jetzt))
                setattr(self.tracker_objekt, 'letzter_job_zeit_stamp', zeit_jetzt_stamp)

        self._funk_sql_add_und_commit_all([self.tracker_objekt])
        
        # If the rate limit is reached, do not allow the processing of the order and stop script
        # from running
        if flagge_ausfuehren == False:                    
            nachricht_fehler = f'''ACHTUNG!: In den letzten {constants.ZEITRAUM_FUER_RATELIMIT}
                Sekunden wurden (von möglicherweise verschiedenen Personen) bereits zu viele
                Aufträge an diese Web App gesendet. Bitte versuche es in {naechste_nullung_in_sek}
                Sekunden erneut oder verringere die gesuchte Anzeigenanzahl in den Optionen auf
                höchstens {kontingent_offen} Anzeigen!
                [Hier](#hinweis-zum-rate-limiting) findest du einen Hinweis zum Rate Limiting.
                '''

            self.eventmanager.funk_event_eingetreten(
                arg_event_name='Vorzeitig_abgebrochen',
                arg_argumente_von_event={
                                        'arg_art': 'Fehler',
                                        'arg_nachricht': nachricht_fehler
                                        }
                )
            
    
    def _funk_sql_add_und_commit_all(
            self,
            arg_liste_objekte: list
            ):
        """Adds and commits all (changed) objects in list
        arg_liste_objekte to the database.
        
        Keyword arguments:\n
        arg_liste_objekte -- List of (changed) objects to commit
        """
        self.sql_session_erstellt.add_all(arg_liste_objekte)
        self._funk_sql_commit()


    def _funk_sql_commit(self):
        """Executes a controlled commit to the database with rollback
        if failed.
        """
        try:
            self.sql_session_erstellt.commit()
        except IntegrityError as integrity_fehler:
            try:
                self.sql_session_erstellt.rollback()
                helpers.funk_drucken('BESTAETIGUNG!: Rollback nach IntegrityError erfolgreich')                
            except Exception as fehler:
                pass
                helpers.funk_drucken('ACHTUNG!: Fehler bei rollback nach IntegrityError')
                
        except Exception as fehler:
            pass
            fehler_name = str(type(fehler).__name__)
            helpers.funk_drucken(f'BESTAETIGUNG!: Rollback nach {fehler_name} erfolgreich')  
            try:
                self.SQL_Session_erstellt.rollback()
                helpers.funk_drucken(f'ACHTUNG!: Fehler bei rollback nach {fehler_name}')
            except:
                pass


    def _funk_sql_neue_session_erstellen(self):
        """Renews the SQL session in attribute sql_session_erstellt."""
        self._funk_sql_session_schliessen()
        self.sql_session_macher = sessionmaker(bind=self.engine_erstellt)
        self.sql_session_erstellt = self.sql_session_macher()   

    
    def _funk_sql_session_schliessen(self):
        """Closes the SQL session in attribute sql_session_erstellt."""
        try:
            self.sql_session_erstellt.close()
        except Exception as fehler:
            helpers.funk_drucken('ACHTUNG!: Fehler in sqlWorker._funk_sql_session_schliessen')
            helpers.funk_drucken('Exception:', str(type(fehler).__name__))
            helpers.funk_drucken('Fehler:', fehler)


    def _funk_sql_schema_erstellen(self):
        """Creates the SQL database schema."""
        sql_basis.metadata.create_all(self.engine_erstellt)



# %%
###################################################################################################
class ScraperWorker:
    """An instance of this class can perform all scraping related
    actions in the web app.
    
    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        eventmanager -- Instance of Eventmanager to work with\n
        sql_worker -- Instance of sqlWorker to work with\n
        user_interface -- Instance of UserInterface to work with\n
        suchbegriff -- Current search term\n
        anzahl_seiten -- Current number of pages that should be
        scraped\n
        liste_ueberschriften -- Current list of scraped article
        headlines\n
        liste_vorschautexte -- Current list of scraped article preview
        texts\n
        gesammelte_texte -- Dict containing data of attributes
        liste_ueberschriften and liste_vorschautexte\n
        cookies -- Cookies to work with while scraping\n
        html_objekt -- Current HTML to work with\n
        link_naechste_seite -- Link to next news page relative to the
        current one
        
    Public methods:\n
        funk_auftrag_annehmen -- This function receives the scraping
        order from the eventmanager.

    Private methods:\n
        _funk_arbeiten -- Scrapes the news with the help of the other
        private methods.\n
        _funk_html_objekt_erste_seite_bearbeiten -- Updates attribute
        html_objekt to HTML of the first news page for the current
        search term.\n
        _Funk_html_objekt_naechste_Seite_bearbeiten -- Updates attribute
        html_objekt to HTML of the next news page following the current
        one.\n
        _funk_link_naechste_Seite_updaten -- Updates attribute
        link_naechste_seite to URL of the next news page following the
        current one.\n
        _funk_liste_ueberschriften_erweitern -- Appends all article
        headlines from current news page to list in attribute
        liste_ueberschriften.\n
        _funk_liste_vorschautexte_erweitern -- Appends all article
        preview texts from current news page to list in attribute
        liste_vorschautexte.\n
        _funk_html_objekt_erstellen -- Sends a request and returns
        HTML.\n
        _funk_ergebnisse_speichern -- Saves the scraped data in the
        dict in attribute gesammelte_texte.
    """

    def __init__(
            self,
            init_eventmanager: Eventmanager,
            init_sql_worker: sqlWorker,
            init_user_interface: UserInterface,
            ):
        """Inits ScraperWorker.

        Keyword arguments:\n
        init_eventmanager -- Active instance of class Eventmanager\n
        init_sql_worker -- Active instance of class sqlWorker\n
        init_user_interface -- Active instance of class UserInterface
        """
        self.eventmanager = init_eventmanager
        self.sql_worker = init_sql_worker
        self.user_interface = init_user_interface
        self.suchbegriff = ''
        self.anzahl_seiten = constants.ANZAHL_SEITEN
        
        self.liste_ueberschriften = []
        self.liste_vorschautexte = []
        self.gesammelte_texte = {}
        
        self.cookies = streamlit.session_state['Cookies']
        self.html_objekt = None
        self.link_naechste_seite = None


    def funk_auftrag_annehmen(
            self,
            arg_auftrag_suchbegriff: str):
        """This function receives the scraping order from the
        eventmanager.
        
        Keyword arguments:\n
        Arg_Auftrag_Suchbegriff -- Search term of incoming order\n
        """               
        # If the user typed in nothing as search term, stop the script from running
        if arg_auftrag_suchbegriff == '':
            nachricht_fehler = 'ACHTUNG!: Bitte gib einen Suchbegriff ein!'
                
            self.eventmanager.funk_event_eingetreten(
                arg_event_name='Vorzeitig_abgebrochen',
                arg_argumente_von_event={
                                        'arg_art': 'Fehler',
                                        'arg_nachricht': nachricht_fehler
                                        }
                )
        
        # Check whether the rate limit for all users is not reached
        self.sql_worker.funk_sql_tracker_updaten(arg_anzahl_seiten=self.anzahl_seiten)
        
        self.suchbegriff = arg_auftrag_suchbegriff.lstrip().rstrip()
                
        self.liste_ueberschriften = []
        self.liste_vorschautexte = []
        self.gesammelte_texte = {}
        
        with self.user_interface.platzhalter_ausgabe_spinner_02:
            with streamlit.spinner('Deine Daten werden gerade gesammelt.'):
                self._funk_arbeiten()
        
        # Tell the eventmanager that the scraping is done
        self.eventmanager.funk_event_eingetreten(
            arg_event_name='Fertig_geschuerft',
            arg_argumente_von_event={
                'arg_auftrag_suchbegriff': self.suchbegriff,
                'arg_auftrag_liste_ueberschriften': self.liste_ueberschriften,
                'arg_auftrag_liste_vorschautexte': self.liste_vorschautexte
                }
            )
            

    def _funk_arbeiten(self):   
        """Scrapes the news with the help of other private methods after
        the order was received.
        """   
        self._funk_html_objekt_erste_seite_bearbeiten()
        self._funk_liste_ueberschriften_erweitern()
        self._funk_liste_vorschautexte_erweitern()
        
        for i in range(0, self.anzahl_seiten - 1):
            helpers.funk_schlafen(
                constants.SCHLAFEN_SEKUNDEN - 1,
                constants.SCHLAFEN_SEKUNDEN + 1
                )
            self._funk_link_naechste_seite_updaten()
            self._funk_html_objekt_naechste_seite_bearbeiten()
            self._funk_liste_ueberschriften_erweitern()
            self._funk_liste_vorschautexte_erweitern()

        self._funk_ergebnisse_speichern()
  
    
    def _funk_html_objekt_erste_seite_bearbeiten(self):
        """Updates attribute html_objekt to HTML of the first news page
        for the current search term. 
        """
        self.html_objekt = self._funk_html_objekt_erstellen(
            arg_link=None,
            arg_suchbegriff=self.suchbegriff
            )
    
    
    def _funk_html_objekt_naechste_seite_bearbeiten(self):
        """Updates attribute html_objekt to HTML of the next news page
        following the current one.
        """
        self.html_objekt = self._funk_html_objekt_erstellen(
            arg_link=self.link_naechste_seite,
            arg_suchbegriff=None
            )        
    
    
    def _funk_link_naechste_seite_updaten(self):
        """Updates attribute link_naechste_seite to URL of the next
        news page following the current one.
        """
        element_naechste_seite = self.html_objekt.cssselect('a.nBDE1b.G5eFlf')[-1]
        string_naechste_seite = element_naechste_seite.attrib['href']
        self.link_naechste_seite = ''
        
    
    def _funk_liste_ueberschriften_erweitern(self):
        """"Appends all article headlines from current news page to
        list in attribute liste_ueberschriften.
        """
        liste_elemente_ueberschriften = self.html_objekt.\
            cssselect('h3.zBAuLc.l97dzf > div.BNeawe.vvjwJb.AP7Wnd')
        
        for x in liste_elemente_ueberschriften:
            text = x.text_content()
            self.liste_ueberschriften.append(text)
            

    def _funk_liste_vorschautexte_erweitern(self):
        """Appends all article preview texts from current news page to
        list in attribute liste_vorschautexte.
        """
        liste_elemente_vorschautexte = self.html_objekt.\
            cssselect('div.BNeawe.s3v9rd.AP7Wnd > div:nth-child(1)')
        
        for x in liste_elemente_vorschautexte:
            text = x.text_content()            
            self.liste_vorschautexte.append(text)


    def _funk_html_objekt_erstellen(
            self,
            arg_link: str = None,
            arg_suchbegriff: str = None
            ):
        """Sends a request and returns HTML.

        Keyword arguments:\n
        arg_link -- Link for request\n
        arg_suchbegriff -- Search term
        """
        with requests.Session() as sitzung:
            sitzung.headers.update({'Accept-Language': 'de;q=1.0, en;q=0.0, *;q=0.0'})

            # If a link is handed over in argument Arg_Link, use this link for the request
            if arg_link != None:
                link = arg_link
            # Elif a search term is handed over in argument arg_suchbegriff, use this search term
            # for creating a link 
            elif arg_suchbegriff != None:
                link = f''
            
            antwort_server = sitzung.get(
                link,
                cookies=self.cookies
                )

            helpers.funk_drucken('antwort_server:', antwort_server)
            antwort_server_html = antwort_server.content.decode('ISO-8859-1')
            baum_html = html.fromstring(antwort_server_html)
          
            return(baum_html)


    def _funk_ergebnisse_speichern(self):
        """Saves the scraped data in the dict in attribute
        gesammelte_texte.
        """
        self.gesammelte_texte['Ueberschriften'] = self.liste_ueberschriften
        self.gesammelte_texte['Vorschautexte'] = self.liste_vorschautexte
    


# %%
###################################################################################################
class AnalyzerWorker:
    """An instance of this class can perform all analyzing related
    actions in the web app.

    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        eventmanager -- Instance of eventmanager to work with\n
        user_interface -- Instance of UserInterface to work with\n
        suchbegriff -- Current search term\n
        liste_ueberschriften -- Current list of scraped article
        headlines\n
        liste_vorschautexte -- Current list of scraped article preview
        texts\n
        liste_ueberschriften_clean -- Current list with cleaned data
        from article headlines\n
        liste_vorschautexte_clean -- Current list with cleaned data
        from article preview texts\n
        liste_gesamter_text_clean -- Current list with cleaned data
        from attributes liste_ueberschriften_clean and
        liste_vorschautexte_clean\n
        buch_fuer_wordcloud -- Dict with word for wordcloud as keys and
        the ir frequency over all texts as values \n
        wordcloud_objekt -- Wordcloud object\n
        wordcloud_objekt_array -- Wordcloud as array\n
        mittelwert_sentiment -- Current value for coloring of the word
        cloud, relevant for private method _funk_wordcloud_zeigen\n
        liste_fuer_wordcloud -- Current list with data for wordcloud
        object to create\n
        liste_fuer_sentiment -- Current list with data for mean
        sentiment calculation\n        
        modell_sentiment -- Model for sentiment analysis\n
        tagger -- Tagger for sentiment analysis
        
    Public methods:\n
        funk_auftrag_annehmen -- This function receives the analyzing
        order from the eventmanager.

    Private methods:\n
        _funk_modell_sentiment_erstellen -- Returns model for sentiment
        analysis.\n
        _funk_tagger_erstellen -- Returns tagger for sentiment
        analysis.\n
        _funk_arbeiten -- Analyzes the texts with the help of the other
        private methods.\n
        _funk_texte_verarbeiten -- Processes the texts in attributes
        liste_ueberschriften und liste_vorschautexte.\n
        _funk_sentiment_analysieren -- Analyzes the sentiment and store
        results in attribute buch_fuer_wordcloud.\n
        _funk_wordcloud_erstellen -- Creates wordcloud object in
        attribute wordcloud_objekt from data in attribute
        buch_fuer_wordcloud.\n
        _funk_wordcloud_konvertieren -- Converts attribute
        wordcloud_objekt to wordcloud array object and stores it in
        attribute wordcloud_objekt_array.\n
        _funk_wordcloud_faerben -- Calculates the color of the word
        cloud and returns it as HSL color string.
        """
    
    def __init__(
            self,
            init_eventmanager: Eventmanager,
            init_user_interface: UserInterface
            ):
        """Inits AnalyzerWorker.

        Keyword arguments:\n
        init_eventmanager -- Active instance of class Eventmanager\n
        init_user_interface -- Active instance of class UserInterface
        """
        self.eventmanager = init_eventmanager
        self.user_interface = init_user_interface

        self.suchbegriff = ''   
        self.liste_ueberschriften = None
        self.liste_vorschautexte = None

        self.liste_ueberschriften_clean = None
        self.liste_vorschautexte_clean = None
        self.liste_gesamter_text_clean = None
        self.buch_fuer_wordcloud = None
        self.wordcloud_objekt = None
        self.wordcloud_objekt_array = None
        self.mittelwert_sentiment = None
        
        self.liste_fuer_wordcloud = []
        self.liste_fuer_sentiment = []

        self.modell_sentiment = AnalyzerWorker._funk_modell_sentiment_erstellen()
        self.tagger = AnalyzerWorker._funk_tagger_erstellen()
    

    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _funk_modell_sentiment_erstellen():
        """Returns model for sentiment analysis."""
        modell_sentiment = SentimentModel() 
        return(modell_sentiment)
    

    @staticmethod
    @streamlit.cache_resource(ttl=3600, show_spinner=False)
    def _funk_tagger_erstellen():
        """Returns tagger for sentiment analysis."""
        tagger = HanoverTagger.HanoverTagger('morphmodel_ger.pgz') 
        return(tagger)


    def funk_auftrag_annehmen(
            self,
            arg_auftrag_suchbegriff: str,
            arg_auftrag_liste_ueberschriften: list,
            arg_auftrag_liste_vorschautexte: list
            ):
        """This function receives the analyzing order from the
        eventmanager.
        
        Keyword arguments:\n
        arg_auftrag_suchbegriff -- Search term of incoming order\n
        arg_auftrag_liste_ueberschriften -- List of scraped article
        headlines of incoming order\n
        arg_auftrag_liste_vorschautexte -- List of scraped article
        preview texts of incoming order
        """ 
        self.suchbegriff = arg_auftrag_suchbegriff
        self.liste_ueberschriften = arg_auftrag_liste_ueberschriften
        self.liste_vorschautexte = arg_auftrag_liste_vorschautexte

        self.mittelwert_sentiment = None
        self.liste_fuer_wordcloud = []
        self.liste_fuer_sentiment = []
        
        with self.user_interface.platzhalter_ausgabe_spinner_02:
            with streamlit.spinner('Deine Daten werden gerade analysiert.'):
                self._funk_arbeiten()
        
        self.eventmanager.funk_event_eingetreten(
            arg_event_name='Fertig_analysiert',
            arg_argumente_von_event={
                                    'arg_art': 'Erfolg',
                                    'arg_nachricht': 'NEUER AUFTRAG FERTIG BEARBEITET!'
                                    }
            )

    
    def _funk_arbeiten(self):
        """Analyzes the texts with the help of the other private
        methods.
        """
        self._funk_texte_verarbeiten()
        self._funk_wordcloud_erstellen()
        self._funk_wordcloud_konvertieren()
        self._funk_ergebnisse_speichern()
        

    def _funk_texte_verarbeiten(self):
        """Processes the texts in attributes liste_ueberschriften und
        liste_vorschautexte.
        """
        self.liste_ueberschriften_clean = []
        for x in self.liste_ueberschriften:
            if import_funk_detektieren(x) == 'de':
                self.liste_ueberschriften_clean.append(x) 
        
        self.liste_vorschautexte_clean = []
        for x in self.liste_vorschautexte:
            index = (x.find('vor', len(x)-20))
            clean_x = x[:index]
            if import_funk_detektieren(clean_x) == 'de':
                self.liste_vorschautexte_clean.append(clean_x)
        
        self.liste_gesamter_text_clean = self.liste_ueberschriften_clean\
                                            + self.liste_vorschautexte_clean

        if len(self.liste_gesamter_text_clean) < 1:
            nachricht_fehler = f'''ACHTUNG!: Die gesammelte Textmenge ist zu gering.
                Wahrscheinlich waren zu viele Suchergebnisse nicht in deutscher Sprache. Bitte
                versuche es mit einem anderen Suchbegriff erneut!'''
                
            self.eventmanager.funk_event_eingetreten(
                arg_event_name='Vorzeitig_abgebrochen',
                arg_argumente_von_event={
                                        'arg_art': 'Fehler',
                                        'arg_nachricht': nachricht_fehler
                                        }
                )

        self._funk_sentiment_analysieren(arg_liste=self.liste_ueberschriften_clean)
        self._funk_sentiment_analysieren(arg_liste=self.liste_vorschautexte_clean)
    
            
    def _funk_sentiment_analysieren(
            self,
            arg_liste: list
            ):
        """Analyzes the sentiment and stores the results in attribute
        buch_fuer_wordcloud.

        Keyword arguments:\n
        arg_liste -- List with texts to be analyzed
        """
        # Analyze the sentiment for each text in the argument arg_liste
        for i, x in enumerate(arg_liste.copy()):
            klassifizierung_x, wahrscheinlichkeiten_x = self.modell_sentiment.\
                predict_sentiment([x],
                output_probabilities = True)

            # Weight and label sentiment of analyzed text
            if klassifizierung_x[0] == 'neutral':
                sentiment = 0
                sentiment_beschreibung = 'neutral'
            elif klassifizierung_x[0] == 'positive':
                sentiment = 1
                sentiment_beschreibung = 'positiv'
            elif klassifizierung_x[0] == 'negative':
                sentiment = -1
                sentiment_beschreibung = 'negativ'

            self.liste_fuer_sentiment.append(sentiment)

            arg_liste[i] = [x, f' ### Sentiment: {sentiment_beschreibung}']
            
            x_ohne_bindestriche = x.replace('-', ' ')
    
            liste_tokens = nltk.tokenize.word_tokenize(x_ohne_bindestriche, language='german')

            for wort_x in liste_tokens:
                tuple_tag = self.tagger.analyze(wort_x)

                # Only use verbs and nouns for the wordcloud
                if True in (y in tuple_tag[1] for y in ['VV']) or tuple_tag[1][0] == 'N':
                    self.liste_fuer_wordcloud.append(tuple_tag[0])
            
            self.mittelwert_sentiment = float(mean(self.liste_fuer_sentiment))
            
            # Count how often each word occured
            self.buch_fuer_wordcloud = Counter(self.liste_fuer_wordcloud)

            for key_x in self.buch_fuer_wordcloud.copy().keys():
                wert_x = self.buch_fuer_wordcloud[key_x]

                if wert_x < 4:
                    del(self.buch_fuer_wordcloud[key_x])


    def _funk_wordcloud_erstellen(self):
        """Creates wordcloud object in attribute wordcloud_objekt from
        data in attribute buch_fuer_wordcloud.
        """
        self.wordcloud_objekt = WordCloud(
            width=1280,
            height=720
            ).generate_from_frequencies(self.buch_fuer_wordcloud)
        

    def _funk_wordcloud_konvertieren(self):
        """Converts attribute wordcloud_objekt to wordcloud array
        object and stores it in attribute wordcloud_objekt_array.
        """
        self.wordcloud_objekt.recolor(
            color_func=AnalyzerWorker._funk_wordcloud_faerben,
            random_state=self.mittelwert_sentiment
            )
        
        self.wordcloud_objekt_array = self.wordcloud_objekt.to_array()


    def _funk_ergebnisse_speichern(self):
        streamlit.session_state['Arrays_fuer_Clouds'][self.suchbegriff] = {
            'Array': self.wordcloud_objekt_array,
            'Rohdaten_Ueberschriften': self.liste_ueberschriften,
            'Rohdaten_Vorschautexte': self.liste_vorschautexte,
            'Verarbeitete_Ueberschriften': self.liste_ueberschriften_clean,
            'Verarbeitete_Vorschautexte': self.liste_vorschautexte_clean
            }
        
    
    @staticmethod
    def _funk_wordcloud_faerben(
            font_size,
            position,
            orientation,
            random_state: float,
            **kwargs
            ):
        """Calculates the color of the wordcloud and returns it as
        HSL color string.
        """
        if random_state == None:
            return('hsl(0, 100%, 100%)')
        
        elif random_state != None:
            wert_hsl = 60 + random_state*3*60

            if wert_hsl < 0:
                wert_hsl = 0
            elif wert_hsl > 120:
                wert_hsl = 120

            return(f'hsl({wert_hsl}, 100%, 50%)')
