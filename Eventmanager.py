"""This module contains the class Eventmanager.

Classes:\n
    Eventmanager -- An instance of this class manages the interaction
    between events and their effects, i. e. their subscriber functions.
"""

# %%
###################################################################################################

##################################################
# Import modules from folder
import Helpers


# %%
###################################################################################################
class Eventmanager:
    """An instance of this class manages the interaction between events
    and their, i. e. their subscriber functions.

    Attributes:\n
        _Events_Dict -- Dictionary of all added events to manage

    Public methods:\n
        Funk_Abonnent_hinzufuegen -- Adds subscriber function in
        argument Arg_Abonnent with parameters in
        argument Arg_Argumente_vom_Abonnieren to dictionary in
        attribute _Events_Dict.\n
        Funk_Abonnent_loeschen -- Deletes subscriber function from
        argument Arg_Abonnent for event in argument Arg_Event_Name.\n
        Funk_Event_eingetreten -- This function can be called whenever
        it should be signalled that an event has happend.
    """

    def __init__(self):
        """Inits Eventmanager."""
        self._Events_Dict = {}
    

    def Funk_Abonnent_hinzufuegen(
            self,
            Arg_Event_Name: str,
            Arg_Abonnent,
            Arg_Argumente_vom_Abonnieren: dict
            ):
        """Adds subscriber function in argument
        Arg_Abonnent with parameters in argument
        Arg_Argumente_vom_Abonnieren to dictionary in attribute
        _Events_Dict.

        Keyword arguments:\n
            Arg_Event_Name -- Name of event\n
            Arg_Abonnent -- Name of function to be called when event
            has happend\n
            Arg_Argumente_vom_Abonnieren -- Arguments for subscriber
            function to be called. These will get passed to the
            subscriber function along with the arguments passed from the
            specific event (see function Funk_Event_eingetreten in this
            file).
        """
        Eventmanager_keys = self._Events_Dict.keys()
        
        if Arg_Event_Name not in Eventmanager_keys:
            self._Events_Dict[Arg_Event_Name] = {}
        
        Dict_mit_Abonenntennamen = self._Events_Dict[Arg_Event_Name]
        Abonnent_Name = Arg_Abonnent.__name__

        # If the function is already a subscriber of the event, add a suffix to the function name.
        # In this way it is possible for a function to subscribe to an event multiple times with
        # different parameters.
        if Abonnent_Name in Dict_mit_Abonenntennamen.keys():
            i = 1
            while Abonnent_Name in Dict_mit_Abonenntennamen.keys():
                i += 1
                Abonnent_Name = f'{Abonnent_Name}_{i}'

        self._Events_Dict[Arg_Event_Name][Abonnent_Name] = [
            Arg_Abonnent,
            Arg_Argumente_vom_Abonnieren
            ]

    
    def Funk_Abonnent_loeschen(
            self,
            Arg_Event_Name: str,
            Arg_Abonnent_Name
            ):
        """Deletes subscriber function from argument Arg_Abonnent for
        event in argument Arg_Event_Name.

        Keyword arguments:\n
            Arg_Event_Name -- Name of event\n
            Arg_Abonnent_Name -- Name of subscriber function
        """
        del(self._Events_Dict[Arg_Event_Name][Arg_Abonnent_Name])


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
            to all subscriber functions for this specific occurence of
            the event
        """
        for Key_x, Value_x in self._Events_Dict[Arg_Event_Name].items():
            Helpers.Funk_Drucken(f'Event {Arg_Event_Name} gerade eingetreten.\n'
                                 f'\tDeshalb wird nun Funktion {Key_x} durchgefuehrt.'
                                 )
            
            # Merge arguments which are passed where the event happened and those which are already
            # in the Eventmanager (see function Funk_Abonennet_hinzufuegen in this file). Arguments
            # with the same name from the Eventmanager have priority, i. e. they overwrite the ones
            # passed from the specific event which has happened.
            Buch_merged = {**Arg_Argumente_von_Event, **Value_x[1]}

            # Call the subscriber function with the merged arguments
            Value_x[0](**Buch_merged)
