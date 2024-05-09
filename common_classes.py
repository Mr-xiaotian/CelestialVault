# -*- coding: utf-8 -*-
#版本 1.02
#作者：晓天
#时间：12/11/2021
'''
import numpy as np
import numpy.random as nr
import scipy.special as sp
'''
class neuralNetwork:
    def __init__(self,inputnodes,hiddennodes,outputnodes,learningrate):
        #定义输入层 隐藏层 输出层节点数，及学习率
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes
        self.lr = learningrate

        #定义权重矩阵
        #self.wih = nr.rand(self.hnodes,self.inodes) - 0.5
        #self.who = nr.rand(self.onodes, self.hnodes) - 0.5
        self.wih = nr.normal(0,pow(self.hnodes,-0.5),(self.hnodes,self.inodes))
        self.who = nr.normal(0,pow(self.onodes,-0.5),(self.onodes,self.hnodes))

        #定义sigmoid方程
        self.activation_function = lambda x: sp.expit(x)
        pass
    
    def train(self, input_list, targets_list):
        target = np.array(targets_list, ndmin=2).T
        inputs = np.array(input_list, ndmin=2).T

        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        output_errors = target - final_outputs
        hidden_errors = np.dot(self.who.T,output_errors)

        self.who += self.lr * np.dot((output_errors*final_outputs*(1-final_outputs)),
                                     np.transpose(hidden_outputs))
        self.wih += self.lr * np.dot((hidden_errors*hidden_outputs*(1 - hidden_outputs)),
                                     np.transpose(inputs))
        
        e = self.lr * np.dot((output_errors*final_outputs*(1-final_outputs)),
                                     np.transpose(hidden_outputs))
        return final_outputs, output_errors, e
    
    def query(self, input_list):
        inputs = np.array(input_list, ndmin=2).T

        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        
        return np.argmax(final_outputs)

class Node(object):
    def __init__(self, elem, _next=None):
        self.elem = elem  # 表示对应的元素值
        self._next = _next  # 表示下一个链接的链点
        
class Queue(object):
    def __init__(self):
        self.head = None  # 头部链点为 None
        self.rear = None  # 尾部链点为 None
        
    def is_empty(self):
        return self.head is None  # 判断队列是否为空
    
    def enqueue(self, elem):
        """
        往队尾添加一个元素
        :param elem:
        :return:
        """
        p = Node(elem)  # 初始化一个新的点
        if self.is_empty():
            self.head = p  # 队列头部为新的链点
            self.rear = p  # 队列尾部为新的链点
        else:
            self.rear._next = p  # 队列尾部的后继是这个新的点
            self.rear = p  # 然后让队列尾部指针指向这个新的点
            
    def dequeue(self):
        """
        从队列头部删除一个元素，并返回这个值，类似于pop
        :return:
        """
        if self.is_empty():  # 判断队列是否为空
            print('Queue_is_empty')  # 若队列为空，则退出 dequeue 操作
        else:
            result = self.head.elem  # result为队列头部元素
            self.head = self.head._next  # 改变队列头部指针位置
            return result  # 返回队列头部元素
        
    def peek(self):
        """
        查看队列的队头
        :return:
        """
        if self.is_empty():  # 判断队列是否为空
            print('NOT_FOUND')  # 为空则返回 NOT_FOUND
        else:
            return self.head.elem  # 返回队列头部元素
        
    def print_queue(self):
        print("queue:")
        temp = self.head
        myqueue = []  # 暂时存放队列数据
        while temp is not None:
            myqueue.append(temp.elem)
            temp = temp._next
        print(myqueue)

class Queue_bylist():
    def __init__(self):
        self.entries = []  # 表示队列内的参数
        self.length = 0  # 表示队列的长度
        self.front = 0  # 表示队列头部位置

    def enqueue(self, item):
        self.entries.append(item)  # 添加元素到队列里面
        self.length = self.length + 1  # 队列长度增加 1

    def dequeue(self):
        self.length = self.length - 1  # 队列的长度减少 1
        dequeued = self.entries[self.front]  # 队首元素为dequeued
        self.front += 1  # 队首的位置增加1
        self.entries = self.entries[self.front:]  # 队列的元素更新为退队之后的队列
        return dequeued

    def peek(self):
        return self.entries[0]  # 直接返回队列的队首元素

    def print_queue(self):
        print(self.entries)

from threading import Thread
class MyThread(Thread):
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
        
if __name__ == '__main__':
    queue = Queue()
    queue.enqueue(44)
    queue.enqueue(99)
    queue.enqueue("BB")
    queue.print_queue()
    print(queue.dequeue())
    print(queue.peek())

