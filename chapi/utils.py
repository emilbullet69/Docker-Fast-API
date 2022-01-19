import sys
from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger

from chapi.models import InsertRequest, AggregateReq, UpdateRequest


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


def user_input_to_df(user_input: InsertRequest) -> pd.DataFrame:
    """
    Transforms user input into a dataframe that can be easily appended to the existing table
    Args:
        user_input: Create Request

    Returns:
        Pandas dataframe that is matching the table structure.
    """
    data_to_add = pd.DataFrame(user_input).transpose()
    data_to_add.columns = \
        "dt,AverageTemperature,AverageTemperatureUncertainty,City,Country,Latitude,Longitude".split(",")
    data_to_add.drop(data_to_add.index[0], inplace=True)
    return data_to_add


def aggregate_data(df: pd.DataFrame,
                   job_id: str,
                   user_input: AggregateReq) -> Dict:
    """
    Getting the maximum monthly average temperature for each unique city within the time range
     but returning the top demanded
    Args:
        df: Whole time range data
        job_id: X-Request-ID
        user_input: Aggregate request

    Returns:

    """
    unique_places = df.loc[:, ["Latitude", "Longitude"]].drop_duplicates().values.tolist()
    unique_places_max_temp = []
    for unique_place in unique_places:
        sub_df = df.loc[(df["Latitude"] == unique_place[0]) & (df["Longitude"] == unique_place[1])]
        sub_df = sub_df.sort_values("AverageTemperature", ascending=False).head(1)
        unique_places_max_temp.append(sub_df)
    max_df = pd.concat(unique_places_max_temp)
    max_df = max_df.sort_values("AverageTemperature", ascending=False).head(user_input.top).reset_index(drop=True)
    suspect = max_df.to_dict("index")
    logger.success(f"{job_id} | Top {user_input.top} AverageTemperature: {suspect}")
    return suspect


def transform_optional_user_input(user_input: UpdateRequest) -> str:
    """
    Transforming optional user input to a single string that can be used in the update query
    Args:
        user_input: Update Request

    Returns:
        Empty string or value assigning query snippet
    """
    string_list = []
    if isinstance(user_input.avg_temp, float):
        string_list.append(f"`AverageTemperature` = {user_input.avg_temp}")
    if isinstance(user_input.avg_unc, float):
        string_list.append(f"`AverageTemperatureUncertainty` = {user_input.avg_unc}")
    update_string = " AND ".join(string_list)
    return update_string
