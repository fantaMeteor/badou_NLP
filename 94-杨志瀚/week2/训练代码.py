﻿import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""

规律：x是一个5维向量，如果第1个数>第2个数，第1个数>第3个数，类别1
                     第2个数>第1个数，第2个数>第3个数  类别2
                     第3个数>第1个数，第3个数>第1个数  类别3
"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, 3)  # 线性层
        self.activation = torch.softmax #softmax
        self.loss = nn.CrossEntropyLoss()  # loss函数采用交叉熵函数

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        y_pred= self.linear(x)  # (batch_size, input_size) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return y_pred  # 输出预测结果
    def forward1(self, x, y=None):
        x = self.linear(x)  # (batch_size, input_size) -> (batch_size, 1)
        y_pred = self.activation(x,dim=0)  # (batch_size, 1) -> (batch_size, 1)

        return y_pred  # 输出预测结果




# 生成样本, 样本的生成方法，代表了我们要学习的规律
def build_sample():
    x = np.random.random(5)
    if x[0] > x[1] and x[0] > x[2]:
        return x, 0
    elif x[1] > x[0] and x[1] > x[2]:
        return x, 1
    else:
        return x, 2



# 随机生成一批样本
# 正负样本均匀生成
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append([y])
    return torch.FloatTensor(X), torch.LongTensor(Y).squeeze()#返回五维x及类别y



def main():
    # 配置参数
    epoch_num = 100  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    learning_rate = 0.05  # 学习率
    # 建立模型
    model = TorchModel(input_size)
    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size : (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size : (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算loss
            loss.backward()  # 计算梯度
            if batch_index % 2 == 0:
                optim.step()  # 更新权重
                optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "model.pth")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return

#
# # # 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(model.state_dict())
# #
    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward1(torch.FloatTensor(input_vec)) 
	
 # 模型预测
    print(result)
#   for vec, res in zip(input_vec, result):
#         # print("输入：%s, 预测类别：%d" % (vec, res))  # 打印结果
#         print(res)


if __name__ == "__main__":
    main()
    test_vec = [[0.47889086,0.15229675,0.31082123,0.03504317,0.18920843],
                [0.94963533,0.5524256,0.95758807,0.95520434,0.84890681],
                [0.78797868,0.67482528,0.13625847,0.34675372,0.09871392],
                [0.89349776,0.59416669,0.92579291,0.41567412,0.7358894],
                [0.78934976,0.1,0.5,0.41567412,0.7358894]]
    predict("model.pth", test_vec)