import aiohttp
import asyncio
import base64
import datetime
import json
import random
import re
import ssl
import time
import uuid
import websockets

from loguru import logger
import pyfiglet
from websockets_proxy import Proxy, proxy_connect

ONETIME_PROXY = 100
DELAY_INTERVAL = 1
MAX_RETRIES = 5
FILE_UID = "uid.txt"
FILE_PROXY = "proxy.txt"
USERAGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.2365.57",
]
HTTP_STATUS_CODES = {
    200: "OK",
}

logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format=(
        "<green>{time:DD/MM/YY HH:mm:ss}</green> | "
        "<level>{level:8} | {message}</level>"
    ),
    colorize=True
)

def print_header():
    cn = pyfiglet.figlet_format("小草脚本")
    print(cn)
    print("{╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗")
    print("{╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║")
    print("{─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║")
    print("{─╔╝╚╗║║─║║╔══╣║╔═╣╚═╝║║─║║")
    print("{╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║")
    print("{╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝")
    print("{我的gihub：github.com/Gzgod")
    print("{我的推特：推特雪糕战神@Hy78516012")
def read_uid_and_proxy():
    with open(FILE_UID, 'r') as file:
        uid_count = sum(1 for _ in file)
    with open(FILE_PROXY, 'r') as file:
        proxy_count = sum(1 for _ in file)
    return uid_count, proxy_count

def get_user_input():
    while True:
        inp = input("遇到特定失败时是否要移除代理 (yes/no)? ").strip().lower()
        if inp in ['yes', 'no']:
            return inp == 'yes'
        print("无效输入。请输入 'yes' 或 'no'。")

def truncate_userid(user_id):
    return f"{user_id[:3]}--{user_id[-3:]}"

def truncate_proxy(proxy):
    match = re.search(r'([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})|(?:\d{1,3}\.){3}\d{1,3})', proxy)
    return match.group(0) if match else '未定义'

def count_proxies():
    try:
        with open(FILE_PROXY, 'r') as file:
            return len(file.readlines())
    except FileNotFoundError:
        logger.error(f"文件 {FILE_PROXY} 未找到！")
        return 0

async def connect_to_wss(protocol_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, protocol_proxy))
    random_user_agent = random.choice(USERAGENTS)
    logger.info(f"UID: {truncate_userid(user_id)} | {node_type} | 生成设备ID: {device_id} | 代理: {truncate_proxy(protocol_proxy)}")

    has_received_action = False
    is_authenticated = False
    total_proxies = count_proxies()

    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {"User-Agent": random_user_agent}
            custom_headers["Origin"] = "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"  

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = random.choice(["wss://proxy2.wynd.network:4444", "wss://proxy2.wynd.network:4650"])
            server_hostname = uri.split("://")[1].split(":")[0]
            proxy = Proxy.from_url(protocol_proxy)

            async with proxy_connect(
                uri,
                proxy=proxy,
                ssl=ssl_context,
                server_hostname=server_hostname,
                extra_headers=custom_headers
            ) as websocket:
                logger.success(f"UID: {truncate_userid(user_id)} | {node_type} | 成功连接到WS | uri: {uri} | 头部信息: {custom_headers} | 设备ID: {device_id} | 代理: {truncate_proxy(protocol_proxy)} | 剩余代理数量: {total_proxies}")

        except Exception as e:
            logger.error(f"UID: {truncate_userid(user_id)} | {node_type} | 代理 {truncate_proxy(protocol_proxy)} 出现错误 错误原因： {str(e)} | 剩余代理数量: {total_proxies}")

async def main():
    user_ids = open(FILE_UID, 'r').read().splitlines()
    all_proxies = open(FILE_PROXY, 'r').read().splitlines()

    random.shuffle(all_proxies)
    proxy_allocation = {user_id: all_proxies[i * ONETIME_PROXY:(i + 1) * ONETIME_PROXY] for i, user_id in enumerate(user_ids)}

    tasks = {}
    retry_count = {}

    for user_id, proxies in proxy_allocation.items():
        logger.warning(f"UID: {truncate_userid(user_id)} | {node_type} | 使用的代理总数: {len(proxies)}")
        await asyncio.sleep(DELAY_INTERVAL)

    for user_id, proxies in proxy_allocation.items():
        for proxy in proxies:
            retry_count[(proxy, user_id)] = 0
            await asyncio.sleep(DELAY_INTERVAL)
            tasks[asyncio.create_task(connect_to_wss(proxy, user_id))] = (proxy, user_id)


if __name__ == '__main__':
    try:
        print_header()
        uid_count, proxy_count = read_uid_and_proxy()
        print(f"UID: {uid_count}. 来自 {FILE_UID}。")
        print(f"加载了 {proxy_count} 个代理。来自 {FILE_PROXY}。")
        print()

        remove_on_all_errors = get_user_input()
        print(f"您选择了: {'是' if remove_on_all_errors else '否'},\n")

        global node_type
        node_type = 'extension'
        print(f"使用默认节点类型: Extension。\n")

        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info(f"您终止了程序。\n")
