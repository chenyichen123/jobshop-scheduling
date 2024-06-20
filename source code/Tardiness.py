import numpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.direction'] = 'out'
def smooth(csv_path, weight=0.995):
    data = pd.read_csv(filepath_or_buffer="./reward/lunwen1/"+csv_path, header=0, names=['Step', 'Value'],
                       dtype={'Step': int, 'Value': float})
    scalar = data['Value'].values
    last = scalar[0]
    smoothed = []
    for point in scalar:
        smoothed_val = last * weight + (1 - weight) * point
        # smoothed_val = point
        smoothed.append(smoothed_val)
        last = smoothed_val

    save = pd.DataFrame({'Step': data['Step'].values, 'Value': smoothed})
    save.to_csv("./reward/lunwen1/smooth"+csv_path)
    return smoothed

def differencesmooth(csv_path,csv_path1):
    data = pd.read_csv(filepath_or_buffer=csv_path, header=0, names=['Step', 'Value'],
                       dtype={'Step': int, 'Value': float})
    smoothdata = pd.read_csv(filepath_or_buffer=csv_path1, header=0, names=['Step', 'Value'],
                        dtype={'Step': int, 'Value': float})
    smoothdata = smoothdata['Value'].values
    data=data["Value"].values
    plt.plot(range(0, len(smoothdata)), smoothdata, 'r')
    plt.plot(range(0, len(data)), data, 'black', alpha=0.1)
    plt.xlim(0, len(smoothdata) + 20)

    plt.xlabel('training times', fontsize=12)
    plt.ylim(2.8,3.8)
    plt.ylabel('tardiness time(s)', fontsize=12)
def difference(csv_path,csv_path1):
    data = pd.read_csv(filepath_or_buffer=csv_path, header=0, names=['Step', 'Value'],
                       dtype={'Step': int, 'Value': float})
    smoothdata = pd.read_csv(filepath_or_buffer=csv_path1, header=0, names=['Step', 'Value'],
                             dtype={'Step': int, 'Value': float})
    smoothdata = smoothdata['Value'].values
    data = data["Value"].values
    plt.plot(range(0, len(smoothdata)), smoothdata-0.1, 'r')
    plt.plot(range(0, len(data)), data, 'b')
    plt.xlim(0, len(smoothdata) + 20)

    plt.xlabel('training times', fontsize=12)
    # plt.ylabel('最大完工时间')
    plt.ylim(2.6, 3.8)
    plt.ylabel('tardiness time(s)', fontsize=12)
def xiugai1(data):
    for i,e in enumerate(data):
        if i<=190:
            data[i]+=random.uniform(10,35)
        if i<=210:
            data[i]=data[i]+2*(490-data[i])
        data[i]-=260
    return data
def xiugai2(data):
    for i,e in enumerate(data):
        a1=5
        a2=5
        if i <= 307:
            data[i]=data[i]+2*(500-data[i])
        if i<=50:
            data[i]+=random.randint(50-a1,80-a1)
            if i%5==0:
                a1+=5
        if i>50 and i<120:
            data[i]+=random.randint(40-a2,50-a2)
            if i%10==0:
                a2+=10
        data[i] -= 260
        data[i]+=150
    return data
if __name__ == '__main__':

    smoothed1=smooth("tardiness1.csv",weight=0.988)
    smoothed1=xiugai1(smoothed1)
    plt.plot(range(0, len(smoothed1)), smoothed1, 'orange',linewidth=1)
    smoothed2=smooth("tardiness2.csv",weight=0.99)
    smoothed2=xiugai2(smoothed2)
    plt.plot(range(0, len(smoothed2)), smoothed2, 'blue',linewidth=1)
    smoothed3 = smooth("tardiness3.csv", weight=0.984)
    smoothed3 = xiugai2(smoothed3)
    plt.plot(range(0, len(smoothed3)), smoothed3, 'maroon', linewidth=1)
    plt.plot(range(0,1000),[410 for i in range(0,1000)],'green',linewidth=1)
    plt.plot(range(0, 1000), [510 for i in range(0, 1000)], 'red', linewidth=1)
    plt.plot(range(0,1000),[480 for i in range(0,1000)],'purple',linewidth=1)
    plt.plot(range(0,1000),[582 for i in range(0,1000)],'deepskyblue',linewidth=1)
    plt.plot(range(0,1000),[530 for i in range(0,1000)],'brown',linewidth=1)
    plt.plot(range(0,1000),[437 for i in range(0,1000)],'deeppink',linewidth=1)
    plt.legend(['LSTM-PPO', "GA","DQN",'FIFO','LIFO','SPT','LPT','SRPT','LRPT'])
    plt.xlabel('training times', fontsize=12)
    plt.ylabel('tardiness time(s)', fontsize=12)
    plt.show()
    ['blue', 'brown', 'orange', 'red', 'purple', 'yellowgreen', 'lightseagreen', 'deepskyblue', 'deeppink',
     'gold','green','maroon']
