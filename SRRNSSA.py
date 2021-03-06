import random
import sys

import numpy as np
import math

from numpy.core.defchararray import find
from SSALIGHTGBM import F22
from solution import solution
import time
import matplotlib.pyplot as plt

def Bounds( s, Lb, Ub):
    temp = s
    for i in range(len(s)):
        if temp[i] < Lb[0, i]:
            temp[i] = Lb[0, i]
        elif temp[i] > Ub[0, i]:
            temp[i] = Ub[0, i]

    return temp
def SRRNSSA( lb, ub, dim, N, Max_iteration):

    # Max_iteration=1000
    # lb=-100
    # ub=100
    # dim=30
    P_percent = 0.2
    pNum = round(N * P_percent)  # 生产者的人口规模占总人口规模的20%
    # N = 50  # Number of search agents
    # if not isinstance(lb, list):
    #     lb = [lb] * dim
    # if not isinstance(ub, list):
    #     ub = [ub] * dim
    lb = lb * np.ones((1, dim))  # 生成1*dim的全1矩阵，并全乘以c；lb是下限
    ub = ub * np.ones((1, dim))  # ub是上限
    X = np.zeros((N, dim))  # 生成pop*dim的全0矩阵，代表麻雀位置
    fit = np.zeros((N, 1))  # 适应度值初始化

    s = solution()

    print('SRRNSSA is optimizing  "' + F22.__name__ + '"')
    for i in range(N):
        X[i, :] = lb + (ub - lb) * np.random.rand(1, dim)  # 麻雀属性随机初始化初始值
        fit[i, 0] = F22(X[i, :])   # 初始化最佳适应度值

    pFit = fit  # 最佳适应度矩阵
    pX = X  # 最佳种群位置
    fMin = np.min(fit[:, 0])  # fMin表示全局最优适应值，生产者能量储备水平取决于对个人适应度值的评估
    bestI = np.argmin(fit[:, 0])
    bestX = X[bestI, :]  # bestX表示fMin对应的全局最优位置的变量信息
    Convergence_curve = np.zeros(Max_iteration)
    # Convergence_curve = np.zeros((1, Max_iteration))  # 初始化收敛曲线
    timerStart = time.time()
    for t in range(Max_iteration):  # 迭代更新
        sortIndex = np.argsort(pFit.T)  # 对麻雀的适应度值进行排序，并取出下标
        fmax = np.max(pFit[:, 0])  # 取出最大的适应度值
        B = np.argmax(pFit[:, 0])  # 取出最大的适应度值得下标
        worse = X[B, :]  # 最差适应度

        r2 = np.random.rand(1)  # 预警值
        # 这一部位为发现者（探索者）的位置更新
        if r2 < 0.8:  # 预警值较小，说明没有捕食者出现
            # for i in range(pNum):
            #     r1 = np.random.randn(1)
            #     X[sortIndex[0, i], :] = pX[sortIndex[0, i], :] * (1 + r1)  # 对自变量做一个随机变换
            #     X[sortIndex[0, i], :] = Bounds(X[sortIndex[0, i], :], lb, ub)  # 对超过边界的变量进行去除
            #     fit[sortIndex[0, i], 0] = objf(X[sortIndex[0, i], :])  # 算新的适应度值
            for i in range(pNum):
                r1 = np.random.rand(1)
                w0 = 1
                c = 0.9
                w = w0 * (c ** t)
                X[sortIndex[0, i], :] = pX[sortIndex[0, i], :] * np.exp(-(i) / (r1 * Max_iteration*w))  # 对自变量做一个随机变换
                hungry = np.random.rand(1)
                if hungry>0.9:
                    X[i, :] = lb + (ub - lb) * np.random.rand(1, dim)
                X[sortIndex[0, i], :] = Bounds(X[sortIndex[0, i], :], lb, ub)  # 对超过边界的变量进行去除
                fit[sortIndex[0, i], 0] = F22( X[sortIndex[0, i], :])  # 算新的适应度值
        elif r2 >= 0.8:  # 预警值较大，说明有捕食者出现威胁到了种群的安全，需要去其它地方觅食
            for i in range(pNum):
                Q = np.random.randn(1)  # 也可以替换成  np.random.normal(loc=0, scale=1.0, size=1)
                X[sortIndex[0, i], :] = pX[sortIndex[0, i], :] + Q * np.ones((1, dim))  # Q是服从正态分布的随机数。L表示一个1×d的矩阵
                X[sortIndex[0, i], :] = Bounds(X[sortIndex[0, i], :], lb, ub)
                fit[sortIndex[0, i], 0] = F22( X[sortIndex[0, i], :])
        bestII = np.argmin(fit[:, 0])
        bestXX = X[bestII, :]
        # max=np(np.sqrt(worse-bestX))
        #  这一部位为加入者（追随者）的位置更新
        for ii in range(N - pNum):
            i = ii + pNum
            A = np.floor(np.random.rand(1, dim) * 2) * 2 - 1
            sdis=np.empty(pNum)
            max = sys.maxsize
            for j in range(pNum):
                sdis[j] = np.sqrt(np.sum(np.square((X[sortIndex[0, i], :] - pX[sortIndex[0, j], :]))))



            #print(sdis)
            if i > N / 2:  # 这个代表这部分麻雀处于十分饥饿的状态（因为它们的能量很低，也就是适应度值很差），需要到其它地方觅食 已修改
                #t=random.randint(1,pNum)
                j = np.random.randint(0, pNum)
                Q = np.random.randn(1)  # 也可以替换成  np.random.normal(loc=0, scale=1.0, size=1)
                # X[sortIndex[0, i], :] = Q * np.exp(worse - pX[sortIndex[0, i], :] / np.square(i))

                X[sortIndex[0, i], :] = Q * np.exp(pX[sortIndex[0, j], :] - pX[sortIndex[0, i], :] / np.square(i))

            else:
                # print(sdis)
                # print("最小值")
                # print(sdis.min())
                # print(np.where(sdis==sdis.min())[0])

                j1=np.where(sdis==sdis.min())[0][0]  # 这一部分追随者是围绕最好的发现者周围进行觅食，其间也有可能发生食物的争夺，使其自己变成生产者 已修改
                    # j = np.random.randint(0, pNum)
                # print(j1)
                X[sortIndex[0, i], :] = pX[sortIndex[0, j1], :] + np.dot(np.abs(pX[sortIndex[0, i], :] - pX[sortIndex[0, j1], :]),
                                                        1 / (A.T * np.dot(A, A.T))) * np.ones((1, dim))
            X[sortIndex[0, i], :] = Bounds(X[sortIndex[0, i], :], lb, ub)
            fit[sortIndex[0, i], 0] = F22( X[sortIndex[0, i], :])

        # 这一部位为意识到危险（注意这里只是意识到了危险，不代表出现了真正的捕食者）的麻雀的位置更新
        # np.arange()函数返回一个有终点和起点的固定步长的排列，如[1,2,3,4,5]，起点是1，终点是5，步长为1。
        # 一个参数时，参数值为终点，起点取默认值0，步长取默认值1
        arrc = np.arange(len(sortIndex[0, :]))
        # c=np.random.shuffle(arrc)
        # 这个的作用是在种群中随机产生其位置（也就是这部分的麻雀位置一开始是随机的，意识到危险了要进行位置移动，
        #  处于种群外围的麻雀向安全区域靠拢，处在种群中心的麻雀则随机行走以靠近别的麻雀）
        c = np.random.permutation(arrc)  # 随机排列序列
        b = sortIndex[0, c[0:20]]
        z = np.random.randint(0, pNum)
        for j in range(len(b)):
            # sdis = np.empty(pNum)
            #
            # for S in range(pNum):
            #     sdis[j] = np.sqrt(np.sum(np.square((X[sortIndex[0, i], :] - pX[sortIndex[0, j], :]))))

            if pFit[sortIndex[0, b[j]], 0] > fMin:
                X[sortIndex[0, b[j]], :] = bestX + np.random.rand(1, dim) * np.abs(pX[sortIndex[0, b[j]], :] - bestX)
                # hungry = np.random.rand(1)
                # if hungry > 0.5:
                #     X[i, :] = lb + (ub - lb) * np.random.rand(1, dim)


            else:
                X[sortIndex[0, b[j]], :] = pX[sortIndex[0, b[j]], :] + (2 * np.random.rand(1) - 1) * np.abs(
                    pX[sortIndex[0, b[j]], :] - worse) / (pFit[sortIndex[0, b[j]]] - fmax + 10 ** (-50))
            X[sortIndex[0, b[j]], :] = Bounds(X[sortIndex[0, b[j]], :], lb, ub)
            fit[sortIndex[0, b[j]], 0] = F22(X[sortIndex[0, b[j]]])
        for i in range(N):

            if fit[i, 0] < pFit[i, 0]:
                pFit[i, 0] = fit[i, 0]
                pX[i, :] = X[i, :]
            if pFit[i, 0] < fMin:
                fMin = pFit[i, 0]

                bestX = pX[i, :]
        # print(fMin)
        # print("1111")
        # print(fMin)
        Convergence_curve[t] = fMin
        # print(fMin)
    print(bestX)
    #print(Convergence_curve)
    print('SRRNSSA is optimizing  "' + F22.__name__ )
    print("SRRNSSA迭代最小值")
    print(Convergence_curve.min())
    timerEnd = time.time()
    s.endTime = time.strftime("%Y-%m-%d-%H-%M-%S")
    s.executionTime = timerEnd - timerStart
    s.convergence = Convergence_curve
    s.optimizer = "SRRNSSA"
    s.objfname = F22.__name__
    thr1 = np.arange(len(Convergence_curve))
    #plt.plot(thr1, Convergence_curve)

    plt.xlabel('num')
    plt.ylabel('object value')
    plt.title('line')
    plt.show()
    return s

# X = np.random.randint(0,1000,(50,5))
SRRNSSA(2,500,10,50,100)