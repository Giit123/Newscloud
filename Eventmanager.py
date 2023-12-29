"""This module contains the class Eventmanager.

Classes:\n
    Eventmanager -- An instance of this class manages the interaction
    between events and their effects.
"""

# %%
###################################################################################################
import datetime

##################################################
# Import modules from folder
import Helpers

# %%
###################################################################################################
class Eventmanager:
    """An instance of this class manages the interaction between events
    and their effects.

    Attributes:\
        _Events_Dict -- Dictionary of all added events to manage

    Public methods:
        Funk_Abonnent_hinzufuegen -- Adds subscriber function in
        argument Arg_aufzurufende_Funktion with parameters in argument
        Arg_Argumente to dictionary in attribute _Events_Dict.\n
        Funk_Abonnent_loeschen -- Deletes subscriber function from
        argument Arg_aufzurufende_Funktion for event in argument
        Arg_Event_Name.\n
        Funk_Event_eingetreten -- This function can be called whenever
        it should be signalled that an event has happend.
    """

    def __init__(self):
        """Inits Eventmanager."""
        self._Events_Dict = {}
    

    def Funk_Abonnent_hinzufuegen(
            self,
            Arg_Event_Name: str,
            Arg_aufzurufende_Funktion,
            Arg_Argumente: dict
            ):
        """Adds subscriber function in argument
        Arg_aufzurufende_Funktion with parameters in argument
        Arg_Argumente to dictionary in attribute _Events_Dict.

        Keyword arguments:\n
            Arg_Event_Name -- Name of event\n
            Arg_aufzurufende_Funktion -- Name of function to be called
            when event has happend\n
            Arg_Argumente -- Parameters of function to be called
        """
        Eventmanager_keys = self._Events_Dict.keys()
        
        if Arg_Event_Name not in Eventmanager_keys:
            self._Events_Dict[Arg_Event_Name] = {}
                
        Dict_mit_Abonenntennamen = self._Events_Dict[Arg_Event_Name]
        Aufzurufende_Funktion_Name = Arg_aufzurufende_Funktion.__name__

        # If the function is already a subscriber of the event, add a suffix to the function name.
        # In this way it is possible for a function to subscribe to an event multiple times with
        # different parameters.
        if Aufzurufende_Funktion_Name in Dict_mit_Abonenntennamen.keys():
            i = 1
            while Aufzurufende_Funktion_Name in Dict_mit_Abonenntennamen.keys():
                i += 1
                Aufzurufende_Funktion_Name = f'{Aufzurufende_Funktion_Name}_{i}'
        
        self._Events_Dict[Arg_Event_Name][Aufzurufende_Funktion_Name] = [
            Arg_aufzurufende_Funktion,
            Arg_Argumente
            ]


    def Funk_Abonnent_loeschen(
            self,
            Arg_Event_Name: str,
            Arg_aufzurufende_Funktion_Name
            ):
        """Deletes subscriber function from argument
        Arg_aufzurufende_Funktion for event in argument Arg_Event_Name.

        Keyword arguments:\n
            Arg_Event_Name -- Name of event\n
            Arg_aufzurufende_Funktion_Name -- Name of function 
        """
        del(self._Events_Dict[Arg_Event_Name][Arg_aufzurufende_Funktion_Name])


    def Funk_Event_eingetreten(
            self,
            Arg_Event_Name: str,
            Arg_Argumente_von_Event: dict
            ):
        """This function can be called whenever it should be signalled
        that an event has happend.

        Keyword arguments:\n
            Arg_Event_Name -- Name of event\n
            Arg_Argumente_von_Event-- Parameters that should pe passed
            to all subscriber functions
        """
        for key_x, value_x in self._Events_Dict[Arg_Event_Name].items():
            Helpers.Funk_Drucken(f'Event {Arg_Event_Name} gerade eingetreten.\
                                 \n\tDeshalb wird nun Funktion {key_x} durchgefuehrt.')
            
            # Merge arguments which are passed where the event happened and those which are
            # already in the Eventmanager. Arguments with the same name from the Eventmanager have
            # priority, i. e. they overwrite the ones passed from where the event happened.
            Buch_merged = {**Arg_Argumente_von_Event, **value_x[1]}

            # Call the subscriber function with the merged arguments
            value_x[0](**Buch_merged)
