import sys
from pathlib import Path

import pandas as pd
from loguru import logger


def configure_logger() -> None:
    """
    Replacing at default logger by a loguru logger
    """
    logger.remove()
    logger.add("logs/chapi.log", level="DEBUG", rotation="1 day", retention="1 week")
    logger.add(sys.stdout, level="INFO")
    
    
def read_local_file(file_path: Path) -> pd.DataFrame:
    """
    Reads local .CSV file as Pandas Dataframe.

    :param file_path: Local file path.
    """
    return pd.read_csv(file_path)