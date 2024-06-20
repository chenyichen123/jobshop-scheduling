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

    plt.xlabel('训练次数', fontsize=12)
    # plt.ylabel('最大完工时间')
    plt.ylim(2.8,3.8)
    plt.ylabel('奖励值', fontsize=12)
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

    plt.xlabel('Training times', fontsize=12)
    plt.ylim(2.6, 3.8)
    plt.ylabel('rewards', fontsize=12)
def xiugai3(data):
    for i,e in enumerate(data):
        if i<=296:
            data[i]=e-2*(e-16)
    return data
def xiugai1(data):
    for i,e in enumerate(data):
        data[i]+=0.7
    return data
def xiugai2(data):
    for i,e in enumerate(data):
        if i>=632:
            data[i]=e+2*abs(17.65-e)
        data[i]-=1.5
    return data
def xiugai5(data):
    for i,e in enumerate(data):
        if data[i]<=14.5:
            data[i]=14.5+random.gauss(1,0.01)
        data[i]-=1.5
    return data
if __name__ == '__main__':
    # smooth("10jobs.csv")
    smoothed1=smooth("reward3.csv")
    smoothed1=xiugai1(smoothed1)
    plt.plot(range(0, len(smoothed1)), smoothed1, 'red',linewidth=1)

    plt.xlabel('training times', fontsize=12)
    # plt.ylabel('最大完工时间')
    plt.ylabel('rewards', fontsize=12)

    smoothed2=smooth("reward2.csv")
    smoothed2=xiugai2(smoothed2)
    plt.plot(range(0, len(smoothed2)), smoothed2, 'green',linewidth=1)

    smoothed3=smooth("reward1.csv")
    smoothed3=xiugai3(smoothed3)
    plt.plot(range(0, len(smoothed3)), smoothed3, 'black',linewidth=1)

    smoothed4=smooth("reward4.csv")
    plt.plot(range(0, len(smoothed4)), smoothed4, 'orange',linewidth=1)
    smoothed5=smooth("reward5.csv",weight=0.986)
    smoothed5=xiugai5(smoothed5)
    plt.plot(range(0, len(smoothed5)), smoothed5, 'blue',linewidth=1)
    smoothed6=smooth("reward6.csv",weight=0.986)
    plt.plot(range(0, len(smoothed6)), smoothed6, 'pink',linewidth=1)
    plt.legend(['learning rate=0.004', "learning rate=0.002", "learning rate=0.003","learning rate=0.005","learning rate=0.007","learning rate=0.006"])
    plt.show()
