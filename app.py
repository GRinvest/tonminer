import asyncio

from loguru import logger

from data import State
from miner import LiteClient, task_benchmark, task_miner, task_statistic_miner
from ws import WebSocketClient


def save_benchmark():
    import json
    with open('/home/user/gpu_benchmark.json', 'w', encoding='utf-8') as f:
        json.dump(State.benchmark, f, ensure_ascii=False, indent=4)


async def main_tasks():
    lite_client = LiteClient()
    State.msg = {}
    State.job = {}
    State.process = []
    State.exnonce = {}
    State.reconnect = 0
    tasks = [
        asyncio.create_task(WebSocketClient().run()),
        asyncio.create_task(task_statistic_miner())
    ]
    if State.args.benchmark:
        State.benchmark = {}
        for i in range(State.gpu_count):
            tasks.append(asyncio.create_task(
                task_benchmark(lite_client, str(i))))
        res = await asyncio.gather(*tasks)
        save_benchmark()
    else:
        for i in range(State.gpu_count):
            tasks.append(asyncio.create_task(task_miner(lite_client, str(i))))
        err, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        logger.exception(err)
