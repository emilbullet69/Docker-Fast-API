===================================================
Challenege API
===================================================

.. start-inclusion-marker-do-not-remove
.. image:: https://img.shields.io/static/v1?label=style&message=black&color=black&style=for-the-badge
   :alt: Code Style: BLACK
   :target: https://github.com/psf/black


Fast API for minimal db interaction

Getting Started
################

1. Clone Repo
2. Install Docker
3. Install Docker, Docker-Compose
4. Make sure that docker daemon is configured and  running
5. Navigate to cloned repo folder
6. Download the static file from the link below:
 https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data?select=GlobalLandTemperaturesByCity.csv

7. Unzip it and put it into the :code:`temp_dir` in the project’s root
8. Run :code:`docker-compose up -d`
9. Wait until both containers are up and running, then visit http://localhost:8090/docs
10. Expand the needed endpoint > click on :code:`Try it out` button> Modify the request as you wish > Click :code:`Execute`

Here you can experiment with the functionality using a nice Swagger UI. Docu also available.

Important note!: The DB is empty. It is getting filled up during the container startup.

By default, the API is running in test mode, which means that the full data is not loaded. Only the first 30k elements.

If you want to query all the data just like as it would be in prod, you need to change :code:`trial_run` env variable to **0** in the **docker-compose.yml** file.
Then stop and delete the existing containers and do the step 8 again. Be aware, with full data loading, it might take a few minutes until the containers are up again.

Examples
###############

**3.a**

Request:

.. code-block::

  curl -X 'POST' \
  'http://localhost:8000/rest/city_temp/v1/monthly_avg' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "from_date": "2000-01-01",
  "till_date": "2022-01-17",
  "top": 1
  }'

Response:

.. code-block::

    Response Code: 200
    Response Headers:
        content-length: 216
        content-type: application/json
        date: Mon,17 Jan 2022 22:15:25 GMT
        server: uvicorn
        x-correlation-id: e6802a3d188e47f09d98a4088a550ae2
        x-processes-time: 151.6996
        x-request-id: f398f4ce9280411dbb836334d07c8460
    Response Body:
        "{\"0\": {\"dt\": \"2013-07-01\",
                  \"AverageTemperature\": 39.15600000000001,
                  \"AverageTemperatureUncertainty\": 0.37,
                  \"City\": \"Ahvaz\",
                  \"Country\": \"Iran\",
                  \"Latitude\": \"31.35N\",
                  \"Longitude\": \"49.01E\"
                 }
        }"

Some logs:

.. code-block::

    INFO:     Started server process [28476]
    INFO:     Waiting for application startup.
    2022-01-17 23:14:59.824 | SUCCESS  | chapi.api_source:startup:73 - Startup was successful.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
    2022-01-17 23:15:26.434 | INFO     | chapi.api_source:dispatch:36 -  56e71e4ef4084fa7b5debe21225d379e | /docs
    2022-01-17 23:15:26.435 | INFO     | chapi.api_source:dispatch:37 -  56e71e4ef4084fa7b5debe21225d379e | Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'cache-control': 'max-age=0', 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 'sec-ch-ua-mobile': '?0', 'upgrade-insecure-requests': '1', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'sec-fetch-site': 'none', 'sec-fetch-mode': 'navigate', 'sec-fetch-user': '?1', 'sec-fetch-dest': 'document', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7', 'cookie': 'Pycharm-86fccf8d=6887e30f-ed57-4489-8cb0-b5e9470638e0'})
    2022-01-17 23:15:26.435 | INFO     | chapi.api_source:dispatch:45 -  56e71e4ef4084fa7b5debe21225d379e | finished after 0.0002
    INFO:     127.0.0.1:60646 - "GET /docs HTTP/1.1" 200 OK
    2022-01-17 23:15:26.570 | INFO     | chapi.api_source:dispatch:36 -  6d84fef940484d67bc0e63a0fa03e270 | /openapi.json
    2022-01-17 23:15:26.570 | INFO     | chapi.api_source:dispatch:37 -  6d84fef940484d67bc0e63a0fa03e270 | Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 'accept': 'application/json,*/*', 'sec-ch-ua-mobile': '?0', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'http://localhost:8000/docs', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7', 'cookie': 'Pycharm-86fccf8d=6887e30f-ed57-4489-8cb0-b5e9470638e0'})
    2022-01-17 23:15:26.576 | INFO     | chapi.api_source:dispatch:45 -  6d84fef940484d67bc0e63a0fa03e270 | finished after 0.0060
    INFO:     127.0.0.1:60646 - "GET /openapi.json HTTP/1.1" 200 OK
    2022-01-17 23:16:13.727 | INFO     | chapi.api_source:dispatch:36 -  f398f4ce9280411dbb836334d07c8460 | /rest/city_temp/v1/monthly_avg
    2022-01-17 23:16:13.727 | INFO     | chapi.api_source:dispatch:37 -  f398f4ce9280411dbb836334d07c8460 | Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'content-length': '72', 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 'accept': 'application/json', 'sec-ch-ua-mobile': '?0', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'content-type': 'application/json', 'origin': 'http://localhost:8000', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'http://localhost:8000/docs', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7', 'cookie': 'Pycharm-86fccf8d=6887e30f-ed57-4489-8cb0-b5e9470638e0'})
    2022-01-17 23:16:13.727 | INFO     | chapi.api_source:get_period:224 - f398f4ce9280411dbb836334d07c8460 | Request all between 2000-01-01 and 2022-01-17
    2022-01-17 23:18:45.305 | SUCCESS  | chapi.api_source:aggregate_data:210 - f398f4ce9280411dbb836334d07c8460 | Top 1 AverageTemperature: {0: {'dt': datetime.date(2013, 7, 1), 'AverageTemperature': 39.15600000000001, 'AverageTemperatureUncertainty': 0.37, 'City': 'Ahvaz', 'Country': 'Iran', 'Latitude': '31.35N', 'Longitude': '49.01E'}}
    2022-01-17 23:18:45.428 | INFO     | chapi.api_source:dispatch:45 -  f398f4ce9280411dbb836334d07c8460 | finished after 151.6996
    INFO:     127.0.0.1:60647 - "POST /rest/city_temp/v1/monthly_avg HTTP/1.1" 200 OK

**3.b**

Request:

.. code-block::

  curl -X 'PUT' \
  'http://localhost:8000/rest/city_temp/v1/create_single' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "date": "2022-01-01",
  "city": "Ahvaz",
  "avg_temp": 39.25600000000001,
  "avg_unc": 0.37,
  "country": "Iran",
  "latitude": "31.35N",
  "longitude": "49.01E"
  }'

Response:

.. code-block::

    Response Code: 200
    Response Headers:
         content-length: 33
         content-type: application/json
         date: Mon,17 Jan 2022 22:56:24 GMT
         server: uvicorn
         x-correlation-id: 9e757c1222a54b1dbaaa9c2a037065bb
         x-processes-time: 0.0370
         x-request-id: fc8a3a7a2941430daf508b1e20370049
    Response Body:
        "{\"msg\": {\"0\": \"SUCCESS\"}}"

Some logs:

.. code-block::

    2022-01-17 23:56:25.151 | INFO     | chapi.api_source:dispatch:35 -  fc8a3a7a2941430daf508b1e20370049 | /rest/city_temp/v1/create_single
    2022-01-17 23:56:25.151 | INFO     | chapi.api_source:dispatch:36 -  fc8a3a7a2941430daf508b1e20370049 | Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'content-length': '167', 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 'accept': 'application/json', 'sec-ch-ua-mobile': '?0', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'content-type': 'application/json', 'origin': 'http://localhost:8000', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'http://localhost:8000/docs', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7', 'cookie': 'Pycharm-86fccf8d=6887e30f-ed57-4489-8cb0-b5e9470638e0'})
    2022-01-17 23:56:25.163 | INFO     | chapi.api_source:create_single:103 - fc8a3a7a2941430daf508b1e20370049 | Adding new entry to Global_Land_Temperatures_By_City table:            dt AverageTemperature  ... Latitude Longitude
    1  2022-01-01             39.256  ...   31.35N    49.01E

    [1 rows x 7 columns]
    2022-01-17 23:56:25.188 | SUCCESS  | chapi.api_source:create_single:105 - fc8a3a7a2941430daf508b1e20370049 | New entry was added to Global_Land_Temperatures_By_City table:            dt AverageTemperature  ... Latitude Longitude
    1  2022-01-01             39.256  ...   31.35N    49.01E

    [1 rows x 7 columns]
    2022-01-17 23:56:25.189 | INFO     | chapi.api_source:dispatch:44 -  fc8a3a7a2941430daf508b1e20370049 | finished after 0.0370
    INFO:     127.0.0.1:60762 - "PUT /rest/city_temp/v1/create_single HTTP/1.1" 200 OK

**3.c**

Request:

.. code-block::

  curl -X 'PUT' \
  'http://localhost:8000/rest/city_temp/v1/update_existing' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "date": "2013-07-01",
  "city": "Ahvaz",
  "avg_temp": 36.65600000000001,
  "avg_unc": 0.37
  }'

Response:

.. code-block::

    Response Code: 200
    Response Headers:
        content-length: 33
        content-type: application/json
        date: Mon,17 Jan 2022 23:19:36 GMT
        server: uvicorn
        x-correlation-id: 8a5d82819ec04164bf092a9ec8b6e5ff
        x-processes-time: 0.0140
        x-request-id: 9557af8996a14af98f1bd2ead324be21
    Response Body:
        "{\"msg\": {\"0\": \"SUCCESS\"}}"

Some logs:

.. code-block::

    2022-01-18 00:19:37.116 | INFO     | chapi.api_source:dispatch:35 -  9557af8996a14af98f1bd2ead324be21 | /rest/city_temp/v1/update_existing
    2022-01-18 00:19:37.116 | INFO     | chapi.api_source:dispatch:36 -  9557af8996a14af98f1bd2ead324be21 | Headers({'host': 'localhost:8000', 'connection': 'keep-alive', 'content-length': '97', 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 'accept': 'application/json', 'sec-ch-ua-mobile': '?0', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 'content-type': 'application/json', 'origin': 'http://localhost:8000', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'http://localhost:8000/docs', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7', 'cookie': 'Pycharm-86fccf8d=6887e30f-ed57-4489-8cb0-b5e9470638e0'})
    2022-01-18 00:19:37.129 | INFO     | chapi.api_source:update_entry:302 - 9557af8996a14af98f1bd2ead324be21 | Updated AverageTemperature and/or AverageTemperatureUncertainty for Ahvaz on 2013-07-01
    2022-01-18 00:19:37.130 | INFO     | chapi.api_source:dispatch:44 -  9557af8996a14af98f1bd2ead324be21 | finished after 0.0140
    INFO:     127.0.0.1:60832 - "PUT /rest/city_temp/v1/update_existing HTTP/1.1" 200 OK

Author
########

Emil

.. end-inclusion-marker-do-not-remove

Documentation
##############

http://localhost:8090/docs

Comments
#############

Challenges were mainly coming from my constant wish to make everything as if it would be a POC for production.

E.g: Shoud I use env variables for credentials, or a config.ini is enough.
Ideal would be a keepass api to retrieve passwords but that would require much more effort.

Decided to use README.rst instead of .md because restructured text can be easily pulled and used as docu in Confluence for example.

Another example is Django vs Flask vs Open API or whatever.
Django would be an overkill for such a small project.
I decided to go with Fast API, as it has the Swagger UI supported out of the box which is a minimalistic UI for user interaction.
Also it is lightweight and visualizing some docu related to endpoint usage.

Was hesitating if I should add connection pooling. Should have added it as there are no real down sides.

Wanted to use Selenium to download the static file on startup.
Just to make things one-click.
Decided not to do it as it wasn't one of the tasks, so could be implemented in next iterations.

Planned to add more user input validation and more meaningful response patterns.
E.g: Doing all the DB interaction using SqlAlchemy's ORM instead of plain SQL.
That would also eliminate the security risk of SQL injections.

Was thinking trough a concept for more detailed aggregation as not immediately noticed that all datapoints are not daily but monthly.

I know that it is much better to clarify stuff beforehand but, was mainly working on this stuff on Saturday and Sunday, so would not make much sense to wait till Monday for the answers. If that would go to prod, I could be quite annoying with all the questions.
Same applies for unit and integration tests.
All the specified tasks are completed. The existing code base is more than enough to make a decision regarding my coding skills.
Please let me know if you
expect me to write here extensive unit and integration tests. Otherwise I would skip it as this is just a coding challenge.

Overall I've spent on the whole challenge around 12 hours.
