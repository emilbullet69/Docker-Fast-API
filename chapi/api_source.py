import time
import json
from pathlib import Path
from typing import Dict

import pandas as pd
from loguru import logger
from fastapi import FastAPI, Response
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette_context import context, plugins
from starlette_context.middleware import ContextMiddleware


from chapi.config import define_config
from chapi.db_connector import DbConnector
from chapi.utils import configure_logger, read_local_file
from chapi.models import InsertRequest, UpdateRequest, AggregateReq


directory = Path(__file__).parent
TEMP_DIR = directory.parent.joinpath("temp_dir")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
CONFIG = define_config()
DB_CONNECTOR = DbConnector(CONFIG)


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log specific info.
    """
    async def dispatch(self, request: Request, call_next):
        x_requests_id = context.data["X-Request-ID"]
        logger.info(f" {x_requests_id} | {request.url.path} ")
        logger.info(f" {x_requests_id} | {request.headers} ")
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (time.perf_counter() - start_time)
        formatted_process_time = f'{process_time:0.4f}'
        response.headers["X-Processes-Time"] = formatted_process_time
        logger.info(f" {x_requests_id} | finished after {formatted_process_time}")
        return response


middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(LoggerMiddleware),
]

app = FastAPI(title="Challenge API", version="Alpha", middleware=middleware)


@app.on_event("startup")
async def startup():
    """
    Run the necessary setup before start of the service. E.g: fill up DB with data
    """
    configure_logger()

    file_path = TEMP_DIR.joinpath("GlobalLandTemperaturesByCity.csv")
    static_data = read_local_file(file_path)
    await create_table(static_data.head(1))
    DB_CONNECTOR.df_to_db(static_data, "Global_Land_Temperatures_By_City", "append")

    logger.success("Startup was successful.")


@app.put("/rest/city_temp/v1/create_single")
def create_single(user_input: InsertRequest, response: Response) -> str:
    """
        Adds new DB entry using data provided by the user

        Examples:

            request:
            {
                "date": 2022-01-16,
                "avg_temp": 6.06800,
                "avg_unc": 1.73700,
                "city": "Aarhus",
                "country": "Denmark",
                "latitude": "57.05N",
                "longitude": "10.33E"
            }

            return:
             {
                "msg": "SUCCESS"
            }
        """
    job_id = context.data["X-Request-ID"]
    response.headers["X-Request-Id"] = job_id

    data_to_add = user_input_to_df(user_input)

    try:
        logger.info(f'{job_id} | Adding new entry to Global_Land_Temperatures_By_City table: {data_to_add}')
        DB_CONNECTOR.df_to_db(data_to_add, "Global_Land_Temperatures_By_City", "append")
        logger.success(f'{job_id} | New entry was added to Global_Land_Temperatures_By_City table: {data_to_add}')
        res = json.dumps({"msg": {0: "SUCCESS"}})
    except Exception as e:
        logger.error(f'{job_id} | Error: {e}')
        response.status_code = 400
        res = json.dumps({"msg": {0: f"{e}"}})
    return res


@app.put("/rest/city_temp/v1/update_existing")
def update_existing(user_input: UpdateRequest, response: Response) -> str:
    """
        Updates an existing entry in the DB using data provided by the user

        Examples:

            request:
            {
                "date": 2022-01-16,
                "city": "Aarhus",
                "avg_temp": 6.06800,
                "avg_unc": 1.73700,
            }

            return:
             {
                "msg": "SUCCESS"
            }
        """
    job_id = context.data["X-Request-ID"]
    response.headers["X-Request-Id"] = job_id

    update_string = transform_optional_user_input(user_input)
    if update_string:
        random_city = get_city(user_input)
        if random_city.empty:
            res = define_missing_entry_response(job_id, response, user_input)
        else:
            res = update_entry(job_id, response, user_input, update_string)
    else:
        logger.warning(f'{job_id} | At least avg_temp or avg_unc should be given or both')
        response.status_code = 400
        res = json.dumps({"msg": {0: "At least avg_temp or avg_unc should be given or both"}})
    return res


@app.post("/rest/city_temp/v1/monthly_top_n")
def sort_data(user_input: AggregateReq, response: Response) -> str:
    """
        Returns the top N cities that have the highest monthly AverageTemperature in
        a specified time range.

        Examples:

            request:
            {
               "from_date": 2000-01-11,
               "till_date": 2022-01-17,
               "top": 1
            }

            return:
            {
                "0":
                    {
                        "dt": "2013-07-01",
                        "AverageTemperature": 39.15600000000001,
                        "AverageTemperatureUncertainty": 0.37,
                        "City": "Ahvaz",
                        "Country": "Iran",
                        "Latitude": "31.35N",
                        "Longitude": "49.01E"
                    }
            }
        """
    job_id = context.data["X-Request-ID"]
    response.headers["X-Request-Id"] = job_id

    try:
        df = get_period(job_id, user_input)
        suspect = aggregate_data(df, job_id, user_input)
        res = json.dumps(suspect, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error(f'{job_id} | Error: {e}')
        response.status_code = 400
        res = json.dumps({"msg": {0: f"{e}"}})
    return res


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
        sub_df = df.loc[(df['Latitude'] == unique_place[0]) & (df['Longitude'] == unique_place[1])]
        sub_df = sub_df.sort_values('AverageTemperature', ascending=False).head(1)
        unique_places_max_temp.append(sub_df)
    max_df = pd.concat(unique_places_max_temp)
    max_df = max_df.sort_values('AverageTemperature', ascending=False).head(user_input.top).reset_index(drop=True)
    suspect = max_df.to_dict("index")
    logger.success(f'{job_id} | Top {user_input.top} AverageTemperature: {suspect}')
    return suspect


def get_period(job_id: str, user_input: AggregateReq) -> pd.DataFrame:
    """
    Query all entries for the whole period
    Args:
        job_id: X-Request-ID
        user_input: Aggregate request

    Returns:
        PD dataframe with queried data
    """
    logger.info(f'{job_id} | Request all between {user_input.from_date} and {user_input.till_date}')
    query = f"""SELECT * 
                FROM {CONFIG.schema}.Global_Land_Temperatures_By_City
                WHERE dt 
                BETWEEN '{user_input.from_date}' AND '{user_input.till_date}';"""
    df = DB_CONNECTOR.sql_query_to_pandas(query)
    return df


async def create_table(dummy_static_data: pd.DataFrame) -> None:
    """
    Creating SQL table and adding primary keys before loading the data
    Args:
        dummy_static_data: DF head as reference for table creation
    """
    DB_CONNECTOR.df_to_db(dummy_static_data, "Global_Land_Temperatures_By_City")
    DB_CONNECTOR.engine.execute(f"ALTER TABLE {CONFIG.schema}.Global_Land_Temperatures_By_City "
                                f"MODIFY dt DATE;")
    DB_CONNECTOR.engine.execute(f"ALTER TABLE {CONFIG.schema}.Global_Land_Temperatures_By_City "
                                f"MODIFY Latitude CHAR(8);")
    DB_CONNECTOR.engine.execute(f"ALTER TABLE {CONFIG.schema}.Global_Land_Temperatures_By_City "
                                f"MODIFY Longitude CHAR(8);")
    DB_CONNECTOR.engine.execute(f"ALTER TABLE {CONFIG.schema}.Global_Land_Temperatures_By_City "
                                f"ADD KEY (dt,Latitude,Longitude);")
    DB_CONNECTOR.engine.execute(f"TRUNCATE TABLE {CONFIG.schema}.Global_Land_Temperatures_By_City;")


def define_missing_entry_response(job_id: str,
                                  response: Response,
                                  user_input: UpdateRequest) -> str:
    """
    Case when someone is trying to modify a not existing entry
    """
    response.status_code = 202
    comment = f"Entry not exist: {user_input.city} on {user_input.date}"
    logger.warning(f'{job_id} | {comment}')
    res = json.dumps({"msg": {0: f"No entry to update where city name is {user_input.city} "
                                 f"and date is {user_input.date}. "
                                 f"Use /rest/city_temp/v1/create_single endpoint to create one"}})
    return res


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


def update_entry(job_id: str,
                 response: Response,
                 user_input: UpdateRequest,
                 update_string: str) -> str:
    """
    Updating AverageTemperature and/or AverageTemperatureUncertainty of a single City on a certain date
    Args:
        job_id: X-request ID
        response: HTTP response
        user_input: Update Request
        update_string: SQL snippet

    Returns:

    """
    try:
        u_query = f"""UPDATE {CONFIG.schema}.Global_Land_Temperatures_By_City
                      SET {update_string}
                      WHERE `dt` = '{user_input.date}'
                      AND `City` = '{user_input.city}'
                      LIMIT 1;"""
        DB_CONNECTOR.engine.execute(u_query)
        logger.info(f'''{job_id} | Updated AverageTemperature and/or AverageTemperatureUncertainty 
                    for {user_input.city} on {user_input.date}''')
        res = json.dumps({"msg": {0: "SUCCESS"}})
    except Exception as e:
        logger.error(f'{job_id} | Error: {e}')
        response.status_code = 400
        res = json.dumps({"msg": {0: f"{e}"}})
    return res


def get_city(user_input: UpdateRequest) -> pd.DataFrame:
    """
        Querying an entry that has matching city name and date
    Args:
        user_input: Update Request

    Returns:
        Matching city name as pandas df
    """
    query = f"""SELECT `City` 
                FROM {CONFIG.schema}.Global_Land_Temperatures_By_City
                WHERE `dt` = '{user_input.date}'
                AND `City` = '{user_input.city}'
                LIMIT 1;"""
    random_city = DB_CONNECTOR.sql_query_to_pandas(query)
    return random_city


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
