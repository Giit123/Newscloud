"""This module contains the SQL class sqlKlasseTracker.

Classes:\n
    sqlKlasseTracker -- An instance of this class represents an entry
    in the SQL table with the name Tabelle_Tracker.
"""

# %%
###################################################################################################
import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

sql_basis = declarative_base()


###################################################################################################
class sqlKlasseTracker(sql_basis):
    """An instance of this class represents an entry in the SQL table
    with the tablename Tabelle_Tracker.
    """
    __tablename__ = 'Tabelle_Tracker'

    tracker_id: Mapped[str] = mapped_column(
        sqlalchemy.String(200),
        primary_key=True
        )
    
    # Time of last successfully processed job / order as string
    letzter_job_zeit: Mapped[str] = mapped_column(sqlalchemy.String(100))
    # Time of last processed job / order as timestamp
    letzter_job_zeit_stamp: Mapped[int] = mapped_column(sqlalchemy.Integer)
    # Sum of pages of all processed jobs / orders in the timeframe ZEITRAUM_FUER_RATELIMIT definded
    # in constants.py
    summe_n_aktuell_in_zeitraum: Mapped[int] = mapped_column(sqlalchemy.Integer)
    # Timestamp of last zeroing of summe_n_aktuell_in_zeitraum
    letzte_nullung_stamp: Mapped[int] = mapped_column(sqlalchemy.Integer)
    
    def __repr__(self):
        return(
            f'<sqlKlasseTracker(Tracker_ID={self.tracker_id},\
                letzter_job_zeit={self.letzter_job_zeit},\
                letzter_job_zeit_stamp={self.letzter_job_zeit_stamp},\
                summe_n_aktuell_in_zeitraum={self.summe_n_aktuell_in_zeitraum},\
                letzte_nullung_stamp={self.letzte_nullung_stamp},)>'
            ) 
