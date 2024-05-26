"""This file is the main script for the Newscloud web app. It runs 
from top to bottom every time the user presses the button.
"""

# %%
###################################################################################################
import streamlit
streamlit.set_page_config(page_title='Newscloud', layout='wide', page_icon='💭')


###################################################################################################
with streamlit.spinner('''Bitte warte einen Moment, bis der Server aufgewacht ist. Dieser ist bei
    längerer Zeit ohne Nutzung der Web App im Stand-by.'''
    ):
    
    import gc
    gc.enable()
    
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
# Create Eventmanager object which organizes most of the communication between the User_Interface,
# Scraper_Worker and Analyzer_worker object
Eventmanager_A = Eventmanager()

# Create objects for each distinct task (i. e. displaying UI, scraping, analyzing).
User_Interface_A = User_Interface(Init_Eventmanager=Eventmanager_A)
User_Interface_A.Funk_Einrichten()

with User_Interface_A.Platzhalter_Ausgabe_Spinner_01:
    with streamlit.spinner('Bitte warte, bis ich verschwunden bin, bevor du weitermachst!'):
        SQL_Worker_A = SQL_Worker(
            Init_Eventmanager=Eventmanager_A,
            Init_UI=User_Interface_A
            )

        Scraper_A = Scraper_Worker(
            Init_Eventmanager=Eventmanager_A,
            Init_SQL_Worker=SQL_Worker_A,
            Init_UI=User_Interface_A
            )

        Analyzer_A = Analyzer_Worker(
            Init_Eventmanager=Eventmanager_A,
            Init_UI=User_Interface_A
            )

        # Add different events and subscriber functions to the Eventmanager object 
        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Button_gedrueckt',
            Arg_Abonnent=Scraper_A.Funk_Auftrag_annehmen,
            Arg_Argumente_vom_Abonnieren={}
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_geschuerft',
            Arg_Abonnent=Analyzer_A.Funk_Auftrag_annehmen,
            Arg_Argumente_vom_Abonnieren={}
            )
        
        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_analysiert',
            Arg_Abonnent=User_Interface_A.Funk_Feedback_ausgeben,
            Arg_Argumente_vom_Abonnieren={}
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Fertig_analysiert',
            Arg_Abonnent=User_Interface_A.Funk_Ergebnisse_ausgeben,
            Arg_Argumente_vom_Abonnieren={}
            )
        
        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Vorzeitig_abgebrochen',
            Arg_Abonnent=User_Interface_A.Funk_Feedback_ausgeben,
            Arg_Argumente_vom_Abonnieren={}
            )

        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Vorzeitig_abgebrochen',
            Arg_Abonnent=User_Interface_A.Funk_Ergebnisse_ausgeben,
            Arg_Argumente_vom_Abonnieren={}
            )
        
        Eventmanager_A.Funk_Abonnent_hinzufuegen(
            Arg_Event_Name='Vorzeitig_abgebrochen',
            Arg_Abonnent=User_Interface_A.Funk_Aufraeumen,
            Arg_Argumente_vom_Abonnieren={}
            )
        
        # Check whether there are open jobs
        User_Interface_A.Funk_Jobs_pruefen()

        # Clean up
        User_Interface_A.Funk_Aufraeumen()

gc.collect()

# %%
# Stop script from running
streamlit.stop()
