# Newscloud

(German version below!)

Welcome to Newscloud! With this web app, you can create a word cloud by scraping german news for a specific search term.

The design of the code is based on the [**observer design pattern**](https://refactoring.guru/design-patterns/observer) in the broadest sense: An instance of the class Eventmanager serves as a coordinator between the classes Scraper_Worker, Analyzer_Worker and User_Interface. This instance (named 'Eventmanager_A' in the file Newscloud.py) has an attribute _Events_Dict. This is a dictionary that contains the names of specific events as keys and the subscriber functions and their parameter as values (as another dictionary).

The web app is built with the framework [**Streamlit**](https://streamlit.io/). The most important characteristic of Streamlit is that the main script of the web app (Newscloud.py) runs again from top to bottom every time the user presses a button. Buttons can be used in [several ways](https://docs.streamlit.io/library/advanced-features/button-behavior-and-examples) to affect subsequent runs of the main script. In this web app the 'communication' between runs happens by using the Streamlit feature [session_state](https://docs.streamlit.io/library/api-reference/session-state) which allows to store information between runs.

Because the web app should run on [**Heroku Eco dynos**](https://devcenter.heroku.com/articles/dyno-types) and the language model is already of significant size, only 3 word clouds can be saved per user at the same time (the data for the word clouds are saved in memory, not in the SQL database). The oldest word cloud will be deleted if the user searches for a forth search term.

## Prerequisites and requirements

The limit for requests (respectively orders) summed over all users is implemented by the SQL class SQL_Klasse_Tracker which monitors the sum of all processed orders in a specific timeframe (definded in Constants.py). The web app is built to be deployed with Heroku and uses the [**PostgreSQL database add-on**](https://elements.heroku.com/addons/heroku-postgresql). If you want to run the app locally, you have to access the PostgreSQL database as remote.

The requirements.txt contains the packages for deployment on Heroku. You also have to add an nltk.txt file to your repository for Heroku to download the [nltk Punkt sentence tokenizer](https://www.nltk.org/_modules/nltk/tokenize/punkt.html) in the [deployment process](https://devcenter.heroku.com/articles/python-nltk). If you want to use the app locally, you have to download punkt with [nltk.download(punkt)](https://www.nltk.org/data.html) in your virtual environment.

The deployment was done with Python 3.9.18. The code is divided into cells by using the seperator "# %%". In this way, the code can be exported as Jupyter notebook in VS Code.

## Disclaimer

To actually use the web app, there are some to-dos which are not described here because the author does not want to encourage web scraping of the particular site (which is not allowed). The code is for general demonstration purposes only. Also notice that there is [**no license**](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) for this project, so (re)use of the code is prohibited.


--------------------------------------------------------------------------------------------------------------
## Deutsche Version

Willkommen bei Newscloud! Mit dieser Web App kannst du eine Wordcloud erstellen, indem du Webscraping von deutschsprachigen News für einen bestimmten Suchbegriff anwendest.

Das Design des Codes basiert im weitesten Sinne auf dem [**Observer Design Pattern**](https://refactoring.guru/design-patterns/observer): Eine Instanz der Klasse Eventmanager dient als Koordinator der Klassen Scraper_Worker, Analyzer_Worker und User_Interface. Diese Instanz (mit dem Namen 'Eventmanager_A' in der Datei Newscloud.py) besitzt ein Attribut _Events_Dict. Dies ist ein Dictionary, welches die Namen von spezifischen Events als Keys und die Subscriber Funktionen und deren Parameter als Values enthält (als ein weiteres Dictionary).

Die Web App ist mit dem Framework [**Streamlit**](https://streamlit.io/) erstellt. Das wichtigste Merkmal von Streamlit ist, dass das Main-Skript der Web App (Newscloud.py) erneut von Anfang bis Ende durchlaufen wird, wann immer der/die User/in einen Button drückt. Buttons können auf [unterschiedliche Weise](https://docs.streamlit.io/library/advanced-features/button-behavior-and-examples) genutzt werden, um nachfolgende Durchläufe des Main-Skripts zu beeinflussen. In dieser Web App erfolgt die 'Kommunikation' zwischen verschiedenen Durchläufen mittels des Streamlit Features [session_state](https://docs.streamlit.io/library/api-reference/session-state), welches die Speicherung von Informationen zwischen verschiedenen Runs erlaubt.

Weil die Web App auf [**Heroku Eco dynos**](https://devcenter.heroku.com/articles/dyno-types) laufen soll und auch das Sprachmodell viele Ressourcen benötigt, werden je Nutzer/in nur 3 Wordclouds zu einem gegebenen Zeitpunkt gespeichert (die Daten werden in memory gespeichert, nicht in der SQL Datenbank). Die älteste Wordcloud wird gelöscht, wenn der/die User/in nach einem vierten Suchbegriff sucht.

## Voraussetzungen und Anforderungen

Das Limit für Anfragen (bzw. Aufträge) summiert über alle User/innen ist mittels der SQL Klasse SQL_Klasse_Tracker implementiert, welche die Summe aller verarbeiteten Aufträge in einem spezifischen Zeitraum überwacht (definiert in Constants.py). The Web App soll mit Heroku deployed werden und nutzt das [**PostgreSQL database add-on**](https://elements.heroku.com/addons/heroku-postgresql). Wenn du die App lokal nutzen möchtest, musst du auf die PostgresSQL Datenbank remote zugreifen.

Die Datei requirements.txt enthält die Packages für das Deployment bei Heroku. Du musst zudem eine Datei nltk.txt zu deinem Repository für Heroku hinzufügen, um den [nltk Punkt sentence tokenizer](https://www.nltk.org/_modules/nltk/tokenize/punkt.html) während des [Deployment Prozesses](https://devcenter.heroku.com/articles/python-nltk) zu downloaden. Wenn du die App lokal nutzen möchtest, musst du punkt mit [nltk.download(punkt)](https://www.nltk.org/data.html) in deinem virtuellen Environment downloaden.

Das Deployment erfolgte mit Python 3.9.18. Der Code ist mittels des Seperators "# %%" in Zellen unterteilt. Auf diese Weise kann der Code in VS Code als Jupyter Notebook exportiert werden.

## Disclaimer

Um die Web App tatsächlich zu nutzen, sind einige weitere Aufgaben zu erledigen, die hier nicht beschrieben wurden, weil der Autor nicht zum Web Scraping der Seite ermutigen möchte (solches ist nämlich nicht erlaubt). Der Code dient nur allgemeinen Demonstrationszwecken. Es sei außerdem darauf hingewiesen, dass [keine Lizenz](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) für dieses Projekt vorliegt, sodass eine (Weiter-)verwendung dieses Codes nicht erlaubt ist.