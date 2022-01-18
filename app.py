from uvicorn import run
from chapi import api_source


app = api_source.app

if __name__ == "__main__":
    run(app, host="localhost", port=8000)
