# -*- coding: utf-8 -*-
#版本 1.60
#作者：晓天, GPT-4
#时间：26/7/2023

import sys
import traceback
from math import ceil
from threading import Thread
import asyncio


class ThreadWorker(Thread):
    def __init__(self, func, args):
        """
        Initialization of ThreadWorker

        Parameters:
        func: callable object
        args: arguments for the callable object
        """
        super().__init__()
        self.func = func
        self.args = args
        self.result = None
        self.exitcode = True
        self.exception = None
        self.exc_traceback = ''

    def run(self):
        try:
            self.result = self.func(*self.args)
        except Exception as e:
            self.exitcode = False
            self.exception = e
            # 在成员变量中记录异常信息
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))

    def getResult(self):
        return self.result

class ThreadManager:
    def __init__(self, func, pool=None, thread_num=50):
        self.func = func
        self.pool = pool
        self.thread_num = thread_num
        self.result_list = []
        self.result_dict = {}
        self.error_list = []
        self.error_dict = {}

    def get_args(self, obj):
        raise NotImplementedError("This method should be overridden")

    def process_result(self, obj, result):
        raise NotImplementedError("This method should be overridden")

    def handle_error(self, obj):
        raise NotImplementedError("This method should be overridden")

    def start(self, dictory, start_type='serial'):
        self.result_list = []
        dictory_len = len(dictory)
        self.error_flag = True
        self.error_list = []

        for i in range(0,ceil(dictory_len/self.thread_num)):
            dictory_start = i * self.thread_num
            dictory_end = min((i+1) * self.thread_num, dictory_len)
            
            if start_type == 'parallel':
                self.run_in_parallel(dictory[dictory_start:dictory_end])
            elif start_type == 'async':
                asyncio.run(self.run_in_async(dictory[dictory_start:dictory_end]))
            else:
                self.run_in_serial(dictory[dictory_start:dictory_end])
    
    async def start_async(self, dictory):
        self.result_list = []
        dictory_len = len(dictory)
        self.error_flag = True
        self.error_list = []

        for i in range(0,ceil(dictory_len/self.thread_num)):
            dictory_start = i * self.thread_num
            dictory_end = min((i+1) * self.thread_num, dictory_len)
            
            await self.run_in_async(dictory[dictory_start:dictory_end])

    def run_in_parallel(self, dictory):
        threads = []
        for d in dictory:
            thread = ThreadWorker(self.func, self.get_args(d))
            threads.append(thread)
            thread.start()

        for num, (thread, d) in enumerate(zip(threads, dictory)):
            thread.join()
            if not thread.exitcode:
                self.error_flag = False
                self.error_list.append(d)
                self.error_dict[d] = thread.exc_traceback
                continue

            result = thread.getResult()
            processed_result = self.process_result(d, result)
            self.result_list.append(processed_result)
            self.result_dict[d] = processed_result

    def run_in_serial(self, dictory):
        for num, d in enumerate(dictory):
            try:
                result = self.func(*self.get_args(d))
                processed_result = self.process_result(d, result)
            except Exception as e:
                self.error_flag = False
                self.error_list.append(d)
                self.error_dict[d] = traceback.format_exc()
                continue

            self.result_list.append(processed_result)
            self.result_dict[d] = processed_result

    async def run_in_async(self, dictory):
        tasks = []
        for d in dictory:
            task = asyncio.create_task(self.func(*self.get_args(d)))
            tasks.append(task)

        for num, (task, d) in enumerate(zip(tasks, dictory)):
            try:
                result = await task
                processed_result = self.process_result(d, result)
            except Exception as e:
                self.error_flag = False
                self.error_list.append(d)
                self.error_dict[d] = traceback.format_exc()
                continue

            self.result_list.append(processed_result)
            self.result_dict[d] = processed_result

    def get_result_list(self):
        return self.result_list

    def get_result_dict(self):
        return self.result_dict
