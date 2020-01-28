"""Quick app for pipeline testing"""

__version__ = "0.1.0"

from datetime import datetime, timedelta
import os
import re
from typing import Union

import aioredis
from fastapi import FastAPI
from pydantic import BaseModel, validator  # pylint: disable=E0611


REDIS_URL = os.environ.get("REDIS_URL")


class MonitorIn(BaseModel):
    """Model for incoming body via monitor api"""

    app_id: str
    action: str
    duration: Union[int, None] = None

    @validator("app_id")
    def must_be_alpha_numeric(cls, value):  # pylint: disable=E0213,R0201
        """Make sure the app_id is alpha-numeric."""
        if re.search("[^0-9a-zA-Z]+", value):
            raise ValueError("app_id can only contain alpha-numeric characters")
        return value

    @validator("action")
    def must_be_allowed_action(cls, value):  # pylint: disable=E0213,R0201
        """Make sure action is start or stop"""
        if value.lower() not in {"start", "stop"}:
            raise ValueError("action must be 'start' or 'stop'")
        return value


async def kv_set(key, value):
    """Set redis key/value."""
    redis = await aioredis.create_redis_pool(f"redis://{REDIS_URL}")
    await redis.set(key, value)
    redis.close()
    await redis.wait_closed()


async def kv_get(key):
    """Return a redis value based on key."""
    redis = await aioredis.create_redis_pool(f"redis://{REDIS_URL}")
    result = await redis.get(key)
    redis.close()
    await redis.wait_closed()
    return result


class MonitorOut(BaseModel):  # pylint: disable=R0903
    """Model for respone bodies for monitor api."""

    app_id: str
    action: str
    duration: Union[int, None] = None
    status: str


app = FastAPI()  # pylint: disable=C0103


@app.get("/testmon/now")
async def now():
    """Return the current time."""
    _now = datetime.now()
    return {
        "status": "alive",
        "now": _now.ctime(),
    }


@app.post("/testmon/monitor/", response_model=MonitorOut)
async def monitor_endpoint(monitor_in: MonitorIn):
    """Start or stop a monitor."""
    _now = datetime.now()
    if monitor_in.action.lower() == "start":
        if monitor_in.duration is None:
            return {
                "status": "duration must be set when action is 'start'",
                **monitor_in.dict(),
            }
        value = (_now + timedelta(seconds=monitor_in.duration)).ctime()
        await kv_set(monitor_in.app_id, value)
        return {
            "status": f"monitor started at {value}",
            **monitor_in.dict(),
        }
    if monitor_in.action.lower() == "stop":
        result = await kv_get(monitor_in.app_id)

        if not isinstance(result, str):
            result = result.decode("utf-8")

        cutoff_time = datetime.strptime(result, "%c")
        if cutoff_time < _now:
            overtime = (_now - cutoff_time).total_seconds()
            return {
                "status": f"you're late by {str(overtime)} seconds",
                **monitor_in.dict(),
            }
        time_to_spare = (cutoff_time - _now).total_seconds()
        return {
            "status": f"you are on time with {str(time_to_spare)} seconds to spare",
            **monitor_in.dict(),
        }
