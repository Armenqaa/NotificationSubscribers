import os
import motor.motor_asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(
    os.environ['MONGODB_HOST'],
    int(os.environ['MONGODB_PORT']),
    username=os.environ['MONGODB_USER'],
    password=os.environ['MONGODB_PASSWORD'],
)
db = client[os.environ['MONGODB_DATABASE']]


class MailType(str, Enum):
    tg = 'telegram'
    email = 'email'


class SubscriberModel(BaseModel):
    type: MailType
    address: str


class NotificationSubscribersModel(BaseModel):
    type_of_notification: str
    name_of_notification: str
    subscribers: list[SubscriberModel]


@app.get('/')
async def root():
    return {'message': 'Hello from subs service'}


@app.post('/insert')
async def insert(notification_subscribers: NotificationSubscribersModel):
    res = await db['notification_subscribers'].insert_one(notification_subscribers.dict())
    return {'id': f'{res.inserted_id}'}