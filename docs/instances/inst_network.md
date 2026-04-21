# `celestialvault.instances.inst_network`

## 源文件 - `src/celestialvault/instances/inst_network.py`

## 模块说明

提供神经网络相关类，包括三层前馈神经网络、可组合的层抽象、顺序网络容器和损失函数。

## 导入依赖

- `from __future__ import annotations`
- `random` - 数据打乱
- `numpy` - 矩阵运算
- `numpy.random` - 权重初始化
- `scipy.special` - sigmoid 函数（`expit`）
- `tqdm` - 进度条

## 类

### `NeuralNetwork`

- 继承: 无
- 说明: 三层前馈神经网络（输入层、隐藏层、输出层），使用 sigmoid 激活和反向传播训练。

- 构造函数: `__init__(self, inputnodes, hiddennodes, outputnodes, learningrate)`
  - 参数:
    - `inputnodes` (`int`): 输入层节点数。
    - `hiddennodes` (`int`): 隐藏层节点数。
    - `outputnodes` (`int`): 输出层节点数。
    - `learningrate` (`float`): 学习率。
  - 属性:
    - `self.wih` (`ndarray`): 输入层到隐藏层的权重矩阵，形状 `(hiddennodes, inputnodes)`。
    - `self.who` (`ndarray`): 隐藏层到输出层的权重矩阵，形状 `(outputnodes, hiddennodes)`。
    - `self.activation_function`: sigmoid 激活函数。

- 方法:

  #### `train(self, input_list, targets_list)`
  - 签名: `train(self, input_list, targets_list) -> tuple`
  - 说明: 使用反向传播算法对网络进行一次训练。
  - 参数:
    - `input_list`: 输入数据列表。
    - `targets_list`: 目标输出数据列表。
  - 返回值: `(最终输出, 输出层误差, 误差更新矩阵)` 元组。

  #### `query(self, input_list)`
  - 签名: `query(self, input_list) -> int`
  - 说明: 使用训练好的网络进行推理，返回预测的类别索引。
  - 参数:
    - `input_list`: 输入数据列表。
  - 返回值: 输出层中值最大的索引（预测类别）。

- 用法示例:

```python
from celestialvault.instances.inst_network import NeuralNetwork
import numpy as np

nn = NeuralNetwork(784, 200, 10, 0.1)

# 训练
inputs = np.random.rand(784)
targets = np.zeros(10)
targets[3] = 1.0
nn.train(inputs, targets)

# 推理
prediction = nn.query(inputs)
print(f"预测类别: {prediction}")
```

- 关联: 独立使用，无跨模块依赖。

---

### `Layer`

- 继承: 无
- 说明: 神经网络层的抽象基类，定义前向传播和反向传播接口。

- 构造函数: `__init__(self)`
  - 属性:
    - `params` (`list`): 层参数列表。
    - `previous` (`Layer | None`): 上一层引用。
    - `next` (`Layer | None`): 下一层引用。
    - `input_data`, `output_data`: 前向传播数据缓存。
    - `input_delta`, `output_delta`: 反向传播梯度缓存。

- 方法:

  #### `connect(self, next_layer)`
  - 签名: `connect(self, next_layer: Layer) -> None`
  - 说明: 将当前层与下一层连接，建立双向引用。

  #### `forward(self)`
  - 说明: 前向传播（子类实现）。

  #### `get_forward_input(self)`
  - 说明: 获取前向传播的输入数据：优先取前一层的输出，否则取自身的输入数据。
  - 返回值: 前向传播的输入数据。

  #### `backward(self)`
  - 说明: 反向传播（子类实现）。

  #### `get_backward_input(self)`
  - 说明: 获取反向传播的梯度输入：优先取后一层的输出梯度，否则取自身的输入梯度。
  - 返回值: 反向传播的梯度输入。

  #### `clear_deltas(self)`
  - 说明: 清除累积梯度（子类可覆写）。

  #### `update_params(self, learning_rate)`
  - 说明: 更新参数（子类可覆写）。

  #### `describe(self)`
  - 说明: 打印层描述信息（子类实现）。

- 关联: 被 `ActivationLayer`、`DenseLayer` 继承；被 `SequentialNetwork` 使用。

---

### `ActivationLayer`

- 继承: `Layer`
- 说明: 使用 sigmoid 函数的激活层。输入维度等于输出维度。

- 构造函数: `__init__(self, input_dim)`
  - 参数:
    - `input_dim` (`int`): 输入维度（输出维度与输入相同）。

- 方法: `forward()`, `backward()`, `describe()`

---

### `DenseLayer`

- 继承: `Layer`
- 说明: 全连接层，包含权重矩阵和偏置向量。

- 构造函数: `__init__(self, input_dim, output_dim)`
  - 参数:
    - `input_dim` (`int`): 输入维度。
    - `output_dim` (`int`): 输出维度。
  - 属性:
    - `self.weight` (`ndarray`): 权重矩阵，形状 `(output_dim, input_dim)`。
    - `self.bias` (`ndarray`): 偏置向量，形状 `(output_dim, 1)`。

- 方法: `forward()`, `backward()`, `update_params(learning_rate)`, `clear_deltas()`, `describe()`

---

### `SequentialNetwork`

- 继承: 无
- 说明: 顺序神经网络容器，按添加顺序连接各层并支持小批量训练。

- 构造函数: `__init__(self, loss=None)`
  - 参数:
    - `loss`: 损失函数对象，默认使用 `MSE()`。

- 方法:

  #### `add(self, layer)`
  - 签名: `add(self, layer) -> None`
  - 说明: 添加一层到网络中，并自动与前一层连接。

  #### `train(self, train_data, epochs, mini_batch_size, learning_rate, test_data=None)`
  - 签名: `train(self, train_data, epochs, mini_batch_size, learning_rate, test_data=None) -> None`
  - 说明: 使用小批量随机梯度下降训练网络。
  - 参数:
    - `train_data`: 训练数据列表，每个元素为 `(输入, 目标)` 元组。
    - `epochs` (`int`): 训练轮数。
    - `mini_batch_size` (`int`): 每个小批量的大小。
    - `learning_rate` (`float`): 学习率。
    - `test_data`: 可选的测试数据，用于评估。

  #### `train_batch(self, mini_batch, learning_rate)`
  - 说明: 对单个小批量执行前向-反向传播和参数更新。

  #### `update(self, mini_batch, learning_rate)`
  - 说明: 根据小批量大小归一化学习率，更新所有层的参数并清除梯度。

  #### `forward_backward(self, mini_batch)`
  - 说明: 对小批量中的每个样本执行前向传播和反向传播，累积梯度。

  #### `single_forward(self, x)`
  - 签名: `single_forward(self, x) -> numpy.ndarray`
  - 说明: 对单个输入执行前向传播并返回最终输出。

  #### `evaluate(self, test_data)`
  - 签名: `evaluate(self, test_data) -> int`
  - 说明: 在测试数据上评估网络，返回预测正确的样本数。

- 用法示例:

```python
from celestialvault.instances.inst_network import SequentialNetwork, DenseLayer, ActivationLayer

net = SequentialNetwork()
net.add(DenseLayer(784, 128))
net.add(ActivationLayer(128))
net.add(DenseLayer(128, 10))
net.add(ActivationLayer(10))

# 训练（train_data 为 [(input_array, target_array), ...] 列表）
net.train(train_data, epochs=5, mini_batch_size=32, learning_rate=0.1, test_data=test_data)
```

- 关联: 使用 `DenseLayer`、`ActivationLayer` 和 `MSE` 损失函数。

---

### `MSE`

- 继承: 无
- 说明: 均方误差（Mean Squared Error）损失函数。

- 方法:

  #### `loss(self, predicted, actual)`
  - 签名: `loss(self, predicted, actual) -> float`
  - 说明: 计算预测值与实际值之间的均方误差。

  #### `loss_derivative(self, predicted, actual)`
  - 签名: `loss_derivative(self, predicted, actual) -> numpy.ndarray`
  - 说明: 计算均方误差对预测值的导数：`2 * (predicted - actual) / actual.size`。

- 关联: 被 `SequentialNetwork` 默认使用。

## 顶层函数

### `sigmoid_double(x)`
- 签名: `sigmoid_double(x) -> float`
- 说明: 计算标量 x 的 sigmoid 值，即 `1 / (1 + exp(-x))`。
- 参数: `x` - 输入标量。

### `sigmoid(x)`
- 签名: `sigmoid(x) -> numpy.ndarray`
- 说明: 对数组 x 逐元素计算 sigmoid 激活值（通过 `np.vectorize`）。
- 参数: `x` - 输入数组。

### `sigmoid_prime_double(x)`
- 签名: `sigmoid_prime_double(x) -> float`
- 说明: 计算标量 x 的 sigmoid 导数，即 `sigmoid(x) * (1 - sigmoid(x))`。
- 参数: `x` - 输入标量。

### `sigmoid_prime(z)`
- 签名: `sigmoid_prime(z) -> numpy.ndarray`
- 说明: 对数组 z 逐元素计算 sigmoid 导数（通过 `np.vectorize`）。
- 参数: `z` - 输入数组。
