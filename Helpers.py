"""This module contains helper functions.

Functions:\n
    Funk_Drucken -- Print with timestamp.\n
    Funk_Drucken_Streamlit -- Print with timestamp in streamlit.\n
    Funk_Schlafen -- Sleep for Arg_Sekunden seconds.
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
    print(str(datetime.datetime.now()), ': ', *ZudruckenderText)


def Funk_Drucken_Streamlit(*ZudruckenderText):
    """Print with timestamp in streamlit."""
    streamlit.write(str(datetime.datetime.now()), ': ', *ZudruckenderText)


def Funk_Schlafen(Arg_Sekunden: int):
    """Sleep for Arg_Sekunden seconds.
    
    Keyword arguments:
        Arg_Sekunden: Seconds to sleep
    """
    time.sleep(random.randint(Arg_Sekunden - 2, Arg_Sekunden + 2))
