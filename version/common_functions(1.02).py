# -*- coding: utf-8 -*-
#版本 1.02
#作者：晓天
#时间：12/11/2021
def pro_slash(strs):
    #get_name/get_lyric中获得的网页文件中中文字符用unicode编码，如\u5c11,但所有转义符均被转义，如\\u5c11
    #此函数用来消除多余的转义符，例如'abc\\\\def\\\\ghi\\\\jk'
    re_strs = repr(strs)   #返回对象string格式，如"'abc\\\\\\\\def\\\\\\\\ghi\\\\\\\\jk'"
    pl_strs = re_strs.replace('\\\\', '\\')   #如"'abc\\\\def\\\\ghi\\\\jk'"
    if pl_strs[-2] == '\\':   #在下载monkey dance时，get_lyric进行错误处理，使传入值以\\结尾，eval后将'转义，在此进行临时处理
        print(pl_strs[1:-2])
        pro_strs = eval(pl_strs[1:-2])
        return pro_strs
    else:
        pro_strs = eval(pl_strs)   #如'abc\\def\\ghi\\jk'
        return pro_strs

def creat_folder(path):
    #判断系统是否存在该路径，没有则创建
    import os
    while True:
        try:
            if not os.path.exists(path):   
                os.makedirs(path)
            break
        except:
            path = path[:-1]
            continue
    return path

def str_to_dict(strs):
    header = strs.split('\n')
    headers = {}
    
    while '' in header:
        header.remove('')
        
    for h in header:
        if h[0] == ':':
            h = h[1:]
        sp = h.partition(':')
        headers[sp[0]] = sp[2].strip()

    return headers

def list_removes(lists, _remove):
    while _remove in lists:
        lists.remove(_remove)
    return lists

def iprint(obj):
    from pprint import pprint
    if len(obj) < 16:
        pprint(obj)
    else:
        pprint(obj[:10])
        print(f'(此处省略{len(obj)-15}项)')
        pprint(obj[-5:])
        #print(obj)
    
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


if __name__ == '__main__':
    pass
    


