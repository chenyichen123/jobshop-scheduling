import random
import job


class Machine:

    def __init__(self,
                 env,
                 type,
                 machine_id,
                 buffer_number,
                 process_factor,
                 dispatchingrules,
                 broken_signal=False,
                 DRL=None
                 ):
        self.env = env
        self.machine_type = type
        self.machine_id = machine_id
        self.machine_buffer_number_init = buffer_number
        self.machine_buffer_count = 0
        self.machine_buffer = []
        self.current_processing_job = None
        self.process_factor_init = process_factor
        self.process_factor = process_factor
        self.can_process_time = 0
        self.is_busy = False
        self.process_list = []
        self.ttardiness = 0.
        self.idx = 0
        self.start_working = self.env.event()
        self.wait = self.env.event()
        self.working_over = self.env.event()
        self.working_process = self.env.process(self.working())
        self.buffer_blank_process = self.env.process(self.buffer_blank())
        self.jobshop = None
        self.broken_signal = broken_signal
        self.dispatchingrules = dispatchingrules
        self.DRL = DRL
        self.is_borken=0

    def working(self, idx=0):
        while True:
            if self.broken_signal:
                broken_time = 400
                a = random.randint(1, 10)
                if a <= 1 :
                    count_curr=len(self.machine_buffer)
                    for i in range(0,count_curr):
                        cur=self.machine_buffer[0]
                        self.jobshop.job_list.appendleft(cur)
                        self.remove_job(cur)
                    self.is_borken=1
                    print(f"机床{self.machine_id}发生故障+{self.env.now}+故障时间{broken_time}")
                    yield self.env.timeout(broken_time)
                    self.is_borken=0
                    self.working_over.succeed(self.machine_id)
                    self.working_over = self.env.event()
                    continue
            yield self.start_working
            state = self.jobshop.getJobEnvState(self)
            action_idx = self.DRL.choose_action(state)
            self.DRL.actions_recorder[action_idx] += 1
            rules = self.dispatchingrules.rules[action_idx]
            current_job = rules(self.machine_buffer)
            time = current_job.get_job_process_time()
            time = time * self.process_factor
            start_time = self.env.now
            yield self.env.timeout(time)
            end_time = self.env.now
            self.append_process_list(
                (current_job.job_id, current_job.current_procedure_index + 1, start_time, end_time))
            current_job.next_procedure_index()
            self.remove_job(current_job)
            if current_job.current_procedure_index != -1:
                self.jobshop.add_job_shop(current_job)
            else:
                self.jobshop.add_end_job_shop(current_job)
            self.working_over.succeed(self.machine_id)
            self.working_over = self.env.event()
            self.jobshop.machine_idle()
            state_next = self.jobshop.getJobEnvState(self)
            reward_current = self.jobshop.get_total_time() / (self.jobshop.machine_num * self.env.now)
            reward = reward_current - self.DRL.reward_prev
            self.DRL.reward_prev = reward
            isDone = self.jobshop.check_is_done()
            self.DRL.add_reward(reward)
            self.DRL.remember(state, action_idx, reward, state_next, isDone)
            if self.DRL.step % 5 == 0:
                self.DRL.learn()
            self.DRL.step += 1

    def buffer_blank(self):
        while True:
            if not self.buffer_is_blank():
                self.start_working.succeed()
                self.start_working = self.env.event()
                yield self.working_over
            else:
                yield self.wait

    def trigger_wait(self):

        self.wait.succeed()
        self.wait = self.env.event()

    def put_job(self, job):

        if self.get_machine_buffer_rest_count() > 0:
            self.machine_buffer.append(job)
            self.add_machine_buffer_number()
            return True
        else:
            return False

    def remove_job(self, current_job):
        self.machine_buffer.remove(current_job)
        self.machine_buffer_count -= 1

    def append_process_list(self, tuple1):
        self.process_list.append(tuple1)

    def add_machine_buffer_number(self):
        self.machine_buffer_count += 1
        if self.machine_buffer_count > self.machine_buffer_number_init:
            raise Exception(str(self.machine_id) + "-机床的缓冲区长度大于" + self.machine_buffer_number_init)

    def get_machine_buffer_rest_count(self):
        if self.machine_buffer_count == len(self.machine_buffer):
            return self.machine_buffer_number_init - self.machine_buffer_count
        else:
            raise Exception("缓冲区的长度数目不匹配")

    def get_machine_buffer_count(self):
        return self.machine_buffer_count

    def calculate_machine_ttardiness(self):

        this_time = self.env.now
        sum = 0.
        for i, data in enumerate(self.process_list):

            if i == (len(self.process_list) - 1):
                sum += this_time - data[2] if data[2] < this_time <= data[3] else (data[3] - data[2])
            else:
                sum += (data[3] - data[2])

        ttardiness = sum / this_time if this_time != 0 else 0
        self.ttardiness = ttardiness

    def sum_time(self):
        sum = 0.
        for i in self.process_list:
            sum += (i[3] - i[2])
        return sum

    def buffer_is_blank(self):

        return len(self.machine_buffer) == 0

    def rest(self):
        self.machine_buffer_rest_count = self.machine_buffer_number_init
        self.machine_buffer = []
        self.current_processing_job = None
        self.process_factor = self.process_factor_init
        self.can_process_time = 0
        self.is_busy = False
        self.process_list = []
        self.ttardiness = 0.
