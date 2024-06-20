import sys
# 调度规则类
class DispatchingRules:

    def __init__(self):
        self.rules = [self.SPT, self.LPT, self.FIFO, self.LIFO, self.SRPT, self.LRPT, self.LRM, self.SRM, self.LSO,
                      self.SSO, self.SPTdividedbyTWK, self.LPTdividedbyTWK, self.SPTdividedbyTWKR,
                      self.LPTdividedbyTWKR, self.LPTandLSO, self.SPTandSSO,  self.SPTmultiplyTWK,
                      self.SPRmultiplyTWKR, self.LPTmultiplyTWKR]

    def SPT(self, buffer):
        target = None
        target_time = sys.maxsize
        for job in buffer:
            if job.get_job_process_time() < target_time and job.is_lock is False:
                target = job
                target_time = job.get_job_process_time()
        return target

    def LPT(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            if job.get_job_process_time() > target_time and job.is_lock is False:
                target = job
                target_time = job.get_job_process_time()
        return target

    def FIFO(self, buffer):

        target = None
        if len(buffer) != 0:
            for i, job in enumerate(buffer):
                if job.is_lock is False:
                    target = buffer[i]
                    break
        return target

    def LIFO(self, buffer):

        target = None
        if len(buffer) != 0:
            for i in range(len(buffer) - 1, -1, -1):
                if buffer[i].is_lock is False:
                    target = buffer[i]
                    break
        return target

    def SRPT(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            if job.get_Remaining_Processing_Time() < target_time and job.is_lock is False:
                target = job
                target_time = job.get_Remaining_Processing_Time()
        return target

    def LRPT(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            if job.get_Remaining_Processing_Time() > target_time and job.is_lock is False:
                target = job
                target_time = job.get_Remaining_Processing_Time()
        return target

    def LRM(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_Remaining_Processing_Time() - job.get_job_process_time()
            if time > target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SRM(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:

            time = job.get_Remaining_Processing_Time() - job.get_job_process_time()
            if time < target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LSO(self, buffer):

        target = None
        target_time = -1
        for job in buffer:

            time = job.get_job_next_process_time()
            if time > target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SSO(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:

            time = job.get_job_next_process_time()
            if time < target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SPTdividedbyTWK(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            time = job.get_job_process_time() / job.get_total_Processing_Time()
            if time < target_time * 1.0 and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LPTdividedbyTWK(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_job_process_time() / job.get_total_Processing_Time()
            if time > target_time * 1.0 and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SPTdividedbyTWKR(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            time = job.get_job_process_time() / job.get_Remaining_Processing_Time()
            if time < target_time * 1.0 and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LPTdividedbyTWKR(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_job_process_time() / job.get_Remaining_Processing_Time()
            if time > target_time * 1.0 and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LPTandLSO(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_job_process_time() + job.get_job_next_process_time()
            if time > target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SPTandSSO(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            time = job.get_job_process_time() + job.get_job_next_process_time()
            if time < target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LPTmultiplyTWK(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_job_process_time() + job.get_total_Processing_Time()
            if time > target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SPTmultiplyTWK(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            time = job.get_job_process_time() + job.get_total_Processing_Time()
            if time < target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def LPTmultiplyTWKR(self, buffer):

        target = None
        target_time = -1
        for job in buffer:
            time = job.get_job_process_time() + job.get_Remaining_Processing_Time()
            if time > target_time and job.is_lock is False:
                target = job
                target_time = time
        return target

    def SPRmultiplyTWKR(self, buffer):

        target = None
        target_time = sys.maxsize
        for job in buffer:
            time = job.get_job_process_time() + job.get_Remaining_Processing_Time()
            if time < target_time and job.is_lock is False:
                target = job
                target_time = time
        return target
