"""This module contains the class User_Interface.

Classes:\n
    User_Interface -- An instance of this class can handle all UI
    related actions in the web app.
"""

# %%
###################################################################################################
import streamlit
import streamlit.components.v1 as Komponenten

import datetime
import time
import random
import pickle

##################################################
# Import modules from folder
import Constants
from Eventmanager import Eventmanager


# %%
###################################################################################################
class User_Interface:
    """An instance of this class can handle all UI related actions in
    the web app.

    Attributes:\n
        _Eventmanager -- Instance of Eventmanager to work with\n
        Spalte_A, Spalte_B -- Invisible columns in which elements can
        be inserted\n
        Expander_Optionen -- Equippable expander element on the left
        side of the UI for options\n
        Expander_Ausgabe -- Equippable expander element on the upper
        side of the UI for the results of the user's orders\n
        Expander_Anleitung -- Equippable expander element on the lower
        side of the UI for the manual\n
        Platzhalter -- All attributes which have "Platzhalter" in their
        name are streamlit objects which can be equipped with objects
        that should be displayed to the user.
        
    Public methods:\n
        Funk_Einrichten -- Sets up user interface.\n
        Funk_Expander_Optionen_bestuecken -- Sets up user interfasce
        element in attribute Platzhalter_Optionen_01.\n
        Funk_Platzhalter_bestuecken --Inserts the object in argument
        Arg_Objekt_zum_Einfuegen into page element Arg_Platzhalter.\n
        Funk_Platzhalter_Tabs_bestuecken -- Creates all result tabs
        with one wordcloud each based on saved data from session
        state.\n
        Funk_Jobs_pruefen -- Checks whether there are open jobs, i. e.
        the button was pressed by the user.\n
        Funk_Aufraeumen -- Cleans after the script ran to the end.\n
        Funk_Scroll_into_view -- Scrolls page element in argument Arg_Element into view.

    Private methods:\n
        _Funk_Cookies_aus_Datei_laden -- Returns cookies from file.\n
        _Funk_Startseite_einrichten -- Sets up basic user interface
        template.\n
        _Funk_Geruest_erstellen -- Creates elements for basic user
        interface template.\n
        _Funk_on_click_Button -- This function is called when the
        button is pressed by the user.\n
    """

    def __init__(
            self,
            Init_Eventmanager: Eventmanager
            ):
        """Inits User_Interface.

        Keyword arguments:\n
        Init_Eventamanager -- Active instance of class Eventmanager
        """
        self._Eventmanager = Init_Eventmanager


    def Funk_Einrichten(self):
        """Set up user interface."""
        # First loading of the web app by the user
        if 'User_Interface' not in streamlit.session_state:
            self._Funk_Startseite_einrichten()

            # Create variables in streamlit.session_state for storing between runs
            streamlit.session_state['Arrays_fuer_Clouds'] = {}
            streamlit.session_state['Button_gedrueckt'] = False
            streamlit.session_state['Neues_Array_erstellt'] = False
            streamlit.session_state['Cookies'] = User_Interface._Funk_Cookies_aus_Datei_laden()

        elif streamlit.session_state['Button_gedrueckt'] == True:
            self._Funk_Startseite_einrichten()

        else:
            self._Funk_Startseite_einrichten()


    @staticmethod
    def _Funk_Cookies_aus_Datei_laden():
        """Returns cookies from file."""
        with open('Cookies.pickle', 'rb') as Datei:
            Cookies_geladen = pickle.load(Datei)
        return(Cookies_geladen)
    

    def _Funk_Startseite_einrichten(self):
        """Sets up basic user interface template."""
        self._Funk_Geruest_erstellen()
        self.Funk_Expander_Optionen_bestuecken()
        streamlit.session_state['User_Interface'] = 'Startseite'

    
    def _Funk_Geruest_erstellen(self):
        """Creates elements for basic user interface template."""
        self.Spalte_A, self.Spalte_B = streamlit.columns((10, 35))

        with self.Spalte_A:
            self.Expander_Optionen = streamlit.expander('Optionen:', expanded=True)

            with self.Expander_Optionen:
                self.Platzhalter_Optionen_01 = streamlit.empty()

        with self.Spalte_B:
            self.Expander_Ausgabe = streamlit.expander('Ausgabe:', expanded=True)

            with self.Expander_Ausgabe:
                self.Platzhalter_Ausgabe_Spinner_01 = streamlit.empty()
                self.Platzhalter_Ausgabe_Spinner_02 = streamlit.empty()
                self.Platzhalter_Ausgabe_Warnung = streamlit.empty()
                self.Platzhalter_Ausgabe_01 = streamlit.empty()
                self.Platzhalter_Ausgabe_02 = streamlit.empty()
                self.Platzhalter_Ausgabe_Tabs = streamlit.empty()

            self.Expander_Anleitung = streamlit.expander('Anleitung:', expanded=True)

            with self.Expander_Anleitung:
                self.Platzhalter_Anleitung_01 = streamlit.empty()

                streamlit.markdown('### **Willkommen bei Newscloud!**')
                streamlit.write('Mit dieser Web App kannst du zu einem Suchbegriff eine \
                    Wordcloud für deutschsprachige News erstellen. Dazu werden die \
                    Überschriften und Vorschautexte mehrerer Newsartikel gesammelt und \
                    analysiert. Die Gesamtmenge gesammelter **_Elemente_** besteht also \
                    aus Überschriften UND Vorschautexten. Aus dieser Gesamtmenge werden die \
                    Wörter für die Wordcloud extrahiert. **Die Größe der abgebildeten Wörter \
                    in der Wordcloud repräsentiert deren relative Häufigkeit in der Gesamtmenge. \
                    Die Anordnung der Wörter hat aber keine Bedeutung! Das gemittelte Sentiment \
                    (über alle Überschriften und Vorschautexte) wird durch die Farbe der \
                    Wordcloud dargestellt (s. detaillierte Erläuterung unten).**')
                streamlit.write('Jede neue Wordcloud und ihre zugehörigen Daten werden in einem \
                    Tab im Bereich **"Ausgabe:"** (s. oben) dargestellt. Ein erneuter Auftrag \
                    mit dem identischen Suchbegriff überschreibt die Daten im alten Tab. Es \
                    können maximal 3 dieser Tabs geöffnet sein. Der älteste wird gelöscht, falls \
                    diese Grenze überschritten wird. Du kannst auch mit den Pfeiltasten auf der \
                    Tastatur zwischen den Tabs navigieren! Das Neuladen oder Schließen des \
                    _Browsertabs_ löscht alle deine bisherigen Ergebnisse!')
                
                streamlit.markdown('#### **Detaillierte Erläuterung:**')
                streamlit.write('Für deinen Suchbegriff werden die ersten 3 Seiten News einer \
                    bekannten Internetsuchmaschine gesammelt. Diese Rohaten teilen sich auf in \
                    die Überschriften der Artikel und deren Vorschautexte. Nur deutsche Inhalte \
                    werden weiterverarbeitet. Es müssen mindestens 10 Elemente (d. h. deutsche \
                    Überschriften und / oder Vorschautexte) für eine weitere Bearbeitung deines \
                    Auftrags vorliegen. Aus den Vorschautexten wird zudem der \
                    Veröffentlichungszeitpunkt entfernt (z. B. "vor 2 Tagen"). Beachte, dass bei \
                    ungewöhnlichen Suchbegriffen mit seltenen News auch alte oder wenig sinnvolle \
                    Daten ausgewertet werden können. Außerdem kann es sein, dass das \
                    Sprachmodell fälschlicherweise deutsche Texte nicht erkennt und aussortiert. \
                    Die verarbeiteten Daten und auch die Rohdaten erscheinen unter der jeweiligen \
                    Newscloud, sodass du dort nachvollziehen kannst, welche Daten aussortiert \
                    wurden und wie alt die Daten sind.')
                streamlit.write('Das Sentiment wird nun für jede Überschrift und jeden \
                    Vorschautext einzeln mit dem Package bzw. Sprachmodell "german-sentiment-lib" \
                    von Oliver Guhr analysiert. Eine negatives Sentiment wird danach intern mit \
                    dem Wert -1 abgebildet, ein neutrales mit 0 und ein positives mit +1. Aus \
                    diesen Einzelwerten wird ein Mittelwert gebildet. Ein Mittelwert von 0 \
                    äußert sich in einer gelben Wordcloud. Ein Mittelwert von 0 könnte z. B. \
                    dadurch enstehen, dass alle Elemente ein neutrales Sentiment haben oder auch \
                    dadurch, dass die Elemente hälftig ein positives bzw. ein negatives Sentiment \
                    besitzen. Mittwerte unter bzw. über ± 0,33 werden auf ± 0,33 begrenzt. \
                    Mittelwerte über 0 sind sehr selten. Die Farbe deiner Wordcloud wird also nur \
                    sehr selten ein kräftiges Grün sein. Orange oder rot wird dagegen etwas \
                    häufiger auftreten. Zwischen rot und grün gibt es mehere Abstufungen, wie du \
                    sehen wirst.')
                streamlit.write('Das Sprachmodell wird das Sentiment oft anders beurteilen als \
                    du. Das Sentiment spiegelt nicht die Meinung einer konkreten Person wider. \
                    Du kannst das Sentiment für jedes Element unter der Wordcloud finden. \
                    Weiter unten finden sich auch die unverarbeiteten Rohdaten.')
                streamlit.write('Für die Wordcloud werden Bindestriche aus den Rohdaten entfernt \
                    und die Wörter lemmatisiert. In der Wordcloud werden nur Lemmata bzw. Wörter \
                    angezeigt, die Nomen oder Verben sind und mindestens 4 Mal vorkommen. \
                    Beachte, dass es durch die Lemmatisierung manchmal zu fehlerhaft gebildeten \
                    Wörtern kommt (z. B. bei seltenen Wörtern oder Namen).')
                streamlit.write(f'**HINWEIS!:** Die Nutzung der Web App ist so beschränkt, dass \
                    über _alle aktiven Appnutzer/innen summiert_ maximal \
                    {int(Constants.N_FUER_LIMIT / Constants.ANZAHL_SEITEN)} Aufträge pro \
                    {Constants.ZEITRAUM_FUER_LIMIT} Sekunden bearbeitet werden können. \
                    Wenn dieses Kontingent (von einer anderen Person oder dir) bereits \
                    ausgeschöpft wurde, warte bitte ein paar Sekunden und versuche deinen \
                    Auftrag erneut zu senden. Beachte außerdem, dass die Seite, von der die \
                    News stammen, absichtlich etwas langsamer durchsucht wird, um diese nicht \
                    unnötig zu belasten.')
                streamlit.write('**_Du kannst diese Anleitung ausblenden, indem du oben rechts \
                    auf das Zeichen "˄" klickst! Die Anleitung wird sich dann ganz unten in \
                    dieser Web App wiederfinden lassen, falls du nochmal hier reinschauen \
                    möchtest._**')
                                
    
    def Funk_Expander_Optionen_bestuecken(self):
        """Sets up user interfasce element in attribute
        Platzhalter_Optionen_01.
        """
        with self.Platzhalter_Optionen_01: 
            with streamlit.form('Suchparameter'):
                streamlit.markdown('##### **Suchbegriff:**')
                
                self.Input_Suchbegriff = streamlit.text_input('Hier Suchbegriff eingeben!',
                                                              max_chars=50)

                # The code of the if block is only executed in the next run after the user pressed
                # the button
                if streamlit.form_submit_button(
                    'BUTTON: Newscloud erstellen!',
                    on_click=self._Funk_on_click_Button
                    ):
                        pass

    
    def _Funk_on_click_Button(self):
        """This function is called before running the script again when
        the button is pressed by the user.
        """
        # Set session_state['Button_gedrueckt'] = True to tell the Eventamanager in the subsequent
        # run of the main script that there are open jobs
        streamlit.session_state['Button_gedrueckt'] = True
        

    def Funk_Platzhalter_bestuecken(
            self,
            Arg_Platzhalter,
            Arg_Objekt_zum_Einfuegen
            ):
        """Inserts the object in argument Arg_Objekt_zum_Einfuegen into
        page element Arg_Platzhalter.

        Keyword arguments:\n
        Arg_Platzhalter -- Empty streamlit object which will be
        equipped with object in argument Arg_Objekt_zum_Einfuegen\n
        Arg_Objekt_zum_Einfuegen -- Object which will be shown in the
        UI where empty stramlit element from argument Arg_Platzhalter
        was
        """
        if str(type(Arg_Objekt_zum_Einfuegen)) == "<class 'numpy.ndarray'>":
            with Arg_Platzhalter:
                Linke_Spalte, Mittlere_Spalte, Rechte_Spalte = streamlit.columns([1,4,1])
                with Mittlere_Spalte:
                    streamlit.image(
                        Arg_Objekt_zum_Einfuegen,
                        width=None,
                        use_column_width='always',
                        output_format='PNG'
                        )

        elif type(Arg_Objekt_zum_Einfuegen) == str:
            with Arg_Platzhalter:
                streamlit.markdown(Arg_Objekt_zum_Einfuegen, unsafe_allow_html=True)
    
    
    def Funk_Platzhalter_Tabs_bestuecken(
            self,
            **kwargs
            ):
        """Creates all result tabs with one word cloud each based on
        saved data from session_state.
        """
        Liste_Namen_Tabs = []
        Liste_Namen_Tabs_fuer_Farbe = []

        for key_x, value_x in streamlit.session_state['Arrays_fuer_Clouds'].items():
            Liste_Namen_Tabs.append(key_x)

        Liste_Namen_Tabs.reverse()
        
        for x in Liste_Namen_Tabs:
            Liste_Namen_Tabs_fuer_Farbe.append(f':blue[{x}]')

        with self.Platzhalter_Ausgabe_Tabs:
            self.Liste_Tabs = streamlit.tabs(Liste_Namen_Tabs_fuer_Farbe)

            # Create word cloud for each saved array from previous order and the current one
            for i, x in enumerate(Liste_Namen_Tabs):
                Buch_fuer_Tab = streamlit.session_state['Arrays_fuer_Clouds'][x]
                
                Array = Buch_fuer_Tab['Array']
                with self.Liste_Tabs[i]:
                    Linke_Spalte, Mittlere_Spalte, Rechte_Spalte = streamlit.columns([1,4,1])
                    with Mittlere_Spalte:
                        streamlit.image(
                            Array,
                            width=None,
                            use_column_width='always',
                            output_format='PNG'
                            )

                    time.sleep(0.1)
                                        
                    streamlit.markdown('#### **Verarbeitete Überschriften:**')  
                    streamlit.write(Buch_fuer_Tab['Verarbeitete_Ueberschriften'])
                    streamlit.markdown('#### **Verarbeitete Vorschautexte:**')  
                    streamlit.write(Buch_fuer_Tab['Verarbeitete_Vorschautexte'])
                    streamlit.markdown('#### **Rohdaten Überschriften:**')  
                    streamlit.write(Buch_fuer_Tab['Rohdaten_Ueberschriften'])
                    streamlit.markdown('#### **Rohdaten Vorschautexte:**')  
                    streamlit.write(Buch_fuer_Tab['Rohdaten_Vorschautexte'])

    
    def Funk_Jobs_pruefen(self):
        """Checks whether there are open jobs, i. e. the button was
        pressed by the user.
        """    
        if streamlit.session_state['Button_gedrueckt'] == True:
            # Tell the Eventmanager that the button was pressed by the user
            self._Eventmanager.Funk_Event_eingetreten(
                Arg_Event_Name = 'Button_gedrueckt',
                Arg_Argumente_von_Event = {
                    'Arg_Auftrag_Suchbegriff': self.Input_Suchbegriff
                    }
                )
            

    def Funk_Aufraeumen(self):
        """Cleans up before stopping the script."""
        self.Platzhalter_Ausgabe_Spinner_02.empty()
        
        streamlit.session_state['User_Interface'] = 'Aufgeraeumt'
        streamlit.session_state['Button_gedrueckt'] = False

        self.Platzhalter_Ausgabe_Spinner_01.empty()
        
        if streamlit.session_state['Neues_Array_erstellt'] == True:
            User_Interface.Funk_Scroll_into_view(
                Arg_Element='div.st-emotion-cache-1bt9eao',
                Arg_pixel_x=0,
                Arg_pixel_y=0
                )

        streamlit.session_state['Neues_Array_erstellt'] = False

        streamlit.stop()
    

    @staticmethod
    def Funk_Scroll_into_view(
            Arg_Element,
            Arg_pixel_x,
            Arg_pixel_y
            ):
        """Scroll page element in argument Arg_Element into view."""
        Zahl = datetime.datetime.now().timestamp()
        Komponenten.html(
            f"""
                <p>{Zahl}</p>
                <script>
                    window.parent.document.querySelector('{Arg_Element}').scrollIntoView();
                </script>
            """,
            height=0
        )
