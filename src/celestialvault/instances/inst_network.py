from __future__ import annotations
import random
import numpy as np
import numpy.random as nr
import scipy.special as sp
from tqdm import tqdm

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

class Layer:
    def __init__(self):
        self.params = []

        self.previous: Layer = None
        self.next: Layer = None

        self.input_data = None
        self.output_data = None

        self.input_delta = None
        self.output_delta = None

    def connect(self, next_layer: Layer):
        self.next = next_layer
        next_layer.previous = self

    def forward(self):
        raise NotImplementedError
    
    def get_forward_input(self):
        if self.previous is not None:
            return self.previous.output_data
        else:
            return self.input_data
        
    def backward(self):
        raise NotImplementedError
    
    def get_backward_input(self):
        if self.next is not None:
            return self.next.output_delta
        else:
            return self.input_delta
        
    def clear_deltas(self):
        pass

    def update_params(self, learning_rate):
        pass

    def describe(self):
        raise NotImplementedError
    
def sigmoid_double(x):
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid(x):
    return np.vectorize(sigmoid_double)(x)

def sigmoid_prime_double(x):
    return sigmoid_double(x) * (1 - sigmoid_double(x))

def sigmoid_prime(z):
    return np.vectorize(sigmoid_prime_double)(z)

class ActivationLayer(Layer):
    def __init__(self, input_dim):
        super(ActivationLayer, self).__init__()

        self.input_dim = input_dim
        self.output_dim = input_dim

    def forward(self):
        data = self.get_forward_input()
        if data is None:
            raise ValueError("Input data to forward pass cannot be None.")
        self.output_data = sigmoid(data)

    def backward(self):
        data = self.get_forward_input()
        delta = self.get_backward_input()
        sigmoid_prime_data = sigmoid_prime(data)

        self.output_delta = delta * sigmoid_prime_data

    def describe(self):
        print("|--" + self.__class__.__name__)
        print(f" |-- dimensions: ({self.input_dim}, {self.output_dim})")


class DenseLayer(Layer):
    def __init__(self, input_dim, output_dim):
        super(DenseLayer, self).__init__()
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        self.weight = np.random.randn(output_dim, input_dim)
        self.bias = np.random.randn(output_dim, 1)
        self.params = [self.weight, self.bias]
        
        self.delta_w = np.zeros(self.weight.shape)
        self.delta_b = np.zeros(self.bias.shape)

    def forward(self):
        data = self.get_forward_input()
        if data is None:
            raise ValueError("Input data to forward pass cannot be None.")
        self.output_data = np.dot(self.weight, data) + self.bias

    def backward(self):
        data = self.get_forward_input()
        delta = self.get_backward_input()
        
        self.delta_b += delta
        self.delta_w += np.dot(delta, data.T)
        self.output_delta = np.dot(self.weight.T, delta)

    def update_params(self, learning_rate):
        self.weight -= learning_rate * self.delta_w
        self.bias -= learning_rate * self.delta_b

    def clear_deltas(self):
        self.delta_w = np.zeros(self.weight.shape)
        self.delta_b = np.zeros(self.bias.shape)

    def describe(self):
        print("|--" + self.__class__.__name__)
        print(f" |-- dimensions: ({self.input_dim}, {self.output_dim})")


class SequentialNetwork:
    def __init__(self, loss = None):
        print("Initialize Network...")
        self.layers = []
        if loss is None:
            self.loss = MSE()

    def add(self, layer):
        self.layers.append(layer)
        layer.describe()
        if len(self.layers) > 1:
            self.layers[-2].connect(self.layers[-1])

    def train(self, train_data, epochs, mini_batch_size, learning_rate, test_data=None):
        n = len(train_data)
        for epoch in range(epochs):
            random.shuffle(train_data)

            mini_batches = [
                train_data[k:k+mini_batch_size] 
                for k in range(0, n, mini_batch_size)
                ]
            
            for mini_batch in tqdm(mini_batches):
                self.train_batch(mini_batch, learning_rate)
            
            # if test_data:
            #     n_test = len(test_data)
            #     print(f"Epoch {epoch+1}: {self.evaluate(test_data)} / {n_test}")
            # else:
            #     print(f"Epoch {epoch+1} complete")
        n_test = len(test_data)
        print(f"{self.evaluate(test_data)} / {n_test}")

    def train_batch(self, mini_batch, learning_rate):
        self.forward_backward(mini_batch)
        self.update(mini_batch, learning_rate)

    def update(self, mini_batch, learning_rate):
        learning_rate = learning_rate / len(mini_batch)
        for layer in self.layers:
            layer.update_params(learning_rate)
        for layer in self.layers:
            layer.clear_deltas()

    def forward_backward(self, mini_batch):
        for x, y in mini_batch:
            self.layers[0].input_data = x.reshape(-1, 1)
            for layer in self.layers:
                layer.forward()
            self.layers[-1].input_delta = \
                self.loss.loss_derivative(self.layers[-1].output_data, y.reshape(-1, 1))
            for index,layer in enumerate(reversed(self.layers)):
                layer.backward()

    def single_forward(self, x):
        self.layers[0].input_data = x
        for layer in self.layers:
            layer.forward()
        return self.layers[-1].output_data
    
    def evaluate(self, test_data):
        win = 0
        for x, y in tqdm(test_data):
            r_0 = np.argmax(self.single_forward(x))
            r_1 = np.argmax(y)
            win += 1 if r_0 == r_1 else 0
        return win
    
class MSE:
    def loss(self, predicted, actual):
        return np.mean((predicted - actual) ** 2)

    def loss_derivative(self, predicted, actual):
        return 2 * (predicted - actual) / actual.size