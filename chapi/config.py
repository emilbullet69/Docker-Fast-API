import dataclasses
import os


@dataclasses.dataclass
class Config:
    user: str
    passwd: str
    schema: str
    host: str
    trial_run: int

    def __post_init__(self):
        self.uri = f"mysql+pymysql://{self.user}:{self.passwd}@{self.host}:3306/{self.schema}?local_infile=1"


def define_config() -> Config:
    """Initializes the DB configuration

    Returns:
        Config data class instance
    """
    user = os.environ.get("db_user")
    passwd = os.environ.get("db_pass")
    schema = os.environ.get("db_schema")
    host = os.environ.get("db_host")
    trial_run = int(os.environ.get("trial_run"))

    config = Config(
        user=user,
        passwd=passwd,
        schema=schema,
        host=host,
        trial_run=trial_run
    )
    return config
