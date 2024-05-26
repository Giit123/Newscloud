"""This module contains the class User_Interface.

Classes:\n
    User_Interface -- An instance of this class can perform all UI
    related actions in the web app.
"""

# %%
###################################################################################################
import streamlit
import streamlit.components.v1 as Komponenten

import datetime
import time
import pickle

##################################################
# Import modules from folder
import Constants
from Eventmanager import Eventmanager


# %%
###################################################################################################
class User_Interface:
    """An instance of this class can perform all UI related actions in
    the web app.

    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        Eventmanager -- Instance of Eventmanager to work with\n
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
        that should be displayed to the user\n
        Input_Suchbegriff -- Search term currenty typed in by the user
        in the UI\n
        Liste_Tabs -- List with tabs, each for one of the last three
        successfully processed orders sent by the user
    
    Public methods:\n
        Funk_Einrichten -- Sets up user interface.\n
        Funk_Feedback_ausgeben -- Prints feedback in the UI in attribute
        Platzhalter_Ausgabe_Feedback.\n
        Funk_Ergebnisse_ausgeben -- Creates all result tabs with one
        word cloud each based on saved data from session_state.\n
        Funk_Jobs_pruefen -- Checks whether there are open jobs, i. e.
        the button was pressed by the user.\n
        Funk_Aufraeumen -- Cleans up and stops stopping the script from
        running.

    Private methods:\n
        _Funk_Cookies_aus_Datei_laden -- Returns cookies from file.\n
        _Funk_Startseite_einrichten -- Sets up basic user interface
        template.\n
        _Funk_Geruest_erstellen -- Creates elements for basic user
        interface template.\n
        _Funk_Expander_Optionen_bestuecken -- Sets up options in
        attribute Platzhalter_Optionen_01 which can be used by the
        user.\n
        _Funk_on_click_Button -- This function is called when the
        button is pressed by the user.\n
        _Funk_Scrollen -- Scrolls page element in argument
        Arg_Element into view.
    """

    def __init__(
            self,
            Init_Eventmanager: Eventmanager
            ):
        """Inits User_Interface.

        Keyword arguments:\n
        Init_Eventamanager -- Active instance of class Eventmanager
        """
        self.Eventmanager = Init_Eventmanager

        self.Spalte_A = None
        self.Spalte_B = None
        self.Expander_Optionen = None
        self.Platzhalter_Optionen_01 = None
        self.Expander_Ausgabe = None
        self.Platzhalter_Ausgabe_Spinner_01 = None
        self.Platzhalter_Ausgabe_Spinner_02 = None
        self.Platzhalter_Ausgabe_Feedback = None
        self.Platzhalter_Ausgabe_Ergebnisse = None
        self.Expander_Anleitung = None
        self.Platzhalter_Anleitung_01 = None
        self.Input_Suchbegriff = None
        self.Liste_Tabs = None


    def Funk_Einrichten(self):
        """Sets up user interface."""
        # First loading of the web app by the user
        if 'User_Interface_eingerichtet' not in streamlit.session_state:
            self._Funk_Startseite_einrichten()

            # Create variables in streamlit.session_state for storing between runs
            streamlit.session_state['Arrays_fuer_Clouds'] = {}
            streamlit.session_state['Button_gedrueckt'] = False
            streamlit.session_state['Cookies'] = User_Interface._Funk_Cookies_aus_Datei_laden()

            streamlit.session_state['User_Interface_eingerichtet'] = 'Startseite'

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
        self._Funk_Expander_Optionen_bestuecken()

    
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
                self.Platzhalter_Ausgabe_Feedback = streamlit.empty()
                self.Platzhalter_Ausgabe_Ergebnisse = streamlit.empty()

            # Scroll to the top
            User_Interface._Funk_Scrollen(Arg_Element='summary.st-emotion-cache-p5msec.eqpbllx2')
            
            self.Expander_Anleitung = streamlit.expander('Anleitung:', expanded=True)

            with self.Expander_Anleitung:
                self.Platzhalter_Anleitung_01 = streamlit.empty()

                streamlit.markdown('### **Willkommen bei Newscloud!**')
                streamlit.write('''Mit dieser Web App kannst du zu einem Suchbegriff eine Wordcloud
                    für deutschsprachige News erstellen. Dazu werden die Überschriften und
                    Vorschautexte mehrerer Newsartikel gesammelt und analysiert. Die Gesamtmenge
                    gesammelter **_Elemente_** besteht also aus Überschriften UND Vorschautexten.
                    Aus dieser Gesamtmenge werden die Wörter für die Wordcloud extrahiert. Die
                    Größe der abgebildeten Wörter in der Wordcloud repräsentiert deren relative
                    Häufigkeit in der Gesamtmenge. Die Anordnung der Wörter hat aber keine
                    Bedeutung! Das gemittelte Sentiment (über alle Überschriften und Vorschautexte
                    wird durch die Farbe der Wordcloud dargestellt, s.
                    [detaillierte Erläuterung unten](#72753e29). Schau auch mal in den Abschnitt zu
                    [interessanten Suchtipps](#interessante-suchtipps)!''')
                streamlit.write('''Jede neue Wordcloud und ihre zugehörigen Daten werden in einem
                    App-internen Tab im Bereich **"Ausgabe:"** (s. oben) dargestellt.
                    Ein erneuter Auftrag mit dem identischen Suchbegriff überschreibt die Daten
                    im alten Tab. Es können maximal 3 dieser Tabs geöffnet sein. Der älteste
                    wird gelöscht, falls diese Grenze überschritten wird. Das Neuladen oder
                    Schließen des _Browsertabs_ löscht alle deine bisherigen Ergebnisse! Um noch
                    mehr Ergebnisse zu vergleichen (oder um weniger zu scrollen), öffne die
                    Web App einfach in einem weiteren Browsertab. Auch wichtig:
                    [Hinweis zum Rate Limiting](#hinweis-zum-rate-limiting).''')
                streamlit.write('''**_Diese Anleitung wird sich immer ganz unten in der Web App
                    wiederfinden lassen._**''')
                
                streamlit.markdown('#### **Detaillierte Erläuterung:**')
                streamlit.write('''Für deinen Suchbegriff werden die ersten 3 Seiten News einer
                    bekannten Internetsuchmaschine gesammelt. Diese Rohaten teilen sich auf in die
                    Überschriften der Artikel und deren Vorschautexte. Nur deutsche Inhalte werden
                    weiterverarbeitet. Es müssen mindestens 10 Elemente (d. h. deutsche
                    Überschriften und / oder Vorschautexte) für eine weitere Bearbeitung deines
                    Auftrags vorliegen. Aus den Vorschautexten wird zudem der
                    Veröffentlichungszeitpunkt entfernt (z. B. "vor 2 Tagen"). Beachte, dass bei
                    ungewöhnlichen Suchbegriffen mit seltenen News auch alte oder wenig sinnvolle
                    Daten ausgewertet werden können. Außerdem kann es sein, dass das Sprachmodell
                    fälschlicherweise deutsche Texte nicht erkennt und aussortiert. Die
                    verarbeiteten Daten und auch die Rohdaten erscheinen unter der jeweiligen
                    Newscloud, sodass du dort nachvollziehen kannst, welche Daten aussortiert
                    wurden und wie alt die einzelnen Daten sind.''')
                streamlit.write('''Das Sentiment wird nun für jede Überschrift und jeden
                    Vorschautext einzeln mit dem Package bzw. Sprachmodell
                    [german-sentiment-lib](https://huggingface.co/oliverguhr/german-sentiment-bert)
                    von Oliver Guhr analysiert. Eine negatives Sentiment wird danach intern mit
                    dem Wert -1 abgebildet, ein neutrales mit 0 und ein positives mit +1. Aus
                    diesen Einzelwerten wird ein Mittelwert gebildet. Ein Mittelwert von 0 äußert
                    sich in einer gelben Wordcloud. Ein Mittelwert von 0 könnte z. B. dadurch
                    enstehen, dass alle Elemente ein neutrales Sentiment haben oder auch dadurch,
                    dass die Elemente hälftig ein positives bzw. ein negatives Sentiment besitzen.
                    Mittwerte unter bzw. über ± 0,33 werden auf ± 0,33 begrenzt. Mittelwerte über
                    0 sind sehr selten. Die Farbe deiner Wordcloud wird also nur sehr selten ein
                    kräftiges Grün sein. Orange oder rot werden dagegen etwas häufiger auftreten.
                    Zwischen rot und grün gibt es mehere Abstufungen, wie du sehen wirst.''')
                streamlit.write('''Das Sprachmodell wird das Sentiment oft anders beurteilen als
                    du. Das Sentiment spiegelt nicht die Meinung einer konkreten Person wider. Das
                    Sentiment ist auch nicht unmittelbar eine Bewertung deines Suchbegriffs (z. B.
                    einer Person), sondern ist auch abhängig von Ereignissen im Zusammenhang mit
                    deinem Suchbegriff. Auf diese Ereignisse hat eine Person manchmal gar keinen
                    Einfluss. Du kannst das Sentiment für jedes Element unter der Wordcloud finden.
                    Weiter unten finden sich auch die unverarbeiteten Rohdaten.''')
                streamlit.write('''Für die Wordcloud werden Bindestriche aus den Rohdaten entfernt
                    und die Wörter lemmatisiert. In der Wordcloud werden nur Lemmata bzw. Wörter
                    angezeigt, die Nomen oder Verben sind und mindestens 4 Mal vorkommen.
                    Beachte, dass es durch die Lemmatisierung manchmal zu fehlerhaft gebildeten
                    Wörtern kommt (z. B. bei seltenen Wörtern oder Namen).''')

                streamlit.markdown('#### **Interessante Suchtipps:**')
                streamlit.markdown('''Suche z. B nach den Namen deutscher Parteien, prominenter
                    Personen oder Städte. Vergleiche auch mal die Suchergebnisse von eigentlich
                    neutralen Begriffen / Ereignissen, um die Entscheidungen des Sprachmodells zu
                    untersuchen. Versuche vielleicht auch mal Begriffe / Ereignisse in den News zu
                    finden, welche besonders positiv oder negativ vom Sprachmodell bewertet werden.
                    Insbesondere das Finden von positiven Ergebnissen kann eine Herausforderung
                    sein (versuche vielleicht mal nach aktuellen Sportevents zu suchen, welche für
                    Freude gesorgt haben)!''')

                streamlit.markdown('#### **!!!!! HINWEIS ZUM RATE LIMITING !!!!!:**')
                streamlit.write(f'''Die Suchrate ist so beschränkt beschränkt, dass über _alle
                    aktiven Appnutzer/innen summiert_ maximal
                    {int(Constants.N_FUER_RATELIMIT / Constants.ANZAHL_SEITEN)} Aufträge pro
                    {Constants.ZEITRAUM_FUER_RATELIMIT} Sekunden bearbeitet werden können.
                    Wenn dieses Kontingent (von einer anderen Person oder dir) bereits ausgeschöpft
                    wurde, warte bitte ein paar Sekunden und versuche deinen Auftrag erneut zu
                    senden. Beachte außerdem, dass die Seite, von der die News stammen, absichtlich
                    etwas langsamer durchsucht wird, um diese nicht unnötig zu belasten.''')
                                
    
    def _Funk_Expander_Optionen_bestuecken(self):
        """Sets up options in attribute Platzhalter_Optionen_01 which
        can be used by the user.
        """
        with self.Platzhalter_Optionen_01: 
            with streamlit.form('Suchparameter'):
                streamlit.markdown('##### **Suchbegriff:**')    
                self.Input_Suchbegriff = streamlit.text_input('Hier Suchbegriff eingeben!:',
                                                              max_chars=50)

                # The code of the if block is only executed in a run of the script if the user
                # pressed the button in the previous run
                if streamlit.form_submit_button(
                    'BUTTON: Newscloud erstellen!',
                    on_click=self._Funk_on_click_Button
                    ):
                        pass

    
    def _Funk_on_click_Button(self):
        """This function is called before running the script again when
        the button is pressed by the user.
        """
        # Clear Streamlit URL before running the script again
        streamlit.query_params.clear()
        
        # Set session_state['Button_gedrueckt'] = True to tell the Eventamanager in the subsequent
        # run of the main script that there are open jobs
        streamlit.session_state['Button_gedrueckt'] = True


    def Funk_Feedback_ausgeben(
            self,
            Arg_Art,
            Arg_Nachricht: str
            ):
        """Prints feedback in the UI in attribute
        Platzhalter_Ausgabe_Feedback.

        Keyword arguments:\n
        Arg_Nachricht -- Message to show\n
        Arg_Art -- Select 'Fehler' pro printing error feedback or
        'Erfolg' for printing success feedback
        """
        with self.Platzhalter_Ausgabe_Feedback:
            if Arg_Art == 'Fehler':
                streamlit.warning(Arg_Nachricht)
            elif Arg_Art == 'Erfolg':
                streamlit.success(Arg_Nachricht)

    
    def Funk_Ergebnisse_ausgeben(
            self,
            **kwargs):
        """Creates all result tabs with one word cloud each based on
        saved data from session_state.
        """
        # If there is nothing to show, return
        if len(streamlit.session_state['Arrays_fuer_Clouds'].keys()) == 0:
            return()

        # Elif there are more than 3 tabs with different search terms, delete the oldest one
        elif len(streamlit.session_state['Arrays_fuer_Clouds'].keys()) > 3:
            Liste_Suchbeggriffe_in_state = list(streamlit.session_state['Arrays_fuer_Clouds'].\
                                                keys())
            Liste_Suchbeggriffe_in_state.reverse()
            
            for i, x in enumerate (Liste_Suchbeggriffe_in_state):
                if i > 2:
                    del(streamlit.session_state['Arrays_fuer_Clouds'][x])

        Liste_Namen_Tabs = []
        Liste_fuer_Loop = []

        for Key_x in streamlit.session_state['Arrays_fuer_Clouds']:
            Liste_Namen_Tabs.append(f':rainbow[{Key_x}]')
            Liste_fuer_Loop.append(Key_x)

        Liste_Namen_Tabs.reverse()
        Liste_fuer_Loop.reverse()
        
        with self.Platzhalter_Ausgabe_Ergebnisse:
            self.Liste_Tabs = streamlit.tabs(Liste_Namen_Tabs)

            # Create word cloud for each saved array from previous order and the current one
            for i, x in enumerate(Liste_fuer_Loop):
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

                    streamlit.markdown('<span style="color: hsl(0, 100%, 50%)">Rot </span>'
                                        + 'steht für ein negatives, '
                                        + '<span style="color: hsl(60, 100%, 50%)">gelb </span>'
                                        + 'für ein neutrales und '
                                        + '<span style="color: hsl(120, 100%, 50%)">grün </span>'
                                        + '''für ein positives Sentiment. Mehr zur Berechnung des
                                        Sentiments in der [Anleitung](#72753e29). Schau auch mal
                                        in den Abschnitt zu
                                        [interessanten Suchtipps](#interessante-suchtipps)!''',
                                        unsafe_allow_html=True
                                        )
                    
                    if i == 0:
                        streamlit.markdown('''Hier geht es direkt nach unten zu den
                            _verarbeiteten (d. h. ausgewerteten) Daten und zugehörigen Sentiments_
                            der
                            [Überschriften](#59389694) oder der
                            [Vorschautexte](#verarbeitete-vorschautexte).
                            ''')
                        streamlit.markdown('''Direkt nach unten zu den _Rohdaten_ (d. h. allen
                            gefundenen und ungekürzten Daten) der
                            [Überschriften](#3e5eac6d) oder der
                            [Vorschautexte](#rohdaten-vorschautexte).
                            ''')
            
                    streamlit.markdown('#### **Verarbeitete Überschriften:**')
                    streamlit.write(Buch_fuer_Tab['Verarbeitete_Ueberschriften'])
                    streamlit.markdown('#### **Verarbeitete Vorschautexte:**')
                    streamlit.write(Buch_fuer_Tab['Verarbeitete_Vorschautexte'])
                    streamlit.markdown('#### **Rohdaten Überschriften:**')
                    streamlit.write(Buch_fuer_Tab['Rohdaten_Ueberschriften'])
                    streamlit.markdown('#### **Rohdaten Vorschautexte:**')
                    streamlit.write(Buch_fuer_Tab['Rohdaten_Vorschautexte'])

    
    def Funk_Jobs_pruefen(self):
        """Checks whether there are open jobs, i. e. whether the button
        was pressed by the user.
        """    
        if streamlit.session_state['Button_gedrueckt'] == True:
            # Tell the Eventmanager that the button was pressed by the user
            self.Eventmanager.Funk_Event_eingetreten(
                Arg_Event_Name='Button_gedrueckt',
                Arg_Argumente_von_Event={
                    'Arg_Auftrag_Suchbegriff': self.Input_Suchbegriff
                    }
                )
            

    def Funk_Aufraeumen(
            self,
            **kwargs):
        """Cleans up and stops the script from running."""
        self.Platzhalter_Ausgabe_Spinner_02.empty()
        
        streamlit.session_state['Button_gedrueckt'] = False

        self.Platzhalter_Ausgabe_Spinner_01.empty()

        User_Interface._Funk_Scrollen(Arg_Element='summary.st-emotion-cache-p5msec.eqpbllx2')

        streamlit.stop()
    

    @staticmethod
    def _Funk_Scrollen(
            Arg_Element
            ):
        """Scrolls page element in argument Arg_Element into view.
        
        Keyword arguments:\n
        Arg_Element -- HTML Element to scroll to
        """
        Dummy = datetime.datetime.now().timestamp()
        Komponenten.html(
            f"""
                <p>{Dummy}</p>
                <script>
                    window.parent.document.querySelector('{Arg_Element}').scrollIntoView();
                </script>
            """,
            height=0
            )
