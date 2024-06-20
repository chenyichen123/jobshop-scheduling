class Job:
    def __init__(self,
                 job_id,
                 job_type,
                 job_process_plan,
                 job_process_time,
                 create_time
                 ):
        self.job_id = job_id
        self.job_type = job_type
        self.job_process_plan = job_process_plan
        self.job_process_time = job_process_time
        if len(self.job_process_time) != len(self.job_process_plan):
            raise Exception("工艺路线和工艺时间不匹配")
        self.is_lock = False
        self.current_procedure_index = 0
        self.current_procedure = self.job_process_plan[self.current_procedure_index]
        self.create_time = create_time
        self.start_time = 0
        self.over_time = -1
        self.machine = None
        self.start_end_time_list = []
        self.total_time = 0

    def rest(self, creat_time):
        self.is_lock = False
        self.current_procedure_index = 0
        self.current_procedure = self.job_process_plan[0]
        self.start_time = creat_time
        self.over_time = -1
        self.machine = None
        self.start_end_time_list = []

    def set_start_time(self, time):
        self.start_time = time

    def set_machine(self, machine):
        self.machine = machine
        self.over_time = machine.process_factor * self.job_process_time[self.current_procedure_index] + self.start_time

    def appendToList(self):
        self.start_end_time_list.append((self.start_time, self.over_time))

    def get_job_plan_count(self):
        return len(self.job_process_plan)

    def get_current_procedure(self):
        self.current_procedure = self.job_process_plan[
            self.current_procedure_index] if (len(self.job_process_plan) > self.current_procedure_index >= 0) else -1

        return self.current_procedure

    def next_procedure_index(self):
        self.current_procedure_index += 1
        if self.current_procedure_index > len(self.job_process_plan) - 1:
            self.current_procedure_index = -1

    def get_job_process_time(self):
        return self.job_process_time[self.current_procedure_index]

    def get_job_next_process_time(self):

        return self.job_process_time[self.current_procedure_index + 1] if self.current_procedure_index + 1 < len(
            self.job_process_time) else 0

    def get_Remaining_Processing_Time(self):

        sumTime = 0
        for i in range(self.current_procedure_index, len(self.job_process_plan)):
            sumTime += self.job_process_time[i]
        return sumTime

    def get_total_Processing_Time(self):

        if self.total_time == 0:
            for time in self.job_process_time:
                self.total_time += time

        return self.total_time

    def rest_operation_num(self):

        return len(self.job_process_plan) - self.current_procedure_index

    def get_operation_completion_rate(self):

        ratio = 0
        if self.current_procedure_index == -1:
            ratio = 1
        else:
            ratio = (self.current_procedure_index + 1) / len(self.job_process_plan)
        return ratio

    def __str__(self):
        return "[" + str(self.job_id) + " " + str(self.job_type) + " " + str(self.current_procedure_index + 1) + "]"
