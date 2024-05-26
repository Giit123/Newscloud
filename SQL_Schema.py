"""This module contains the SQL class SQL_Klasse_Tracker.

Classes:\n
    SQL_Klasse_Tracker -- An instance of this class represents an entry
    in the SQL table with the tablename Tabelle_Tracker.
"""

# %%
###################################################################################################
import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

SQL_Basis = declarative_base()


# %%
###################################################################################################
class SQL_Klasse_Tracker(SQL_Basis):
    """An instance of this class represents an entry in the SQL table
    with the name Tabelle_Tracker.
    """
    __tablename__ = 'Tabelle_Tracker'

    Tracker_ID: Mapped[str] = mapped_column(
        sqlalchemy.String(200),
        primary_key=True
        )
    
    # Time of last successfully processed job / order as string
    Letzter_Job_Zeit: Mapped[str] = mapped_column(sqlalchemy.String(100))
    # Time of last processed job / order as timestamp
    Letzter_Job_Zeit_stamp: Mapped[int] = mapped_column(sqlalchemy.Integer)
    # Sum of pages of all processed jobs / orders in the timeframe ZEITRAUM_FUER_RATELIMIT definded
    # in Constants.py
    Summe_n_aktuell_in_Zeitraum: Mapped[int] = mapped_column(sqlalchemy.Integer)
    # Timestamp of last zeroing of Summe_n_aktuell_in_Zeitraum
    Letzte_Nullung_stamp: Mapped[int] = mapped_column(sqlalchemy.Integer)

    def __repr__(self):
        return(
            f'<SQL_Klasse_Tracker(Tracker_ID={self.Tracker_ID},\
                Letzter_Job_Zeit={self.Letzter_Job_Zeit},\
                Letzter_Job_Zeit_stamp={self.Letzter_Job_Zeit_stamp},\
                Summe_n_aktuell_in_Zeitraum={self.Summe_n_aktuell_in_Zeitraum},\
                Letzte_Nullung_stamp={self.Letzte_Nullung_stamp},)>'
            ) 
