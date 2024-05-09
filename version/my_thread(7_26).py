import sys,traceback
from time import sleep
from math import ceil
from random import randint
from threading import Thread
import common_functions as cf

class ThreadWorker(Thread):
    def __init__(self, func, args):
        '''
        :param func: 可调用的对象
        :param args: 可调用对象的参数
        '''
        Thread.__init__(self)
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
            import sys,traceback
            self.exitcode = False
            # 如果线程异常退出，将该标志位设置为False，正常退出为True
            self.exception = e
            self.exc_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
            #在改成员变量中记录异常信息

    def getResult(self):
        return self.result

class Threader:
    def __init__(self, func, _pool = None):
        self.thread_num = 50
        
        self.func = func
        self._pool = _pool
        
        self.texts_list = []
        self.texts_dir = {}
        self.error_text_list = []
        self.error_dictory_list = []

    def get_args(self, obj: object) -> tuple:
        raise NotImplementedError

    def thread_text(self, obj: object, result: object) -> object:
        raise NotImplementedError

    def thread_text_if_error(self, obj: object) -> object:
        raise NotImplementedError
        
    def start(self, dictory, start_type = 'sheep'):
        self.texts_list = []
        dictory_len = len(dictory)
        
        self.error_flag = True
        self.error_text_list = []
        
        for i in range(0,ceil(dictory_len/self.thread_num)):
            dictory_start = i * self.thread_num
            dictory_end = min((i+1) * self.thread_num, dictory_len)
            
            if start_type == 'flock':
                self.flock(dictory[dictory_start:dictory_end], i)
            else:
                self.sheep(dictory[dictory_start:dictory_end], i)
                    
    def start_(self, dictory, file_name, start_type = 'sheep'):
        dictory_len = len(dictory)
        
        for i in range(0,ceil(dictory_len/self.thread_num)):
            self.texts_list = []
            self.error_text_list = []
            self.error_flag = True
            
            dictory_start = i * self.thread_num
            dictory_end = min((i+1) * self.thread_num, dictory_len)
            if start_type == 'sheep':
                self.sheep(dictory[dictory_start:dictory_end], i)
            elif start_type == 'flock':
                self.flock(dictory[dictory_start:dictory_end], i)
            print()
                
            name_add = ''
            file_name = file_name.format(name_add = name_add)

            if not self.error_flag:
                print('\n\n' + "\\".join(self.error_text_list) + '下载出错')

            self._pool.download_main(file_name, self.getTextList())

    def flock(self, dictory, thread_group):
        dictory_len = len(dictory)
        
        for d,num in zip(dictory,range(dictory_len)):
            threads_ = 'thread_' + str(num)
            locals()[threads_] = ThreadWorker(self.func, self.get_args(d))
            locals()[threads_].start()

        for num in range(dictory_len):
            threads_ = 'thread_' + str(num)
            locals()[threads_].join()

            print_file = sys.stdout
            if not locals()[threads_].exitcode:
                self.error_flag = False
                #print('\n', num, locals()[texts_].exception)
                #print(locals()[threads_].exc_traceback)
                self.error_text_list.append(f'{num+1+thread_group*self.thread_num}{d}')
                # self.error_dictory_list.append(d)
                print_file = sys.stderr
                
            # print(f'{num+1+thread_group*self.thread_num}_', end = '',
            #       file = print_file)

        for num,d in enumerate(dictory):
            threads_ = 'thread_' + str(num)
            result = locals()[threads_].getResult()
            
            texts = self.thread_text(d, result)
            self.texts_list.append(texts)
            self.texts_dir[str(d)] = texts

    def sheep(self, dictory, thread_group):
        for num,d in enumerate(dictory):
            try:
                texts = self.thread_text(d, self.func(*self.get_args(d)))
                print_file = sys.stdout
                
            except Exception as e:
                texts = self.thread_text_if_error(d, self.func(*self.get_args(d)))
                self.error_flag = False
                self.error_text_list.append(f'{num+1+thread_group*self.thread_num}{d}')
                self.error_dictory_list.append(d)
                # print(''.join(traceback.format_exception(*sys.exc_info())))
                
                print_file = sys.stderr
                
            finally:
                self.texts_list.append(texts)
                self.texts_dir[str(d)] = texts
                # print(f'{num+1+thread_group*self.thread_num}_', end = '',
                #       file = print_file)

    def getTextList(self):
        return self.texts_list
    
    def getTextDir(self):
        return self.texts_dir
