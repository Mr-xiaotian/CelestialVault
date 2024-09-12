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
