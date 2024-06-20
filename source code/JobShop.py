import machine
from job import Job
from machine import Machine
import random
from simpy.events import AnyOf, AllOf, Event
from collections import deque


class FJobShop:
    def __init__(self,
                 env,
                 job_list: deque,
                 machine_list,
                 machine_number: dict,
                 job_total_number,
                 can_insert_job
                 ):
        self.env = env
        self.job_list = job_list
        self.job_total_number = job_total_number
        self.machine_list = machine_list
        self.machine_num = len(machine_list)
        self.machine_number = machine_number
        self.machine_number_kind = len(self.machine_number)
        self.job_next_step_event = self.env.event()
        self.wait_machine_idle_event = self.env.event()
        self.job_next_step_process = self.env.process(self.job_next_step())
        self.over_job_list = deque([])
        self.job_insert_event = self.env.event()
        self.job_next_id = len(self.job_list) + 1
        self.can_insert_job = can_insert_job
        self.job_insert_process = None
        self.init()

    def init(self):
        for i in self.machine_list:
            i.jobshop = self
        if self.can_insert_job:
            self.job_insert_process = self.env.process(self.job_insert())

    def job_next_step(self):
        job_count = self.job_total_number
        while len(self.over_job_list) != job_count:
            if not self.job_list:
                yield self.wait_machine_idle_event
                continue
            job_selected = self.job_list[0]
            current_procedure = job_selected.get_current_procedure()
            current_machine_list = self.machine_number[current_procedure]
            machine_number = random.randint(0, len(current_machine_list) - 1)
            machine_selected_number = current_machine_list[machine_number]
            machine_selected = self.machine_list[machine_selected_number - 1]
            if machine_selected.put_job(job_selected):
                machine_selected.trigger_wait()
                self.job_list.popleft()
            else:
                yield self.wait_machine_idle_event

    def job_insert(self):
        while self.job_next_id <= self.job_total_number:
            timeout = random.randint(200, 500)
            print(f"工件插入 {self.env.now}  {timeout}")
            yield self.env.timeout(timeout)
            self.creat_random_job()

    def creat_random_job(self):
        job_type = random.randint(1, 3)
        job_count = random.randint(1, self.job_total_number - self.job_next_id + 1)
        li = [[100, 240, 230], [370, 260, 200], [120, 200, 230]]
        pro = [[1, 2, 3], [3, 1, 2], [2, 1, 3]]
        for i in range(job_count):
            job = Job(self.job_next_id, job_type, pro[job_type - 1], li[job_type - 1], self.env.now)
            self.job_next_id += 1
            self.job_list.append(job)
        print(f"插入工件个数{job_count} 工件类型 {job_type}")

    def machine_idle(self):
        self.wait_machine_idle_event.succeed()
        self.wait_machine_idle_event = self.env.event()

    def getJobEnvState(self, current_machine: machine.Machine):
        machine_feature = []
        machine_tardness = []
        machine_tard = 0.
        operation_num = 0.
        for machine in self.machine_list:
            machine.calculate_machine_ttardiness()
            machine_tardness.append(machine.ttardiness)
        machine_tardness = np.array(machine_tardness)
        machine_ave_tard = float(np.mean(machine_tardness)) if len(machine_tardness) != 0 else 0
        machine_std_tard = float(np.std(machine_tardness)) if len(machine_tardness) != 0 else 0
        machine_tard = current_machine.ttardiness
        operation_num = len(current_machine.process_list)
        machine_feature.append(machine_ave_tard)
        machine_feature.append(machine_std_tard)
        machine_feature.append(machine_tard)
        machine_feature.append(operation_num)
        task_feature = []
        for i in range(current_machine.machine_buffer_number_init):
            sum = current_machine.machine_buffer[
                i].rest_operation_num() if i < current_machine.get_machine_buffer_count() else 0
            task_feature.append(sum)
            time = current_machine.machine_buffer[
                i].get_job_process_time() if i < current_machine.get_machine_buffer_count() else 0
            task_feature.append(time)
        time_total = 0.
        num = len(current_machine.machine_buffer)
        completion_rate_list = []
        process_time_list = []
        for job in current_machine.machine_buffer:
            process_time_list.append(job.get_job_process_time())
            completion_rate_list.append(job.get_operation_completion_rate())
            time_total += job.get_job_process_time()
        max_time = max(process_time_list) if len(process_time_list)!=0 else 0
        min_time = min(process_time_list) if len(process_time_list)!=0 else 0
        max_time = max_time / time_total if time_total != 0 else 0.
        min_time = min_time / time_total if time_total != 0 else 0.
        time_avg = time_total / num if num != 0 else 0.
        time_avg = time_avg / time_total if time_total != 0 else 0.
        completion_rate_list = np.array(completion_rate_list)
        completion_rate_avg = float(np.mean(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        completion_rate_std = float(np.std(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        task_feature.append(min_time)
        task_feature.append(max_time)
        task_feature.append(time_avg)
        task_feature.append(completion_rate_avg)
        task_feature.append(completion_rate_std)
        sum1 = 0.
        sum2 = 0.
        for job in self.job_list:
            sum1 += job.get_job_plan_count()
            sum2 += job.current_procedure_index + 1 if job.current_procedure_index >= 0 else job.get_job_plan_count()
        val1 = 1 - len(self.job_list) / (self.job_next_id - 1)
        val2 = len(self.over_job_list) / (self.job_next_id - 1)
        val3 = sum2 / sum1 if sum1 != 0 else 0
        task_feature.append(val1)
        task_feature.append(val2)
        task_feature.append(val3)
        state = []
        state.extend(machine_feature)
        state.extend(task_feature)
        return state

    def check_is_done(self):
        return 1 if len(self.over_job_list) == self.job_total_number else 0

    def get_total_time(self):
        time_total = 0
        for job in self.job_list:
            time_total += job.get_total_Processing_Time()
        return time_total

    def add_job_shop(self, job):
        self.job_list.appendleft(job)
    def add_end_job_shop(self, job):
        self.over_job_list.appendleft(job)


import collections
import random
from job import Job
from machine import Machine
import numpy as np
import sys


class JobEnvironment:
    def __init__(self, dispathingruleslist):
        self.queueList = collections.deque()
        self.joblist = order_creat_method(30, 12, 11, 17)
        self.queueList.extend(self.joblist)
        self.action_space = []
        self.machine_list = []
        self.machine_list.append(Machine(1, 1, 4, 1))
        self.machine_list.append(Machine(1, 2, 4, 1))
        self.machine_list.append(Machine(2, 3, 4, 1))
        self.machine_list.append(Machine(2, 4, 4, 1))
        self.machine_list.append(Machine(3, 5, 4, 1))
        self.machine_list.append(Machine(3, 6, 4, 1))
        self.machine_num = 6
        self.this_time = 0
        self.action = None
        self.dispatchingrules = dispathingruleslist
        self.chooseList = self.dispatchingrules.rules
        self.done = False
        self.reward = 0
        self.jobEnvState = []
        self.doneList = []
        self.minMachineList = []
        self.rewardlist = []
        self.reward1 = 0.

    def resetEnv(self):
        self.queueList = collections.deque()
        self.joblist = order_creat_method(30, 12, 11, 17)
        self.queueList.extend(self.joblist)
        self.this_time = 0
        self.action = None
        self.done = False
        self.reward = 0
        self.jobEnvState = []
        self.doneList = []
        self.minMachineList = []
        self.reward = 0.
        for machine in self.machine_list:
            machine.rest()
        self.queueToProcess()
        machine_list_temp = []
        for machine in self.machine_list:
            if not machine.buffer_is_blank():
                machine_list_temp.append(machine)
        state = self.getJobEnvState(machine_list_temp)
        return state

    def getJobEnvState(self, minMachineList):
        machine_feature = []
        machine_tardiness = []  #ttardiness,utilist
        machine_tard = 0.     #tard,util
        operation_num = 0.
        for machine in self.machine_list:
            machine.calculate_machine_ttardiness(self.this_time)
            machine_tardiness.append(machine.ttardiness)
        machine_tardlist = np.array(machine_tardiness)
        machine_ave_tard = float(np.mean(machine_tardlist)) if len(machine_tardlist) != 0 else 0
        machine_std_tard = float(np.std(machine_tardlist)) if len(machine_tardlist) != 0 else 0
        for machine in minMachineList:
            machine_tard += machine.ttardiness
            operation_num += len(machine.process_list)
        machine_tard = float(machine_tard / len(minMachineList)) if len(minMachineList) != 0 else 0
        operation_num = float(operation_num / len(minMachineList)) if len(minMachineList) != 0 else 0
        machine_feature.append(machine_ave_tard)
        machine_feature.append(machine_std_tard)
        machine_feature.append(machine_tard)
        machine_feature.append(operation_num)
        task_feature = []
        for i in range(4):
            sum = 0.
            time = 0.
            for machine in minMachineList:
                num = machine.machine_buffer[i].rest_operation_num() if i < machine.get_machine_buffer_number() else 0
                timeval = machine.machine_buffer[
                    i].get_job_process_time() if i < machine.get_machine_buffer_number() else 0
                sum += num
                time += timeval
            sum = sum / len(minMachineList) if len(minMachineList) != 0 else 0
            time = time / len(minMachineList) if len(minMachineList) != 0 else 0
            task_feature.append(sum)
            task_feature.append(time)
        time_total = 0.
        max = 0.
        min = 0.
        num = 0.
        completion_rate_list = []
        for machine in minMachineList:
            time_total1 = 0.
            max1 = -1
            min1 = sys.maxsize
            for job in machine.machine_buffer:
                if max1 < job.get_job_process_time(): max1 = job.get_job_process_time()
                if min1 > job.get_job_process_time(): min1 = job.get_job_process_time()
                time_total1 += job.get_job_process_time()
                completion_rate_list.append(job.get_operation_completion_rate())
            max += max1
            min += min1
            time_total += time_total1
            num += len(machine.machine_buffer)

        max = max / time_total if time_total != 0 else 0.
        min = min / time_total if time_total != 0 else 0.
        time_avg = time_total / num if num != 0 else 0.
        time_avg = time_avg / time_total if time_total != 0 else 0.
        completion_rate_list = np.array(completion_rate_list)
        completion_rate_avg = float(np.mean(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        completion_rate_std = float(np.std(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        task_feature.append(min)
        task_feature.append(max)
        task_feature.append(time_avg)
        task_feature.append(completion_rate_avg)
        task_feature.append(completion_rate_std)
        sum1 = 0.
        sum2 = 0.
        for job in self.joblist:
            sum1 += job.get_job_plan_count()
            sum2 += job.current_procedure_index if job.current_procedure_index > 0 else job.get_job_plan_count()
        val1 = (len(self.joblist) - len(self.queueList)) / len(self.joblist)
        val2 = len(self.doneList) / len(self.joblist)
        val3 = sum2 / sum1
        task_feature.append(val1)
        task_feature.append(val2)
        task_feature.append(val3)
        state = []
        state.extend(machine_feature)
        state.extend(task_feature)

        return state

    def getJobEnvState2(self, minMachineList):
        machine_feature = []
        machine_tardiness = []
        machine_tard = 0.
        operation_num = 0.
        for machine in self.machine_list:
            machine.calculate_machine_ttardiness(self.this_time)
            machine_tardiness.append(machine.ttardiness)
        machine_feature.extend(machine_tardiness)
        machine_tardiness = np.array(machine_tardiness)
        machine_ave_tard = float(np.mean(machine_tardiness)) if len(machine_tardiness) != 0 else 0
        machine_std_tard = float(np.std(machine_tardiness)) if len(machine_tardiness) != 0 else 0
        for machine in minMachineList:
            machine_tard += machine.ttardiness
            operation_num += len(machine.process_list)
        machine_tard = float(machine_tard / len(minMachineList)) if len(minMachineList) != 0 else 0
        operation_num = float(operation_num / len(minMachineList)) if len(minMachineList) != 0 else 0
        machine_feature.append(machine_ave_tard)
        machine_feature.append(machine_std_tard)
        machine_feature.append(machine_tard)
        machine_feature.append(operation_num)
        task_feature = []
        for i in range(4):
            sum = 0.
            time = 0.
            for machine in minMachineList:
                num = machine.machine_buffer[i].rest_operation_num() if i < machine.get_machine_buffer_number() else 0
                timeval = machine.machine_buffer[
                    i].get_job_process_time() if i < machine.get_machine_buffer_number() else 0
                sum += num
                time += timeval
            sum = sum / len(minMachineList) if len(minMachineList) != 0 else 0
            time = time / len(minMachineList) if len(minMachineList) != 0 else 0
            task_feature.append(sum)
            task_feature.append(time)
        for machine in minMachineList:
            maxTime = -1
            minTime = sys.maxsize
            for i in range(4):
                candidateMaxTime = machine.machine_buffer[
                    i].get_Remaining_Processing_Time() if i < machine.get_machine_buffer_number() else 0
                candidateMinTime = machine.machine_buffer[
                    i].get_Remaining_Processing_Time() if i < machine.get_machine_buffer_number() else 0
                if candidateMaxTime > maxTime:
                    maxTime = candidateMaxTime
                if candidateMinTime < minTime:
                    minTime = candidateMinTime

        time_total = 0.
        max = 0.
        min = 0.
        num = 0.
        completion_rate_list = []
        for machine in minMachineList:
            time_total1 = 0.
            max1 = -1
            min1 = sys.maxsize
            for job in machine.machine_buffer:
                if max1 < job.get_job_process_time(): max1 = job.get_job_process_time()
                if min1 > job.get_job_process_time(): min1 = job.get_job_process_time()
                time_total1 += job.get_job_process_time()
                completion_rate_list.append(job.get_operation_completion_rate())
            max += max1
            min += min1
            time_total += time_total1
            num += len(machine.machine_buffer)

        max = max / time_total if time_total != 0 else 0.
        min = min / time_total if time_total != 0 else 0.
        time_avg = time_total / num if num != 0 else 0.
        time_avg = time_avg / time_total if time_total != 0 else 0.
        completion_rate_list = np.array(completion_rate_list)
        completion_rate_avg = float(np.mean(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        completion_rate_std = float(np.std(completion_rate_list)) if len(completion_rate_list) != 0 else 0
        task_feature.append(min)
        task_feature.append(max)
        task_feature.append(time_avg)
        task_feature.append(completion_rate_avg)
        task_feature.append(completion_rate_std)
        sum1 = 0.
        sum2 = 0.
        for job in self.joblist:
            sum1 += job.get_job_plan_count()
            sum2 += job.current_procedure_index if job.current_procedure_index > 0 else job.get_job_plan_count()
        val1 = (len(self.joblist) - len(self.queueList)) / len(self.joblist)
        val2 = len(self.doneList) / len(self.joblist)
        val3 = sum2 / sum1
        val4 = len(self.joblist) - len(self.queueList)
        task_feature.append(val1)
        task_feature.append(val2)
        task_feature.append(val3)
        task_feature.append(val4)
        state = []
        state.extend(machine_feature)
        state.extend(task_feature)

        return state

    def test_machine_tolist(self):
        for machine in self.machine_list:
            print("***", machine.machine_id, "***")
            for job in machine.machine_buffer:
                print(job)

    def test_machine_process_list(self):
        for machine in self.machine_list:
            print("##", machine.machine_id, "##")
            for t in machine.process_list:
                print(t)

    def nextStep(self, action):
        time_total = 0.
        self.action = action
        flag = False
        for job in self.joblist:
            time_total += job.get_total_Processing_Time()
        self.reward3 = time_total / (len(self.machine_list) * self.this_time) if self.this_time != 0 else 0.
        self.reward1 = self.reward3

        for machine in self.machine_list:
            if machine.machine_buffer_number < 4 and not machine.is_busy:
                self.chooseJobToProcess(action, machine.machine_buffer, self.chooseList, machine)
                flag = True

        while flag and not self.done:
            self.this_time, self.minMachineList = self.findMinTime()
            time_total = 0.
            for job in self.joblist:
                time_total += job.get_total_Processing_Time()
            self.reward3 = time_total / (len(self.machine_list) * self.this_time)
            self.reward = self.reward3 - self.reward1

            self.jobEnvState = self.getJobEnvState(self.minMachineList)
            self.queueToProcess()
            for machine in self.machine_list:
                if machine.machine_buffer_number < 4 and not machine.is_busy:
                    flag = False

            if len(self.queueList) == 0:
                sum1 = 0
                for machine in self.machine_list:
                    if machine.buffer_is_blank():
                        self.done = True
                        sum1 += 1
                if sum1 != self.machine_num:
                    self.done = False
        self.rewardlist.append(self.reward)
        return self.jobEnvState, self.reward, self.done

    def queueToProcess(self):
        while True:
            if len(self.queueList) == 0:
                return False
            current_job = self.queueList.popleft()
            machine_type = current_job.get_current_procedure()
            if machine_type == -1:
                continue
            machine_to_process = self.chooseMachineToProcess(machine_type)
            if machine_to_process is not None:
                machine_to_process.machine_buffer.append(current_job)
                machine_to_process.machine_buffer_number = machine_to_process.machine_buffer_number - 1 \
                    if machine_to_process.machine_buffer_number > 0 else 0
            else:
                self.queueList.appendleft(current_job)
                break
        return True

    def findMinTime(self):

        minTime = sys.maxsize
        minMachine = None
        minMachineList = []
        for machine in self.machine_list:
            if machine.current_processing_job is not None:
                if machine.current_processing_job.over_time < minTime:
                    minTime = machine.current_processing_job.over_time
                    minMachine = machine
                    if len(minMachineList) > 0: minMachineList.clear()
                elif machine.current_processing_job.over_time == minTime:
                    minMachineList.append(machine)
        minMachineList.append(minMachine)
        if minMachine is None:
            return self.this_time, minMachineList
        for machine in minMachineList:
            machine.is_busy = False
            machine.machine_buffer.remove(machine.current_processing_job)
            machine.add_machine_buffer_number()
            machine.append_process_list(
                (machine.current_processing_job.job_id, machine.current_processing_job.current_procedure_index + 1,
                 machine.current_processing_job.start_time, machine.current_processing_job.over_time))
            machine.current_processing_job.is_lock = False
            machine.current_processing_job.next_procedure_index()
            if machine.current_processing_job.current_procedure_index != -1:
                self.queueList.appendleft(machine.current_processing_job)
            else:
                self.doneList.append(machine.current_processing_job)
            machine.current_processing_job = None
        return minTime, minMachineList

    def chooseJobToProcess(self, action, buffer, chooselist, machine):

        curmethod = chooselist[action]
        curjob = curmethod(buffer)
        machine.current_processing_job = curjob
        machine.is_busy = True
        curjob.set_start_time(self.this_time)
        curjob.set_machine(machine)
        curjob.is_lock = True

    def chooseMachineToProcess(self, type):

        canProcessMachineList = []
        for machine in self.machine_list:
            if machine.machine_buffer_number != 0 and machine.machine_type == type:
               canProcessMachineList.append(machine)

        machinetoprocess = None
        if len(canProcessMachineList) == 0:
            return machinetoprocess
        time = sys.maxsize
        for machine in canProcessMachineList:
            if machine.can_process_time < time:
                machinetoprocess = machine
                time = machinetoprocess.can_process_time
            elif machine.can_process_time == time:
                machinetoprocess = machine if machine.machine_buffer_number > machinetoprocess.machine_buffer_number else machinetoprocess
                time = machinetoprocess.can_process_time
        return machinetoprocess



def order_creat_method(count):
    joblist = []
    jobCount = count
    jobCount1 = int(jobCount * random.uniform(0, 0.6))
    jobCount2 = int((jobCount - jobCount1) * random.uniform(0.3, 0.7))
    jobCount3 = jobCount - jobCount1 - jobCount2
    job_process_time1 = [random.randint(20, 50), random.randint(30, 60), random.randint(10, 40)]
    job_process_time2 = [random.randint(30, 60), random.randint(40, 70)]
    job_process_time3 = [random.randint(10, 80)]
    for i in range(jobCount1):
        job = Job(0, 1, [1, 2, 3], job_process_time1, 0)
        joblist.append(job)
    for i in range(jobCount2):
        job = Job(0, 2, [1, 2], job_process_time2, 0)
        joblist.append(job)
    for i in range(jobCount3):
        job = Job(0, 3, [2], job_process_time3, 0)
        joblist.append(job)
    random.shuffle(joblist)


def order_creat_method(count, jobCount1, jobCount2, jobCount3):
    joblist = []
    jobCount = count
    jobCount1 = jobCount1
    jobCount2 = jobCount2
    jobCount3 = jobCount3
    job_process_time1 = [149, 22, 34, 100]
    job_process_time2 = [37, 300, 20]
    job_process_time3 = [125, 20, 70, 150]

    for i in range(jobCount1):
        job = Job(0, 1, [1, 2, 3, 1], job_process_time1, 0)
        joblist.append(job)
    for i in range(jobCount2):
        job = Job(0, 2, [1, 3, 2], job_process_time2, 0)
        joblist.append(job)
    for i in range(jobCount3):
        job = Job(0, 3, [2, 1, 3, 2], job_process_time3, 0)
        joblist.append(job)

    for i, job in enumerate(joblist):
        job.job_id = i + 1

    return joblist


def split_order_method():
    pass
