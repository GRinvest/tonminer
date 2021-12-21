import asyncio

from loguru import logger

from data import State
from miner import LiteClient, task_miner, task_statistic_miner
from ws import WebSocketClient


async def main_tasks():
    lite_client = LiteClient()
    State.msg = {}
    State.job = {}
    State.process = []
    tasks = [
        asyncio.create_task(WebSocketClient().run()),
        asyncio.create_task(task_statistic_miner())
    ]
    for i in range(State.gpu_count):
        tasks.append(asyncio.create_task(task_miner(lite_client, str(i))))
    err, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    logger.exception(err)
