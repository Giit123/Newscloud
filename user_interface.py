"""This module contains the class UserInterface.

Classes:\n
    UserInterface -- An instance of this class can perform all UI
    related actions in the web app.
"""

# %%
###################################################################################################
import streamlit
import streamlit.components.v1 as import_komponenten

import datetime
import time
import pickle

##################################################
# Import modules from folder
import constants
from eventmanager import Eventmanager


# %%
###################################################################################################
class UserInterface:
    """An instance of this class can perform all UI related actions in
    the web app.

    Attributes:\n
        CAUTION!: All attributes should be used as private ones despite
        not being prefixed with an underscore.\n
        eventmanager -- Instance of eventmanager to work with\n
        spalte_A, spalte_B -- Invisible columns in which elements can
        be inserted\n
        expander_optionen -- Equippable expander element on the left
        side of the UI for options\n
        expander_ausgabe -- Equippable expander element on the upper
        side of the UI for the results of the user's orders\n
        expander_anleitung -- Equippable expander element on the lower
        side of the UI for the manual\n
        platzhalter -- All attributes which have "platzhalter" in their
        name are streamlit objects which can be equipped with objects
        that should be displayed to the user\n
        input_suchbegriff -- Search term currenty typed in by the user
        in the UI\n
        liste_tabs -- List with tabs, each for one of the last three
        successfully processed orders sent by the user
    
    Public methods:\n
        funk_einrichten -- Sets up user interface.\n
        funk_feedback_ausgeben -- Prints feedback in the UI in attribute
        platzhalter_ausgabe_feedback.\n
        funk_ergebnisse_ausgeben -- Creates all result tabs with one
        wordcloud each based on saved data from session_state.\n
        funk_jobs_pruefen -- Checks whether there are open jobs, i. e.
        the button was pressed by the user.\n
        funk_aufraeumen -- Cleans up and stops stopping the script from
        running.

    Private methods:\n
        _funk_cookies_aus_datei_laden -- Returns cookies from file.\n
        _funk_startseite_einrichten -- Sets up basic user interface
        template.\n
        _funk_geruest_erstellen -- Creates elements for basic user
        interface template.\n
        _funk_expander_optionen_bestuecken -- Sets up options in
        attribute platzhalter_optionen_01 which can be used by the
        user.\n
        _funk_on_click_button -- This function is called when the
        button is pressed by the user.\n
        _funk_scrollen -- Scrolls page element in argument
        arg_element into view.
    """

    def __init__(
            self,
            init_eventmanager: Eventmanager
            ):
        """inits UserInterface.

        Keyword arguments:\n
        init_eventmanager -- Active instance of class Eventmanager
        """
        self.eventmanager = init_eventmanager

        self.spalte_A = None
        self.spalte_B = None
        self.expander_optionen = None
        self.platzhalter_optionen_01 = None
        self.expander_ausgabe = None
        self.platzhalter_ausgabe_spinner_01 = None
        self.platzhalter_ausgabe_spinner_02 = None
        self.platzhalter_ausgabe_feedback = None
        self.platzhalter_ausgabe_ergebnisse = None
        self.expander_anleitung = None
        self.platzhalter_anleitung_01 = None
        self.input_suchbegriff = None
        self.liste_tabs = None


    def funk_einrichten(self):
        """Sets up user interface."""
        # First loading of the web app by the user
        if 'User_Interface_eingerichtet' not in streamlit.session_state:
            self._funk_startseite_einrichten()

            # Create variables in streamlit.session_state for storing between runs
            streamlit.session_state['Arrays_fuer_Clouds'] = {}
            streamlit.session_state['Button_gedrueckt'] = False
            streamlit.session_state['Cookies'] = UserInterface._funk_cookies_aus_datei_laden()

            streamlit.session_state['User_Interface_eingerichtet'] = 'Startseite'

        elif streamlit.session_state['Button_gedrueckt'] == True:
            self._funk_startseite_einrichten()

        else:
            self._funk_startseite_einrichten()


    @staticmethod
    def _funk_cookies_aus_datei_laden():
        """Returns cookies from file."""
        with open('Cookies.pickle', 'rb') as datei:
            cookies_geladen = pickle.load(datei)
        return(cookies_geladen)
    

    def _funk_startseite_einrichten(self):
        """Sets up basic user interface template."""
        self._funk_geruest_erstellen()
        self._funk_expander_optionen_bestuecken()

    
    def _funk_geruest_erstellen(self):
        """Creates elements for basic user interface template."""
        self.spalte_A, self.spalte_B = streamlit.columns((10, 35))

        with self.spalte_A:
            self.expander_optionen = streamlit.expander('Optionen:', expanded=True)

            with self.expander_optionen:
                self.platzhalter_optionen_01 = streamlit.empty()

        with self.spalte_B:
            self.expander_ausgabe = streamlit.expander('Ausgabe:', expanded=True)

            with self.expander_ausgabe:
                self.platzhalter_ausgabe_spinner_01 = streamlit.empty()
                self.platzhalter_ausgabe_spinner_02 = streamlit.empty()
                self.platzhalter_ausgabe_feedback = streamlit.empty()
                self.platzhalter_ausgabe_ergebnisse = streamlit.empty()

            UserInterface._funk_scrollen(arg_element='div.st-emotion-cache-18kf3ut')
            
            self.expander_anleitung = streamlit.expander('Anleitung:', expanded=True)

            with self.expander_anleitung:
                self.platzhalter_anleitung_01 = streamlit.empty()

                streamlit.markdown('### **Willkommen bei Newscloud!**')
                streamlit.write('''Mit dieser Web App kannst du zu einem Suchbegriff eine Wordcloud
                    für deutschsprachige News erstellen. Dazu werden die Überschriften und
                    Vorschautexte mehrerer Newsartikel gesammelt und analysiert. Die
                    **_Gesamtmenge_** gesammelter Elemente besteht also aus Überschriften UND
                    Vorschautexten.
                    Aus dieser Gesamtmenge werden die Wörter für die Wordcloud extrahiert. Die
                    Größe der abgebildeten Wörter in der Wordcloud repräsentiert deren relative
                    Häufigkeit in der Gesamtmenge. Die Anordnung der Wörter in der Wordcloud hat
                    aber keine Bedeutung!
                    Das gemittelte Sentiment (über alle Überschriften und Vorschautexte
                    wird durch die Farbe der Wordcloud dargestellt, s.
                    [detaillierte Erläuterung unten](#detaillierte-erlaeuterung)). Schau auch mal
                    in den Abschnitt zu [interessanten Suchtipps](#interessante-suchtipps)!''')
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
                streamlit.write('''Das Sentiment wird zunächst für jede Überschrift und jeden
                    Vorschautext einzeln mit dem Package bzw. Sprachmodell
                    [german-sentiment-lib](https://huggingface.co/oliverguhr/german-sentiment-bert)
                    von Oliver Guhr analysiert. Eine negatives Sentiment wird danach intern mit
                    dem Wert -1 abgebildet, ein neutrales mit 0 und ein positives mit +1. Aus
                    diesen Einzelwerten wird ein Mittelwert gebildet. Ein Mittelwert von 0 äußert
                    sich in einer gelben Wordcloud. Ein Mittelwert von 0 könnte z. B. dadurch
                    enstehen, dass alle Elemente ein neutrales Sentiment besitzen oder auch
                    dadurch, dass die Elemente hälftig ein positives bzw. ein negatives Sentiment
                    besitzen. Mittwerte unter bzw. über ± 0,33 werden auf ± 0,33 begrenzt.
                    Mittelwerte über 0 sind sehr selten. Die Farbe deiner Wordcloud wird also nur
                    sehr selten ein kräftiges Grün sein. Orange oder rot werden dagegen etwas
                    häufiger auftreten. Zwischen rot und grün gibt es mehere Abstufungen, wie du
                    sehen wirst.''')
                streamlit.write('''Das Sprachmodell wird das Sentiment oft anders beurteilen als
                    du. Das Sentiment spiegelt nicht die Meinung einer konkreten Person wider. Das
                    Sentiment ist auch nicht unmittelbar eine Bewertung deines Suchbegriffs (z. B.
                    einer Person, nach der du suchst), sondern ist auch abhängig von Ereignissen im
                    Zusammenhang mit deinem Suchbegriff. Auf diese Ereignisse hat eine Person
                    manchmal gar keinen Einfluss. Du kannst das Sentiment für jedes Element unter
                    der Wordcloud finden. Weiter unten finden sich auch die unverarbeiteten
                    Rohdaten.''')
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
                    {int(constants.N_FUER_RATELIMIT / constants.ANZAHL_SEITEN)} Aufträge pro
                    {constants.ZEITRAUM_FUER_RATELIMIT} Sekunden bearbeitet werden können.
                    Wenn dieses Kontingent (von einer anderen Person oder dir) bereits ausgeschöpft
                    wurde, warte bitte ein paar Sekunden und versuche deinen Auftrag erneut zu
                    senden. Beachte außerdem, dass die Seite, von der die News stammen, absichtlich
                    etwas langsamer durchsucht wird, um diese nicht unnötig zu belasten.''')
                                
    
    def _funk_expander_optionen_bestuecken(self):
        """Sets up options in attribute platzhalter_optionen_01 which
        can be used by the user.
        """
        with self.platzhalter_optionen_01: 
            with streamlit.form('Suchparameter'):
                streamlit.markdown('##### **Suchbegriff:**')    
                self.input_suchbegriff = streamlit.text_input('Hier Suchbegriff eingeben!:',
                                                              max_chars=50)

                # The code of the if block is only executed in a run of the script if the user
                # pressed the button in the previous run
                if streamlit.form_submit_button(
                    'BUTTON: Newscloud erstellen!',
                    on_click=self._funk_on_click_button
                    ):
                        pass

    
    def _funk_on_click_button(self):
        """This function is called before running the script again when
        the button is pressed by the user.
        """
        # Clear Streamlit URL before running the script again
        streamlit.query_params.clear()
        
        # Set session_state['Button_gedrueckt'] = True to tell the eventmanager in the subsequent
        # run of the main script that there are open jobs
        streamlit.session_state['Button_gedrueckt'] = True


    def funk_feedback_ausgeben(
            self,
            arg_art,
            arg_nachricht: str
            ):
        """Prints feedback in the UI in attribute
        platzhalter_ausgabe_feedback.

        Keyword arguments:\n
        arg_nachricht -- Message to show\n
        arg_art -- Select 'Fehler' pro printing error feedback or
        'Erfolg' for printing success feedback
        """
        with self.platzhalter_ausgabe_feedback:
            if arg_art == 'Fehler':
                streamlit.warning(arg_nachricht)
            elif arg_art == 'Erfolg':
                streamlit.success(arg_nachricht)

    
    def funk_ergebnisse_ausgeben(
            self,
            **kwargs):
        """Creates all result tabs with one wordcloud each based on
        saved data from session_state.
        """
        # If there is nothing to show, return
        if len(streamlit.session_state['Arrays_fuer_Clouds'].keys()) == 0:
            return()

        # Elif there are more than 3 tabs with different search terms, delete the oldest one
        elif len(streamlit.session_state['Arrays_fuer_Clouds'].keys()) > 3:
            liste_suchbegriffe_in_state = list(streamlit.session_state['Arrays_fuer_Clouds'].\
                                                keys())
            liste_suchbegriffe_in_state.reverse()
            
            for i, x in enumerate (liste_suchbegriffe_in_state):
                if i > 2:
                    del(streamlit.session_state['Arrays_fuer_Clouds'][x])

        liste_namen_tabs = []
        liste_fuer_loop = []

        for key_x in streamlit.session_state['Arrays_fuer_Clouds']:
            liste_namen_tabs.append(f':rainbow[{key_x}]')
            liste_fuer_loop.append(key_x)

        liste_namen_tabs.reverse()
        liste_fuer_loop.reverse()
        
        with self.platzhalter_ausgabe_ergebnisse:
            self.liste_tabs = streamlit.tabs(liste_namen_tabs)

            # Create wordcloud for each saved array from previous order and the current one
            for i, x in enumerate(liste_fuer_loop):
                buch_fuer_tab = streamlit.session_state['Arrays_fuer_Clouds'][x]
                
                array = buch_fuer_tab['Array']
                with self.liste_tabs[i]:    
                    linke_spalte, mittlere_spalte, rechte_spalte = streamlit.columns([1,4,1])
                    with mittlere_spalte:
                        streamlit.image(
                            array,
                            width="stretch",
                            output_format='PNG'
                            )

                    time.sleep(0.1)

                    streamlit.markdown('<span style="color: hsl(0, 100%, 50%)">Rot </span>'
                                        + 'steht für ein negatives, '
                                        + '<span style="color: hsl(60, 100%, 50%)">gelb </span>'
                                        + 'für ein neutrales und '
                                        + '<span style="color: hsl(120, 100%, 50%)">grün </span>'
                                        + '''für ein positives Sentiment. Mehr zur Berechnung des
                                        Sentiments findest du unten in der [Anleitung](#willkommen-bei-newscloud).
                                        Schau auch mal in den Abschnitt zu
                                        [interessanten Suchtipps](#interessante-suchtipps)!''',
                                        unsafe_allow_html=True
                                        )
                    
                    if i == 0:
                        streamlit.markdown('''Hier geht es direkt nach unten zu den
                            _verarbeiteten (d. h. ausgewerteten) Daten und zugehörigen Sentiments_
                            der
                            [Überschriften](#verarbeitete-ueberschriften) oder der
                            [Vorschautexte](#verarbeitete-vorschautexte).
                            ''')
                        streamlit.markdown('''Direkt nach unten zu den _Rohdaten_ (d. h. allen
                            gefundenen und ungekürzten Daten) der
                            [Überschriften](#rohdaten-ueberschriften) oder der
                            [Vorschautexte](#rohdaten-vorschautexte).
                            ''')
            
                    streamlit.markdown('#### **Verarbeitete Überschriften:**')
                    streamlit.write(buch_fuer_tab['Verarbeitete_Ueberschriften'])
                    streamlit.markdown('#### **Verarbeitete Vorschautexte:**')
                    streamlit.write(buch_fuer_tab['Verarbeitete_Vorschautexte'])
                    streamlit.markdown('#### **Rohdaten Überschriften:**')
                    streamlit.write(buch_fuer_tab['Rohdaten_Ueberschriften'])
                    streamlit.markdown('#### **Rohdaten Vorschautexte:**')
                    streamlit.write(buch_fuer_tab['Rohdaten_Vorschautexte'])

    
    def funk_jobs_pruefen(self):
        """Checks whether there are open jobs, i. e. whether the button
        was pressed by the user.
        """    
        if streamlit.session_state['Button_gedrueckt'] == True:
            # Tell the eventmanager that the button was pressed by the user
            self.eventmanager.funk_event_eingetreten(
                arg_event_name='Button_gedrueckt',
                arg_argumente_von_event={
                    'arg_auftrag_suchbegriff': self.input_suchbegriff
                    }
                )
            

    def funk_aufraeumen(
            self,
            **kwargs):
        """Cleans up and stops the script from running."""
        self.platzhalter_ausgabe_spinner_02.empty()
        
        streamlit.session_state['Button_gedrueckt'] = False

        self.platzhalter_ausgabe_spinner_01.empty()

        UserInterface._funk_scrollen(arg_element='div.st-emotion-cache-18kf3ut')

        streamlit.stop()
    

    @staticmethod
    def _funk_scrollen(
            arg_element
            ):
        """Scrolls page element in argument arg_element into view.
        
        Keyword arguments:\n
        arg_element -- HTML element to scroll to
        """
        dummy = datetime.datetime.now().timestamp()
        
        import_komponenten.html(
	        html=
                f"""
                    <!--<p>{dummy}</p>-->
                    <script>
                        window.parent.document.querySelector('{arg_element}').scrollIntoView();
                    </script>
                """,
            height=1
            )
