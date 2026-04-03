# instances/inst_network.py

## 源文件
- `src/celestialvault/instances/inst_network.py`

## 模块说明
无模块级文档字符串。

## 导入依赖
- `from __future__ import annotations`
- `import random`
- `import numpy as np`
- `import numpy.random as nr`
- `import scipy.special as sp`
- `from tqdm import tqdm`

## 模块常量
- 无

## 顶层函数
### `sigmoid_double`
- 签名: `def sigmoid_double(x)`
- 说明: 计算标量 x 的 sigmoid 值。

:param x: 输入标量。
:return: sigmoid 值，即 1 / (1 + exp(-x))。

### `sigmoid`
- 签名: `def sigmoid(x)`
- 说明: 对数组 x 逐元素计算 sigmoid 激活值。

:param x: 输入数组。
:return: 逐元素计算后的 sigmoid 值数组。

### `sigmoid_prime_double`
- 签名: `def sigmoid_prime_double(x)`
- 说明: 计算标量 x 的 sigmoid 导数。

:param x: 输入标量。
:return: sigmoid 导数值，即 sigmoid(x) * (1 - sigmoid(x))。

### `sigmoid_prime`
- 签名: `def sigmoid_prime(z)`
- 说明: 对数组 z 逐元素计算 sigmoid 导数。

:param z: 输入数组。
:return: 逐元素计算后的 sigmoid 导数数组。

## 类
### `NeuralNetwork`
- 继承: `object`
- 说明: 三层前馈神经网络（输入层、隐藏层、输出层），使用 sigmoid 激活和反向传播训练。
- 方法:
  - `def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate)`
  - `def train(self, input_list, targets_list)`
  - `def query(self, input_list)`

### `Layer`
- 继承: `object`
- 说明: 神经网络层的抽象基类，定义前向传播和反向传播接口。
- 方法:
  - `def __init__(self)`
  - `def connect(self, next_layer: Layer)`
  - `def forward(self)`
  - `def get_forward_input(self)`
  - `def backward(self)`
  - `def get_backward_input(self)`
  - `def clear_deltas(self)`
  - `def update_params(self, learning_rate)`
  - `def describe(self)`

### `ActivationLayer`
- 继承: `Layer`
- 说明: 使用 sigmoid 函数的激活层。
- 方法:
  - `def __init__(self, input_dim)`
  - `def forward(self)`
  - `def backward(self)`
  - `def describe(self)`

### `DenseLayer`
- 继承: `Layer`
- 说明: 全连接层，包含权重矩阵和偏置向量。
- 方法:
  - `def __init__(self, input_dim, output_dim)`
  - `def forward(self)`
  - `def backward(self)`
  - `def update_params(self, learning_rate)`
  - `def clear_deltas(self)`
  - `def describe(self)`

### `SequentialNetwork`
- 继承: `object`
- 说明: 顺序神经网络容器，按添加顺序连接各层并支持小批量训练。
- 方法:
  - `def __init__(self, loss = None)`
  - `def add(self, layer)`
  - `def train(self, train_data, epochs, mini_batch_size, learning_rate, test_data = None)`
  - `def train_batch(self, mini_batch, learning_rate)`
  - `def update(self, mini_batch, learning_rate)`
  - `def forward_backward(self, mini_batch)`
  - `def single_forward(self, x)`
  - `def evaluate(self, test_data)`

### `MSE`
- 继承: `object`
- 说明: 均方误差（Mean Squared Error）损失函数。
- 方法:
  - `def loss(self, predicted, actual)`
  - `def loss_derivative(self, predicted, actual)`
