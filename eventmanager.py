"""This module contains the class Eventmanager.

Classes:\n
    Eventmanager -- An instance of this class manages the interaction
    between events and their effects, i. e. their subscriber functions.
"""

# %%
###################################################################################################

##################################################
# Import modules from folder
import helpers


# %%
###################################################################################################
class Eventmanager:
    """An instance of this class manages the interaction between events
    and their, i. e. their subscriber functions.

    Attributes:\n
        _events_dict -- Dictionary of all added events to manage

    Public methods:\n
        funk_abonnent_hinzufuegen -- Adds subscriber function in
        argument arg_abonnent with parameters in
        argument arg_argumente_vom_abonnieren to dictionary in
        attribute _events_dict.\n
        funk_abonnent_loeschen -- Deletes subscriber function from
        argument arg_abonnent for event in argument arg_event_name.\n
        funk_event_eingetreten -- This function can be called whenever
        it should be signalled that an event has happend.
    """

    def __init__(self):
        """Inits Eventmanager."""
        self._events_dict = {}
    

    def funk_abonnent_hinzufuegen(
            self,
            arg_event_name: str,
            arg_abonnent,
            arg_argumente_vom_abonnieren: dict
            ):
        """Adds subscriber function in argument
        arg_abonnent with parameters in argument
        arg_argumente_vom_abonnieren to dictionary in attribute
        _events_dict.

        Keyword arguments:\n
            arg_event_name -- Name of event\n
            arg_abonnent -- Name of function to be called when event
            has happend\n
            arg_argumente_vom_abonnieren -- Arguments for subscriber
            function to be called. These will get passed to the
            subscriber function along with the arguments passed from the
            specific event (see function funk_event_eingetreten in this
            file).
        """
        eventmanager_keys = self._events_dict.keys()
        
        if arg_event_name not in eventmanager_keys:
            self._events_dict[arg_event_name] = {}
        
        dict_mit_abonnentennamen = self._events_dict[arg_event_name]
        abonnent_name = arg_abonnent.__name__

        # If the function is already a subscriber of the event, add a suffix to the function name.
        # In this way it is possible for a function to subscribe to an event multiple times with
        # different parameters.
        if abonnent_name in dict_mit_abonnentennamen.keys():
            i = 1
            while abonnent_name in dict_mit_abonnentennamen.keys():
                i += 1
                abonnent_name = f'{abonnent_name}_{i}'

        self._events_dict[arg_event_name][abonnent_name] = [
            arg_abonnent,
            arg_argumente_vom_abonnieren
            ]

    
    def funk_abonnent_loeschen(
            self,
            arg_event_name: str,
            arg_abonnent_name
            ):
        """Deletes subscriber function from argument arg_abonnent for
        event in argument arg_event_name.

        Keyword arguments:\n
            arg_event_name -- name of event\n
            arg_abonnent_name -- Name of subscriber function
        """
        del(self._events_dict[arg_event_name][arg_abonnent_name])


    def funk_event_eingetreten(
            self,
            arg_event_name: str,
            arg_argumente_von_event: dict
            ):
        """This function can be called whenever it should be signalled
        that an event has happend.

        Keyword arguments:\n
            arg_event_name -- Name of event\n
            arg_argumente_von_event-- Parameters that should pe passed
            to all subscriber functions for this specific occurence of
            the event
        """
        for key_x, value_x in self._events_dict[arg_event_name].items():
            helpers.funk_drucken(f'Event {arg_event_name} gerade eingetreten.\n'
                                 f'\tDeshalb wird nun Funktion {key_x} durchgefuehrt.'
                                 )
            
            # Merge arguments which are passed where the event happened and those which are already
            # in the eventmanager (see function funk_abonnent_hinzufuegen in this file). Arguments
            # with the same name from the eventmanager have priority, i. e. they overwrite the ones
            # passed from the specific event which has happened.
            buch_merged = {**arg_argumente_von_event, **value_x[1]}

            # Call the subscriber function with the merged arguments
            value_x[0](**buch_merged)
