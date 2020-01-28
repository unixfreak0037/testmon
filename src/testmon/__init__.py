import asyncio
from datetime import datetime, timedelta
import os
import re
from typing import Union

import aioredis
from fastapi import FastAPI
from pydantic import BaseModel, validator


REDIS_URL = os.environ.get('REDIS_URL')


class MonitorIn(BaseModel):
    app_id: str
    action: str
    duration: Union[int, None] = None

    @validator('app_id')
    def must_be_alpha_numeric(cls, v):
        if re.search('[^0-9a-zA-Z]+', v):
            raise ValueError("app_id can only contain alpha-numeric characters")
        return v

    @validator('action')
    def must_be_allowed_action(cls, v, values, **kwargs):
        if v.lower() not in {'start', 'stop'}:
            raise ValueError("action must be 'start' or 'stop'")
        return v


async def kv_set(key, value):
    redis = await aioredis.create_redis_pool(f'redis://{REDIS_URL}')
    await redis.set(key, value)
    redis.close()
    await redis.wait_closed()


async def kv_get(key):
    redis = await aioredis.create_redis_pool(f'redis://{REDIS_URL}')
    result = await redis.get(key)
    redis.close()
    await redis.wait_closed()
    return result


class MonitorOut(BaseModel):
    app_id: str
    action: str
    duration: Union[int, None] = None
    status: str


app = FastAPI()


@app.get('/testmon/now')
async def now():
    now = datetime.now()
    return {
        "status": "alive",
        "now": now.ctime(),
    }


@app.post('/testmon/monitor/', response_model=MonitorOut)
async def monitor_endpoint(monitor_in: MonitorIn):
    now = datetime.now()
    if monitor_in.action.lower() == 'start':
        if monitor_in.duration is None:
            return {
                'status': "duration must be set when action is 'start'",
                **monitor_in.dict(),
            }
        value = (now + timedelta(seconds=monitor_in.duration)).ctime()
        await kv_set(monitor_in.app_id, value)
        return {
            'status': f"monitor started at {value}",
            **monitor_in.dict(),
        }
    if monitor_in.action.lower() == 'stop':
        result = await kv_get(monitor_in.app_id)

        if not isinstance(result, str):
            result = result.decode('utf-8')

        cutoff_time = datetime.strptime(result, '%c')
        if cutoff_time < now:
            overtime = (now - cutoff_time).total_seconds()
            return {
                'status': f"you're late by {str(overtime)} seconds",
                **monitor_in.dict(),
            }
        time_to_spare = (cutoff_time - now).total_seconds()
        return {
            'status': f"you are on time with {str(time_to_spare)} seconds to spare",
            **monitor_in.dict(),
        }
