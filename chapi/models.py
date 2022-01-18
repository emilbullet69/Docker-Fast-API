import datetime
from typing import Optional

from pydantic import BaseModel


class InsertRequest(BaseModel):
    """
    Data to be inserted in the DB as new entry.

    Examples:
        {
           "date": 2022-01-16,
           "avg_temp": 6.06800,
           "avg_unc": 1.73700,
           "city": "Aarhus",
           "country": "Denmark",
           "latitude": "57.05N",
           "longitude": "10.33E"
        }
    """
    date: datetime.date
    avg_temp: float
    avg_unc: float
    city: str
    country: str
    latitude: str
    longitude: str


class UpdateRequest(BaseModel):
    """
    Data to be updated.

    Examples:
        {
           "date": 2022-01-16,
           "city": "Aarhus"
           "avg_temp": 6.06800,
           "avg_unc": 1.73700
        }
    """
    date: datetime.date
    city: str
    avg_temp: Optional[float]
    avg_unc: Optional[float]


class AggregateReq(BaseModel):
    """
    Time frame and amount

    Examples:
        {
           "from_date": 2022-01-16,
           "till_date": 2022-01-16,
           "top": 3
        }
    """
    from_date: datetime.date = datetime.date.today()
    till_date: datetime.date = datetime.date.today()
    top: int = 1
    