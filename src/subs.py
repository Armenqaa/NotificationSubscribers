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


@app.get('/receive_subscribers')
async def show(name_of_notification: str):
    notification_subscribers = \
        await db['notification_subscribers'].find_one({'name_of_notification': name_of_notification})
    if notification_subscribers:
        return {'result': notification_subscribers["subscribers"]}
    else:
        return {'err': 'no such name'}


@app.put('/update_subscribers')
async def update(name_of_notification: str, subscribers: list[SubscriberModel]):
    query = {'name_of_notification': name_of_notification}
    to_update = await db['notification_subscribers'].find_one(query)
    if to_update:
        prepared_subscribers = [subscriber.dict() for subscriber in subscribers]
        updated_result = \
            await db['notification_subscribers'].update_one(query, {'$set': {'subscribers': prepared_subscribers}})
        return {'res': f'updated {updated_result.modified_count}'}
    return {'err': 'no such name'}


@app.put('/add_subscribers')
async def add(name_of_notification: str, subscribers: list[SubscriberModel]):
    query = {'name_of_notification': name_of_notification}
    to_update = await db['notification_subscribers'].find_one(query)
    if to_update:
        updated_subscribers = to_update['subscribers'] + [subscriber.dict() for subscriber in subscribers]
        updated_result = \
            await db['notification_subscribers'].update_one(query, {'$set': {'subscribers': updated_subscribers}})
        return {'res': f'updated {updated_result.modified_count}'}
    return {'err': 'no such name'}


@app.put('/delete_subscribers')
async def delete(name_of_notification: str, subscribers_to_delete: list[SubscriberModel]):
    query = {'name_of_notification': name_of_notification}
    to_update = await db['notification_subscribers'].find_one(query)
    if to_update:
        subscribers_to_delete = [subscriber.dict() for subscriber in subscribers_to_delete]
        updated_subscribers = \
            [subscriber for subscriber in to_update['subscribers'] if subscriber not in subscribers_to_delete]
        updated_result = \
            await db['notification_subscribers'].update_one(query, {'$set': {'subscribers': updated_subscribers}})
        return {'res': f'updated {updated_result.modified_count}'}
    return {'err': 'no such name'}
