import asyncio
import pathlib
import random
from decimal import Decimal
from time import time

from loguru import logger

from data import State

PATH_FILE_BOC = "/var/log/"
FILE_BOC = "/var/log/mined.boc"


class LiteClient:
    STATE_INDEX = 0

    async def run(self, cmd, timeout=0):
        if timeout == 0:
            timeout = 5
        while True:
            args = ['--global-config', State.args.сonfig,
                    "--verbosity", "0", '-i', str(LiteClient.STATE_INDEX), "--cmd", cmd]
            process = await asyncio.create_subprocess_exec(State.args.liteclient, *args, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.exceptions.TimeoutError:
                logger.warning(f"Command {cmd} timed out: {timeout} seconds")
                if LiteClient.STATE_INDEX > 8:
                    LiteClient.STATE_INDEX = 0
                else:
                    LiteClient.STATE_INDEX += 1
                if timeout <= 30:
                    timeout += 1
                continue
            else:
                if stderr:
                    logger.error(f"Error lite-client: {stderr.decode()}")
                    timeout = 5
                    await asyncio.sleep(3)
                    continue
                else:
                    return stdout.decode()
            finally:
                try:
                    process.terminate()
                except OSError:
                    pass


class Miner:

    def __init__(self, lite_client: object, gpu_id: str) -> None:
        self.app_path = State.args.miner
        self.lite_client = lite_client
        self.gpu_id = gpu_id

    async def run(self, args) -> None:
        process = await asyncio.create_subprocess_exec(self.app_path, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        if State.args.benchmark is False:
            State.process.append(process)
        try:
            stdout, _ = await process.communicate()
        except Exception as err:
            logger.error(f"Miner run failed: {err}")
            raise Exception
        else:
            if State.args.benchmark:
                await self.__save_benchmark(stdout.decode())
            else:
                await self.__distribution(stdout.decode())
        finally:
            if State.args.benchmark is False:
                State.process.remove(process)

    async def __save_benchmark(self, data: str) -> None:
        start = data.rfind('best boost factor:')
        end = data.find('[', start)
        boost_factor = int(data[start:end-1].split()[3])
        State.benchmark.update({self.gpu_id: boost_factor})
        State.msg.update({self.gpu_id: boost_factor})

    async def __distribution(self, data: str) -> None:
        if 'FOUND!' in data:
            await self.__submit(data)
        elif 'hashes computed' in data:
            await self.__rest_output(data)

    async def __rest_output(self, data: str) -> None:
        start = data.rfind('hashes computed:')
        end = data.find(']', start)
        State.msg.update({self.gpu_id: data[start:end]})

    async def __submit(self, data: str) -> None:
        import os
        logger.success('Yep!')
        await self.lite_client.run('last')
        await self.lite_client.run("sendfile " + FILE_BOC)
        start = data.find('FOUND!')
        end = data.find('[', start)
        msg = data[start:end-1]
        msg = msg.replace('\n', ' ')
        logger.success('SOLUTION ' + msg)
        file_oldname = os.path.join(PATH_FILE_BOC, "mined.boc")
        file_newname_newfile = os.path.join(
            PATH_FILE_BOC, f"mined_{self.gpu_id}_{int(time())}.boc")
        os.rename(file_oldname, file_newname_newfile)


async def task_miner(lite_client: object, gpu_id: str) -> None:
    logger.level("GPU " + gpu_id, no=60)
    logger.log("GPU " + gpu_id,
               '  Launched successfully, wait for initialization...')
    miner = Miner(lite_client, gpu_id)
    timer = '20'

    while True:
        if State.job.get('seed', False):
            expired = int(time()) + 800
            await miner.run([
                '-vv', '-g', gpu_id, '-F', State.args.boost, '-t', timer, '-e', str(
                    expired),
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
            if State.args.benchmark:
                for i in list_keys:
                    s = str(i)
                    data = State.msg[s]
                    logger.log(f"GPU {s}", f"  Best Boost Factor: {data}")
                break
            else:
                list_hr = []
                for i in list_keys:
                    s = str(i)
                    data = State.msg[s]
                    logger.log(
                        f"GPU {s}", f"  {data}")
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


async def task_benchmark(lite_client: object, gpu_id: str) -> None:
    logger.level("GPU " + gpu_id, no=60)
    logger.log("GPU " + gpu_id,
               '  Launched benchmark, please wait benchmarks...')
    miner = Miner(lite_client, gpu_id)
    while True:
        if State.job.get('seed', False):
            await miner.run([
                '-vv', '-B', '-g', gpu_id, '-t', '180',
                State.args.wallet,
                str(State.job['seed']),
                str(State.job['complexity']),
                str(State.job['iterations'])
            ])
            logger.log("GPU " + gpu_id, '  Benchmark complited')
            break
        else:
            await asyncio.sleep(1)
