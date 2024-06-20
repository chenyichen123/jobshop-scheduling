#该代码生成结果甘特图，但是为DQN生成，和LSTM-PPO没什么关系
import JobShop
from job import Job
from machine import Machine
import random
import simpy
from collections import deque
import matplotlib.pyplot as plt
from adjustText import adjust_text
from dispatchingrules import DispatchingRules
from torch.utils.tensorboard import SummaryWriter
from RLDQN import DQN
from RLDQN import DDQN
from RLDQN import D3QN
import datetime
############  全局参数设置  ###############

# 是否允许机器发生故障
CAN_BROKEN = False
# 是否允许订单的插入
CAN_INSERT_JOB = False
# 使用的强化学习方法
# alpha=0.003 20221025-132632
# alpha=0.001 20221025-131123
# alpha=0.005 20221025-133558
# alpha=0.01 action_dim=10 20221025-135054
# alpha=0.001 action_dim=10 20221025-142600
# alpha=0.001 20221025-221827 tanh DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=10,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
#  20221026-144550 tanh DRL = D3QN(alpha_=0.0001,state_dim=20,action_dim=10,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
#20221026-152811 20221026-151512 DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=10,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
#20221027-104144 DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=5,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
# 20221209-152845 DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=5,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
# 20221027 - 182118 DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=8,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
DRL = DDQN(alpha_=0.001,state_dim=20,action_dim=8,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)#20240427
# DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=8,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
# 20221209-145724 DRL = D3QN(alpha_=0.001,state_dim=20,action_dim=10,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
# 20221209-183120DRL = D3QN(alpha_=0.003,state_dim=20,action_dim=10,fc1_dim=128,fc2_dim=64,fc3_dim=32,fc4_dim=16,ckpt_dir=None)
# 训练的步数
EPISODE = 8000


#########################################
def creat_job(count, init_job_count, jobCount1=0, jobCount2=0, jobCount3=0):
    '''
       创建订单，
       :param count: 工件总数
       :param jobCount1: 工件1数量
       :param jobCount2: 工件2数量
       :param jobCount3: 工件3数量
       :return:工件列表
       '''
    # 加工时间
    process_time_list = [[100, 250, 240], [370, 300, 200], [120, 200, 230]]
    #process_time_list = [[200, 250, 240], [370, 300], [170, 230]]
    # 法兰 轴 板
    #precedure_list = [[1, 2, 3], [1, 2], [2, 3]]
    precedure_list = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
    joblist = []
    jobCount = count
    # init_job_count = random.randint(1, count)
    jobCount1 = random.randint(1, int(init_job_count / 3)) if jobCount1 == 0 else jobCount1
    jobCount2 = random.randint(1, int(init_job_count / 3)) if jobCount2 == 0 else jobCount2
    jobCount3 = init_job_count - jobCount1 - jobCount2 if jobCount3 == 0 else jobCount3

    for i in range(jobCount1):
        job = Job(0, 1, precedure_list[0], process_time_list[0], 0)
        joblist.append(job)
    for i in range(jobCount2):
        job = Job(0, 2, precedure_list[1], process_time_list[1], 0)
        joblist.append(job)
    for i in range(jobCount3):
        job = Job(0, 3, precedure_list[2], process_time_list[2], 0)
        joblist.append(job)
    # 随机打散
    # todo:这个地方后面要根据情况来排序
    # random.shuffle(joblist)
    # 填写工件的编号
    for i, job in enumerate(joblist):
        job.job_id = i + 1

    return deque(joblist)


def gantt(flow, machinecount):
    #colors = ['violet', 'brown', 'orange', 'red', 'purple', 'yellowgreen', 'deeppink', 'deepskyblue', 'lightseagreen','gold']
    colors = ['#FFD700', '#FFFF00','#FFA500', '#FF0000', '#FFC0CB', '#A52A2A', '#006400', '#808080', '#87CEEB', '#00CED1', '#FFB451', '#A0522D',
             '#FFE4B5', '#FF6347', '#FF69B4', '#C0C0C0', '#00BFFF', '#008000', '#800080', '#00CED1' ]
    for j in range(machinecount):
        for i in range(len(flow[j])):
            width = flow[j][i]
            plt.barh(j + 1, width[3] - width[2], 0.5, left=width[2], facecolor=colors[width[0] % 20],
                     edgecolor='black')
            adjust_text(
                [plt.text(width[2] + 0.8, j + 0.85, 'J%s' % (width[0]), color="black", size=13)], )
    plt.show()


def creat_machine():
    rules = DispatchingRules()
    # 是否允许机器故障
    can_broken = 0

   # m1 = Machine(env, 1, 1, 4, 1, rules, can_broken, DRL)
   # m2 = Machine(env, 1, 2, 4, 1.2, rules, can_broken, DRL)
   # m3 = Machine(env, 2, 3, 4, 1, rules, can_broken, DRL)
   # m4 = Machine(env, 2, 4, 4, 0.9, rules, can_broken, DRL)
   # m5 = Machine(env, 3, 5, 4, 1, rules, can_broken, DRL)
   # m6 = Machine(env, 3, 6, 4, 1.3, rules, can_broken, DRL)
    m1 = Machine(env, 1, 1, 4, 1, rules, can_broken, DRL)
    m2 = Machine(env, 1, 2, 4, 1.2, rules, can_broken, DRL)
    m3 = Machine(env, 2, 3, 4, 1, rules, can_broken, DRL)
    m4 = Machine(env, 2, 4, 4, 0.9, rules, can_broken, DRL)
    m5 = Machine(env, 3, 5, 4, 1, rules, can_broken, DRL)
    m6 = Machine(env, 3, 6, 4, 1.3, rules, can_broken, DRL)
    lism = []
    lism.append(m1)
    lism.append(m2)
    lism.append(m3)
    lism.append(m4)
    lism.append(m5)
    lism.append(m6)
    # 机器的分类序号
    machine_number = {1: [1, 2], 2: [3, 4], 3: [5, 6]}
    return lism, machine_number


def run_fjsp():
    global env, jobshop
    job_total_number = 20
    env = simpy.Environment()
    lisa = creat_job(job_total_number, 20, 4, 8, 8)
    #共20个零件，按3种类型，分别为4个、8个、8个
    # 生成机床对象和每种机床的编号从1开始
    lism, machine_number = creat_machine()
    jobshop = JobShop.FJobShop(env, lisa, lism, machine_number, job_total_number, CAN_INSERT_JOB)
    env.run()
    flow = []
    makespan = 0
    for mac in lism:
        mac_process_list = mac.process_list
        print(mac_process_list)
        flow.append(mac_process_list)
        if len(mac_process_list) != 0:
            makespan = max(makespan, mac_process_list[-1][-1])
    print(makespan)
    return makespan,flow



def run():
    current_time=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    writer = SummaryWriter('./log/'+current_time)
    for episode in range(EPISODE):
        # 启动环境初始化,工件，机器，但是算法不初始化
        makespan,_=run_fjsp()
        sum = DRL.sum
        DRL.reward_list.append(sum)
        DRL.sum = 0
        DRL.reward_prev = 0
        writer.add_scalar("reward", sum, global_step=episode)
        writer.add_scalar("maskespan", makespan, global_step=episode)
        print(f"{episode}  ----  {sum}")
    for i in range(len(DRL.loss_recorder)):
        writer.add_scalar('loss',DRL.loss_recorder[i],global_step=i)
    print(DRL.actions_recorder)
    reco=total(DRL.actions_recorder)
    print(reco)
    print("schedule over")
def run2():
    makespan1=100000
    flow1=[]
    # for episode in range(20):
    #     makespan,flow = run_fjsp()
    #     if 3200<makespan<3300:
    #         flow1=flow
    #         makespan1=makespan
    for episod in range(200):
        makespan,flow=run_fjsp()
        if makespan<makespan1:
            flow1=flow
            makespan1=makespan
    print(flow1)
    print(makespan1)
    gantt(flow1, machinecount=6)

def total(actions_recorder):
    totalsum=sum(actions_recorder)
    lis=[]
    for i,e in enumerate(actions_recorder):
        lis.append(e/totalsum)
    return lis
if __name__ == '__main__':
    # 运行车间仿真
    run2()
