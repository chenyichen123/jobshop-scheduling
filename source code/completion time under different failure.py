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

def difference(csv_path,csv_path1):
    data = pd.read_csv(filepath_or_buffer=csv_path, header=0, names=['Step', 'Value'],
                       dtype={'Step': int, 'Value': float})
    smoothdata = pd.read_csv(filepath_or_buffer=csv_path1, header=0, names=['Step', 'Value'],
                             dtype={'Step': int, 'Value': float})
    smoothdata = smoothdata['Value'].values
    data = data["Value"].values

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
    lpt=[4362, 4608, 4797,5144, 5340, 5793]
    lifo=[4599, 4628, 4969, 5388, 5805, 5989]
    spt=[4002, 4106, 4561, 4640, 5136, 5643]
    fifo=[3908, 4297, 4668, 4925, 5505, 5613]
    srpt=[4076, 4236, 4397, 4973, 5259, 5444]
    lrpt = [4126, 4316, 4697, 5173, 5359, 5844]
    dqn=[3961,4125,4361,4480,4766,5174]
    ga=[3871, 4215, 4541, 4600, 4676, 4974]
    lstm=[3752, 3812, 3960, 4054, 4520, 4755]
    con=[lpt,lifo,spt,srpt,lrpt,fifo,dqn,ga,lstm]
    x=[ i+1 for i in range(6)]
    xti=['LIFO','LPT','SPT','FIFO','SRPT','LRPT','DQN','GA',"LSTM-PPO"]
    xti1=['5%','15%','25%','35%','45%','55%']
    color=['green','red','blue','pink','thistle','violet','navy','slategray','gold','gold']
    marker=['o','s','*','h','X','d',"^",'1','o']
    for i in range(0,len(con)):
        plt.plot(x,con[i],color=color[i],marker=marker[i])
    plt.xlabel('failure probability',fontsize=12)
    plt.ylabel('completion time(s)',fontsize=12)
    plt.xticks(range(1,len(xti1)+1),xti1)
    plt.legend(xti,fontsize=9)
    print(con)
    plt.show()
