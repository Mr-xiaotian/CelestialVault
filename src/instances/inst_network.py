import numpy as np
import numpy.random as nr
import scipy.special as sp


class NeuralNetwork:
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
