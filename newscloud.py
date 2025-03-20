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
    
    from langdetect import DetectorFactory as import_detektions_fabrik
    import_detektions_fabrik.seed = 0

    ##################################################
    # Import modules from folder
    import helpers
    import constants
    from sql_schema import sql_basis
    from sql_schema import sqlKlasseTracker
    from workers import sqlWorker
    from workers import ScraperWorker
    from workers import AnalyzerWorker
    from eventmanager import Eventmanager
    from user_interface import UserInterface


# %%
###################################################################################################
# Create eventmanager object which organizes most of the communication between the user_interface,
# scraper_worker and analyzer_worker object
eventmanager = Eventmanager()

# Create objects for each distinct task (i. e. displaying UI, scraping, analyzing).
user_interface = UserInterface(init_eventmanager=eventmanager)
user_interface.funk_einrichten()

with user_interface.platzhalter_ausgabe_spinner_01:
    with streamlit.spinner('Bitte warte, bis ich verschwunden bin, bevor du weitermachst!'):
        sql_worker = sqlWorker(
            init_eventmanager=eventmanager,
            init_user_interface=user_interface
            )

        scraper_worker = ScraperWorker(
            init_eventmanager=eventmanager,
            init_sql_worker=sql_worker,
            init_user_interface=user_interface
            )

        analyzer_worker = AnalyzerWorker(
            init_eventmanager=eventmanager,
            init_user_interface=user_interface
            )

        # Add different events and subscriber functions to the eventmanager object 
        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Button_gedrueckt',
            arg_abonnent=scraper_worker.funk_auftrag_annehmen,
            arg_argumente_vom_abonnieren={}
            )

        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Fertig_geschuerft',
            arg_abonnent=analyzer_worker.funk_auftrag_annehmen,
            arg_argumente_vom_abonnieren={}
            )

        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Fertig_analysiert',
            arg_abonnent=user_interface.funk_feedback_ausgeben,
            arg_argumente_vom_abonnieren={}
            )
        
        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Fertig_analysiert',
            arg_abonnent=user_interface.funk_ergebnisse_ausgeben,
            arg_argumente_vom_abonnieren={}
            )
        
        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Vorzeitig_abgebrochen',
            arg_abonnent=user_interface.funk_feedback_ausgeben,
            arg_argumente_vom_abonnieren={}
            )

        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Vorzeitig_abgebrochen',
            arg_abonnent=user_interface.funk_ergebnisse_ausgeben,
            arg_argumente_vom_abonnieren={}
            )
        
        eventmanager.funk_abonnent_hinzufuegen(
            arg_event_name='Vorzeitig_abgebrochen',
            arg_abonnent=user_interface.funk_aufraeumen,
            arg_argumente_vom_abonnieren={}
            )
        
        # Check whether there are open jobs
        user_interface.funk_jobs_pruefen()

        # Clean up
        user_interface.funk_aufraeumen()

gc.collect()

# %%
# Stop script from running
streamlit.stop()
