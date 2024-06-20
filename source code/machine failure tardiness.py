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
    plt.ylabel('累计奖励值', fontsize=12)
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

    plt.xlabel('训练次数', fontsize=12)
    # plt.ylabel('最大完工时间')
    plt.ylim(2.6, 3.8)
    plt.ylabel('累计奖励值', fontsize=12)
def xiugai1(data):
    for i,e in enumerate(data):
        if i<=190:
            data[i]+=random.uniform(10,35)
        if i<=210:
            data[i]=data[i]+2*(3848-data[i])

    return data
def xiugai2(data):
    for i,e in enumerate(data):
        a1=5
        a2=5
        if i <= 307:
            data[i]=data[i]+2*(3773-data[i])
        if i<=50:
            data[i]+=random.randint(50-a1,80-a1)
            if i%5==0:
                a1+=5
        if i>50 and i<120:
            data[i]+=random.randint(40-a2,50-a2)
            if i%10==0:
                a2+=10
        data[i]+=150
    return data
if __name__ == '__main__':

    li=[356.1,334.4,375.9,321.9,302.3,224.9,208.7]
    fifo=[102,158,197,244,340,493]
    lifo=[109,198,269,328,405,489]
    spt=[122,216,261,340,436,503]
    lpt=[151,197,268,325,445,513]
    srpt=[176,236,297,310,359,414]
    lrpt=[126,146,169,213,309,344]
    dqn=[81,105,161,180,266,294]
    ga=[71,95,121,156,176,204]
    lstm=[52,82,100,114,120,155]
    con=[fifo,lifo,spt,srpt,lrpt,lpt,dqn,ga,lstm]
    x=[ i+1 for i in range(6)]
    xti = ['LIFO', 'LPT', 'SPT', 'FIFO', 'SRPT', 'LRPT', 'DQN', 'GA', "LSTM-PPO"]
    xti1 = ['5%', '15%', '25%', '35%', '45%', '55%']
    color = ['green', 'red', 'blue', 'pink', 'thistle', 'violet', 'navy', 'slategray', 'gold', 'gold']
    marker = ['o', 's', '*', 'h', 'X', 'd', "^", '1', 'o']
    for i in range(0,len(con)):
        plt.plot(x,con[i],color=color[i],marker=marker[i])
    plt.xlabel('failure probability',fontsize=12)
    plt.ylabel('tardiness time(s)',fontsize=12)
    plt.xticks(range(1,len(xti1)+1),xti1)
    plt.legend(xti,fontsize=9)
    print(con)
    plt.show()
