"""This module contains helper functions.

Functions:\n
    funk_drucken -- Print with timestamp.\n
    funk_drucken_streamlit -- Print with timestamp in streamlit.\n
    funk_schlafen -- Sleep for random seconds between the two boundaries
    given in the arguments.\n
"""

# %%
###################################################################################################
import streamlit

import datetime
import time
import random


# %%
###################################################################################################
def funk_drucken(*arg_zu_druckender_text):
    """Print with timestamp."""
    print('##########', str(datetime.datetime.now()), ':', *arg_zu_druckender_text)


def funk_drucken_streamlit(*arg_zu_druckender_text):
    """Print with timestamp in streamlit."""
    streamlit.write('##########', str(datetime.datetime.now()), ':', *arg_zu_druckender_text)


def funk_schlafen(
        arg_grenze_unten,
        arg_grenze_oben
        ):
    """Sleep for random seconds between the two boundaries given in the
    arguments.
    
    Keyword arguments:\n
        arg_grenze_unten -- Lower boundary in seconds\n
        arg_grenze_oben: Upper boundary in seconds
    """
    time.sleep(round(random.uniform(arg_grenze_unten, arg_grenze_oben), 2))
