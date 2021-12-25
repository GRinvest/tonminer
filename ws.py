import asyncio
import json

from aiohttp import (ClientConnectorError, ClientSession,
                     ServerDisconnectedError, WSMsgType)
from loguru import logger

from data import State


class WebSocketClient:

    def __init__(self):
        self.ws_connect = None

    async def __fetch(self):
        try:
            async with ClientSession() as session:
                async with session.ws_connect(f'ws://{State.args.host}:{State.args.port}/ws/connect', heartbeat=5) as ws:
                    self.ws_connect = ws
                    logger.log(
                        'PROXY', f"  Connected host {State.args.host}:{State.args.port} Ok, Your wallet adress for reward: {State.args.wallet}")
                    async for msg in ws:
                        if msg.type == WSMsgType.TEXT:
                            msg_json = json.loads(msg.data)
                            if msg_json['ok']:
                                State.reconnect = 0
                                await self.job_creation(msg_json['data'])
                            else:
                                logger.error(
                                    f"Error fetch new job {msg_json['data']}")
                        elif msg.type == WSMsgType.ERROR:
                            logger.error(f"Error fetch {msg.data}")
        except ClientConnectorError as err:
            logger.error(
                f"Proxy server Connection Error {err} Reconnection after 10 sec...")
        except ServerDisconnectedError as err:
            logger.error(f"Error fetch ServerDisconnectedError {err}")
        except Exception as err:
            logger.exception(f"Error fetch Exception {err}")
        finally:
            if State.args.benchmark is False:
                logger.log(
                    'PROXY', f'  Disconnect host {State.args.host}:{State.args.port} Reconnection: {State.reconnect}')
                if State.reconnect > 10:
                    State.msg = {}
                    State.job = {}
                    if len(State.process):
                        for proc in State.process:
                            try:
                                proc.terminate()
                            except OSError:
                                pass

    async def run(self):
        logger.level("NEW JOB", no=60)
        logger.level("PROXY", no=60, color="<yellow>")
        while True:
            await self.__fetch()
            if State.args.benchmark:
                break
            else:
                State.reconnect += 1
                await asyncio.sleep(10)

    async def job_creation(self, data):
        if State.args.benchmark:
            State.job = data
            await self.ws_connect.close()
        else:
            try:
                logger.log(
                    "NEW JOB", f"seed: {data['seed']}, Giver: {data['giver']}")
            except KeyError:
                pass
            else:
                State.job = data
                if len(State.process):
                    for proc in State.process:
                        try:
                            proc.terminate()
                        except OSError:
                            pass
