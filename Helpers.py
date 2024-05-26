"""This module contains helper functions.

Functions:\n
    Funk_Drucken -- Print with timestamp.\n
    Funk_Drucken_Streamlit -- Print with timestamp in streamlit.\n
    Funk_Schlafen -- Sleep for random seconds between the two boundaries
    given in the arguments.
"""

# %%
###################################################################################################
import streamlit

import datetime
import time
import random


# %%
###################################################################################################
def Funk_Drucken(*ZudruckenderText):
    """Print with timestamp."""
    print('##########', str(datetime.datetime.now()), ':', *ZudruckenderText)


def Funk_Drucken_Streamlit(*ZudruckenderText):
    """Print with timestamp in streamlit."""
    streamlit.write('##########', str(datetime.datetime.now()), ':', *ZudruckenderText)


def Funk_Schlafen(
        Arg_Grenze_unten,
        Arg_Grenze_oben
        ):
    """Sleep for random seconds between the two boundaries given in the
    arguments.
    
    Keyword arguments:\n
        Arg_Grenze_unten -- Lower boundary in seconds\n
        Arg_Grenze_oben: Upper boundary in seconds
    """
    time.sleep(round(random.uniform(Arg_Grenze_unten, Arg_Grenze_oben), 2))
