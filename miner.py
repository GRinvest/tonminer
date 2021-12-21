import asyncio
import pathlib
from decimal import Decimal

from loguru import logger

from data import State
import random

FILE_BOC = "/tmp/mined.boc"
from time import time

class LiteClient:

    def __init__(self) -> None:
        pass

    async def run(self, cmd: str, timeout: int = 2) -> None:
        args = ['--global-config', State.args.сonfig,
                "--verbosity", "0", "--cmd", cmd]
        process = await asyncio.create_subprocess_exec(State.args.lite_client, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        try:
            await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.exceptions.TimeoutError:
            logger.debug(f"Command {cmd} timed out")
        except Exception as e:
            logger.error(f"Lite Client Exception {e}")
            raise Exception
        finally:
            try:
                process.kill()
            except OSError:
                pass


class Miner:

    def __init__(self, lite_client: object, gpu_id: str) -> None:
        self.app_path = State.args.miner
        self.lite_client = lite_client
        self.gpu_id = gpu_id

    async def run(self, args) -> None:
        process = await asyncio.create_subprocess_exec(self.app_path, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        State.process.append(process)
        try:
            stdout, _ = await process.communicate()
        except Exception as err:
            logger.error(f"Miner run failed: {err}")
            raise Exception
        else:
            await self.__distribution(stdout.decode())
        finally:
            State.process.remove(process)

    async def __distribution(self, data: str) -> None:
        if 'FOUND!' in data:
            await self.__submit(data)
        elif 'hashes computed' in data:
            await self.__rest_output(data)

    async def __rest_output(self, data: str) -> None:
        start = data.rfind('hashes computed:')
        end = data.find(']', start)
        State.msg.update({self.gpu_id: f"  {data[start:end]}"})

    async def __submit(self, data: str) -> None:
        await self.lite_client.run("sendfile " + FILE_BOC, 30)
        start = data.find('FOUND!')
        end = data.find('[', start)
        msg = data[start:end-1]
        msg = msg.replace('\n', ' ')
        logger.success('SOLUTION ' + msg)


async def task_miner(lite_client: object, gpu_id: str) -> None:
    logger.level("GPU " + gpu_id, no=60)
    logger.log("GPU " + gpu_id,
               '  Launched successfully, wait for initialization...')
    miner = Miner(lite_client, gpu_id)
    timer = '20'
    
    while True:
        if State.job.get('seed', False):
            expired = int(time()) + random.randint(10,1000)
            h = hex(expired).split('x')[-1]
            State.exnonce.update({gpu_id: h})
            await miner.run([
                '-vv', '-g', gpu_id, '-F', State.args.boost, '-t', timer, '-e', str(expired),
                State.args.wallet,
                str(State.job['seed']),
                str(State.job['complexity']),
                str(State.job['iterations']),
                State.job['giver'],
                FILE_BOC
            ])
            timer = '43200'
        else:
            await asyncio.sleep(1)


async def task_statistic_miner() -> None:
    while True:
        if len(State.msg.keys()):
            logger.info(
                "   -------------------------------------------------------------------------------------------------------")
            list_keys = list(int(i) for i in State.msg.keys())
            list_keys.sort()
            list_hr = []
            for i in list_keys:
                s = str(i)
                data = State.msg[s]
                logger.log(f"GPU {s}", f"  Extranonce: {State.exnonce[s]},{data}")
                start = data.rfind(': ')
                end = data.rfind(' M', start)
                try:
                    hr = Decimal(data[start+2:end])
                except Exception as e:
                    logger.error(f"Error decoding {e}")
                else:
                    list_hr.append(hr)
            if len(list_hr):
                logger.info(
                    f"   Total average hashrate: {sum(list_hr)} Mhash/s")
            await asyncio.sleep(30)
        else:
            await asyncio.sleep(2)
