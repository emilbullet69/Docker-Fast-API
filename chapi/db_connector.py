import sqlalchemy as db
import pandas as pd
from loguru import logger

from chapi.config import Config


class DbConnector(object):
    def __init__(self, config: Config):
        """
        Class to query database via lazy connection over the engine.

        :param config: Config Dataclass instance
        """
        self.engine = db.create_engine(config.uri)
        self.trial_run = config.trial_run

    def df_to_db(self,
                 df: pd.DataFrame,
                 table_name: str,
                 if_exists: str = "replace") -> None:
        """
        Loads Pandas DF into an SQL table.

        :param df: Pandas Dataframe.
        :param table_name: Name of the new table
        :param if_exists: What to do if the table exists (fail, replace, append)
        """
        if self.trial_run:
            df = df.head(n=30000)
            logger.warning("The API is running in test mode. BD populated only by the first 30 rows. "
                           "To disable the limitation, change trial_run env variable to False before "
                           "running a new container")
        df.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False, chunksize=20000)
        
    def sql_query_to_pandas(self, query: str) -> pd.DataFrame:
        """
        Querying data as Pandas dataframe
        
        :param query: SQL query
        :return: result in DF representation
        """
        df = pd.read_sql_query(db.text(query), self.engine)
        return df
