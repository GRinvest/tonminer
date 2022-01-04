import argparse
import asyncio
import os
import pathlib
import sys

from loguru import logger
from pynvml import nvmlDeviceGetCount, nvmlInit

from app import main_tasks
from data import State

VERSION = "0.1.7"

BASE_DIR = pathlib.Path(__file__).parent


def init():
    if sys.platform == "linux" or sys.platform == "linux2":
        os.chdir(sys._MEIPASS)
        try:
            from pyadl import ADLManager
        except Exception as err:
            from pynvml import nvmlDeviceGetCount, nvmlInit, nvmlShutdown
            nvmlInit()
            State.gpu_count = nvmlDeviceGetCount()
            State.miner = BASE_DIR / "pow-miner-cuda"
            nvmlShutdown()
        else:
            State.gpu_count = len(ADLManager.getInstance().getDevices())
            State.miner = BASE_DIR / "pow-miner-opencl"
    elif sys.platform == "win32":
        from multiprocessing import freeze_support

        import wmi

        freeze_support()
        os.chdir(sys._MEIPASS)
        computer = wmi.WMI()
        gpu_info = computer.Win32_VideoController()
        State.gpu_count = len(gpu_info)
        if "AMD" in gpu_info[0].VideoProcessor:
            State.miner =  BASE_DIR / "pow-miner-opencl.exe"
        else:
            State.miner = BASE_DIR / "pow-miner-cuda.exe"

def init_logger():
    logger.remove()
    logger.add(sys.stderr, colorize=True,
               format="<green>{level}</green>:     <level>{message}</level>", level=State.args.logger.upper(), enqueue=True)
    logger.add("/var/log/tonminer-proxy.log", rotation="3 MB")

def createParser():

    parser = argparse.ArgumentParser(
        prog='tonminer-proxy',
        description="Miner Toncoin for ton-proxy",
        epilog='(c) GRinvest 2021. The author of the program, as always, assumes no responsibility for anything.',
        add_help=False
    )
    parent_group = parser.add_argument_group(title='Required Parameters')
    parent_group.add_argument(
        '-W',
        dest="wallet",
        metavar='your_wallet',
        help='Your toncoin wallet, not exchange (etc. EQA1VNu5w...)',
        required=True
    )
    parent_group = parser.add_argument_group(title='Parameters')
    path = BASE_DIR / "global.config.json"
    parent_group.add_argument(
        '-C',
        dest="config",
        default=path,
        metavar="config file",
        help=f'path global.config.json (default: {path})'
    )
    path = BASE_DIR / 'lite-client'
    parent_group.add_argument(
        '-L',
        dest="liteclient",
        default=path,
        metavar="lite-client",
        help=f'path lite-client (default: {path})'
    )
    parent_group.add_argument(
        '-M',
        dest="miner",
        default=State.miner,
        metavar="miner",
        help=f'path miner (default: {State.miner})'
    )
    parent_group.add_argument(
        '-H',
        dest="host",
        default="0.0.0.0",
        metavar='host',
        help='Host where the proxy is running (default: 0.0.0.0)'
    )
    parent_group.add_argument(
        '-P',
        dest="port",
        default=8080,
        metavar='port',
        help='The port on which the proxy is running (default: 8080)',
        type=int
    )
    parent_group.add_argument(
        '-F',
        dest="boost",
        default="64",
        metavar='boost-factor',
        help='1..65536, the multiplier for throughput, affects the number of hashes processed per iteration on the GPU (default: 64)'
    )
    parent_group.add_argument(
        '-B',
        dest="benchmark",
        action='store_true',
        default=False,
        help='Start benchmarking: Optimal Boost Factor (default: False)'
    )
    parser.add_argument('--help', '-h', action='help', help='This is help')
    parser.add_argument('--version', '-v', action='version',
                        help='Print version number', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-D', dest='logger', default='info',
                        help='logger (etc. info, debug, error) default: info')

    return parser


if __name__ == '__main__':
    init()
    parser = createParser()
    State.args = parser.parse_args()
    init_logger()
    try:
        asyncio.run(main_tasks())
    except KeyboardInterrupt:
        logger.warning("Close program Ctrl C")
    except Exception as e:
        logger.exception(e)
