from scoreboard.enums import BREAK_TYPE, JOB_TYPE


class CBreakTimes:
    # В секундах
    # ночь
    break_time_night = (
        (BREAK_TYPE.FIRST, 600),
        (BREAK_TYPE.EAT, 2400),
        (BREAK_TYPE.DOUBLE, 600),
        (BREAK_TYPE.LAST, 1200)
    )
    # день
    break_time_day = (
        (BREAK_TYPE.FIRST, 600),
        (BREAK_TYPE.EAT, 2400),
        (BREAK_TYPE.DOUBLE, 600),
        (BREAK_TYPE.LAST, 1200)
    )

    def __init__(self):
        pass

    @classmethod
    def get_break_time(cls, br_type: BREAK_TYPE, job_time: JOB_TYPE):
        """
        Returnet time in sec
        :param br_type:
        :param job_time:
        :return:
        """
        if job_time == JOB_TYPE.DAY:
            for break_time in cls.break_time_day:
                if break_time[0] == br_type:
                    return break_time[1]
        elif job_time == JOB_TYPE.NIGHT:
            for break_time in cls.break_time_night:
                if break_time[0] == br_type:
                    return break_time[1]
        return 0

    @classmethod
    def get_all_breaks_time(cls, job_time: JOB_TYPE):
        """
        Returnet time in sec
        :param br_type:
        :param job_time:
        :return:
        """
        count = 0
        if job_time == JOB_TYPE.DAY:
            for break_time in cls.break_time_day:
                count += break_time[1]
        elif job_time == JOB_TYPE.NIGHT:
            for break_time in cls.break_time_night:
                count += break_time[1]
        return count
