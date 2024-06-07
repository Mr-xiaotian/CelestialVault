import numpy as np
import numpy.random as nr
import scipy.special as sp

class NeuralNetwork:
    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate):
        # 定义输入层、隐藏层、输出层的节点数，以及学习率
        self.inodes = inputnodes
        self.hnodes = hiddennodes
        self.onodes = outputnodes
        self.lr = learningrate

        # 初始化权重矩阵，使用正态分布，并根据节点数进行缩放
        # 输入层到隐藏层的权重矩阵
        self.wih = nr.normal(0, pow(self.hnodes, -0.5), (self.hnodes, self.inodes))
        # 隐藏层到输出层的权重矩阵
        self.who = nr.normal(0, pow(self.onodes, -0.5), (self.onodes, self.hnodes))

        # 定义激活函数为sigmoid函数
        self.activation_function = lambda x: sp.expit(x)
        pass
    
    def train(self, input_list, targets_list):
        # 将输入列表和目标列表转换为二维数组并转置为列向量
        target = np.array(targets_list, ndmin=2).T
        inputs = np.array(input_list, ndmin=2).T

        # 计算隐藏层的输入和输出
        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        
        # 计算最终输出层的输入和输出
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        # 计算输出层的误差 (目标值 - 预测值)
        output_errors = target - final_outputs
        # 计算隐藏层的误差 (输出层误差传递回隐藏层)
        hidden_errors = np.dot(self.who.T, output_errors)

        # 根据误差更新隐藏层到输出层的权重矩阵
        self.who += self.lr * np.dot((output_errors * final_outputs * (1 - final_outputs)),
                                     np.transpose(hidden_outputs))
        # 根据误差更新输入层到隐藏层的权重矩阵
        self.wih += self.lr * np.dot((hidden_errors * hidden_outputs * (1 - hidden_outputs)),
                                     np.transpose(inputs))
        
        # 计算误差更新矩阵 e 用于输出
        e = self.lr * np.dot((output_errors * final_outputs * (1 - final_outputs)),
                                     np.transpose(hidden_outputs))
        return final_outputs, output_errors, e
    
    def query(self, input_list):
        # 将输入列表转换为二维数组并转置为列向量
        inputs = np.array(input_list, ndmin=2).T

        # 计算隐藏层的输入和输出
        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        
        # 计算最终输出层的输入和输出
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        
        # 返回输出层中值最大的索引，即预测的类别
        return np.argmax(final_outputs)
