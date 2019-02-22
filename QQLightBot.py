#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2019年2月21日
@author: Irony
@site: https://pyqt5.com https://github.com/892768447
@email: 892768447@qq.com
@file: QQLightBot
@description: 机器人WS客户端
"""
from argparse import ArgumentParser
import asyncio
import json
import logging
import sys
from typing import List

import aiohttp


__Author__ = 'Irony'
__Copyright__ = 'Copyright (c) 2019'


class MsgDict(dict):

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        if key in self:
            value = self[key]
            if isinstance(value, dict):
                value = MsgDict(value)
            return value
        return None


class ApiProtocol:

    @classmethod
    def message(cls, type=0, group='', qq='', content='', msgid=''):  # @ReservedAssignment
        """事件.收到消息
        :param cls:
        :param type:        1=好友消息、2=群消息、3=群临时消息、4=讨论组消息、5=讨论组临时消息、6=QQ临时消息
        :param group:       类型为1或6的时候，此参数为空字符串，其余情况下为群号或讨论组号
        :param qq:          消息来源QQ号，"10000"都是来自系统的消息（比如某人被禁言或某人撤回消息等）
        :param content:     消息内容
        :param msgid:       消息id，撤回消息的时候会用到，群消息会存在，其余情况下为空
        """


async def _run(args, entity):
    logger = logging.getLogger('QQLightBot')
    # 创建session
    async with aiohttp.client.ClientSession(timeout=aiohttp.client.ClientTimeout(total=60)) as session:
        logger.info(
            'connect to ws://{0}:{1}{2}'.format(args.hostname, args.port, args.path))
        # 连接服务器
        async with session.ws_connect('ws://{0}:{1}{2}'.format(args.hostname, args.port, args.path)) as ws:
            logger.info('connect succeed')
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    logger.debug('received data: {}'.format(msg.data))
                    try:
                        # 解析json数据
                        msg = MsgDict(json.loads(msg))
                        if msg.event != None:
                            # 调用函数并传递参数
                            try:
                                getattr(entity, msg.event)(**msg.params)
                            except Exception as e:
                                logger.exception(e)
                    except Exception as e:
                        logger.exception(e)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error('connection lost')
                    break


def main(argv: List[str]) -> None:
    arg_parser = ArgumentParser(
        description='QQLightBot WebSocket Client',
        prog='QQLightBot'
    )
    # 连接地址
    arg_parser.add_argument(
        '-H', '--hostname',
        help='connect to server on (default: %(default)r)',
        default='127.0.0.1'
    )
    # 端口
    arg_parser.add_argument(
        '-P', '--port',
        help='connect port to server on (default: %(default)r)',
        type=int,
        default='49632'
    )
    # 路径
    arg_parser.add_argument(
        '-U', '--path',
        help='connect to server url on (default: %(default)r)',
        default='/'
    )
    # 日志级别
    arg_parser.add_argument(
        '-L', '--level',
        help='log level (default: %(default)r), all is: DEBUG INFO WARN ERROR',
        default='DEBUG'
    )

    # 解析命令行参数
    args, _ = arg_parser.parse_known_args(argv)

    # 配置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s %(module)s:%(funcName)s:%(lineno)s] %(levelname)-8s %(message)s')
    logger = logging.getLogger('QQLightBot')
    logger.setLevel(getattr(logging, args.level) if args.level in (
        'DEBUG', 'INFO', 'WARN', 'ERROR') else logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 开始连接
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run(args))


if __name__ == '__main__':
    main(sys.argv[1:])
