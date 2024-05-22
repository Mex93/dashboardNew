

from scoreboard.enums import LINE_ID, JOB_TIME, JOB_BREAK_ARRAY_DATA
from scoreboard.common import CCommon
from sql.enums import CONNECT_DB_TYPE, TIME_ZONES
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent
from sql.sql_data import PLAN_TABLE_FIELDS, SQL_TABLE_NAME
from scoreboard.enums import BREAK_TYPE, JOB_TYPE, BREAK_ARRAY_DATA

from log.Clog import Clog


class CData:
    def __init__(self, time_zone: TIME_ZONES, line_id: LINE_ID):

        self.current_time_zone = time_zone  # Название страны
        self.last_change_data = None  # Дата обновления последняя
        self.total_day_plane = 0  # Дневной план
        self.current_line_id = line_id  # Текущая линия
        self.total_smena_delay = 0  # Дневная смена в часах

        self.current_job_time_type = JOB_TYPE.NONE  # Тип смены день ночь
        self.job_day_delay = 0  # Продолжительность рабочей смены в часах 8-12
        # список с перерывами
        self.break_time_night = tuple()
        # день
        self.break_time_day = tuple()
        # Время старта смены в строке
        self.start_job_day = "08:00"
        self.end_job_day = "20:00"

        self.start_job_night = "20:00"
        self.end_job_night = "08:00"

    def get_data_for_line(self):

        sql_line_id = CCommon.get_line_id_for_sql(self.current_line_id)
        if sql_line_id:

            local_sql = CSqlAgent(self.current_time_zone)
            try:
                result = local_sql.connect_to_db(CONNECT_DB_TYPE.LOCAL, self.current_time_zone)
                sql_handle = local_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД(CData -> get_data_for_line): CONNECT_DB_TYPE.LOCAL [sql_handle: {sql_handle}]")
                if result:
                    query_string = (f"SELECT * "
                                    f"FROM {SQL_TABLE_NAME.local_db_plan_table} "
                                    f"WHERE {PLAN_TABLE_FIELDS.fd_line_id} = %s "
                                    f"LIMIT 1")

                    result = local_sql.sql_query_and_get_result(
                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    sql_line_check = result[0].get(PLAN_TABLE_FIELDS.fd_line_id, None)
                    if sql_line_check is None:
                        return False

                    self.last_change_data = result[0].get(PLAN_TABLE_FIELDS.fd_change_date, None)
                    self.total_day_plane = result[0].get(PLAN_TABLE_FIELDS.fd_plan_current, 1200)
                    self.total_smena_delay = result[0].get(PLAN_TABLE_FIELDS.fd_time_hours_on_smena, 0)

                    # Старт и конец смены
                    self.start_job_day = result[0].get(PLAN_TABLE_FIELDS.fd_time_day_job_start, None)
                    self.end_job_day = result[0].get(PLAN_TABLE_FIELDS.fd_time_day_job_end, None)

                    self.start_job_night = result[0].get(PLAN_TABLE_FIELDS.fd_time_night_job_start, None)
                    self.end_job_night = result[0].get(PLAN_TABLE_FIELDS.fd_time_night_job_end, None)

                    # Время начала строка
                    break_day_one_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_first_time_day_start, None)
                    break_day_eat_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_eat_time_day_start, None)
                    break_day_double_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_double_time_day_start, None)
                    break_day_third_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_third_time_day_start, None)

                    break_night_one_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_first_time_night_start, None)
                    break_night_eat_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_eat_time_night_start, None)
                    break_night_double_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_double_time_night_start, None)
                    break_night_third_start = result[0].get(PLAN_TABLE_FIELDS.fd_brake_third_time_night_start, None)

                    # Длительность в минутах
                    break_day_one_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_first_time_day_len, None)
                    break_day_eat_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_eat_time_day_len, None)
                    break_day_double_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_double_time_day_len, None)
                    break_day_third_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_third_time_day_len, None)

                    break_night_one_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_first_time_night_len, None)
                    break_night_eat_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_eat_time_night_len, None)
                    break_night_double_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_double_time_night_len, None)
                    break_night_third_len = result[0].get(PLAN_TABLE_FIELDS.fd_brake_third_time_night_len, None)

                    self.job_day_delay = result[0].get(PLAN_TABLE_FIELDS.fd_job_day_delay, None)
                    # Тип смены день ночь
                    # Меняется в бд для день или ночь
                    # Если выставлен день то ночных смен нет и наоборот
                    self.current_job_time_type = result[0].get(PLAN_TABLE_FIELDS.fd_smena_start_job_type, None)

                    check_list = (
                        # старт смены и конец - строка
                        self.job_day_delay,
                        self.start_job_day,
                        self.end_job_day,
                        self.start_job_night,
                        self.end_job_night,

                        # тип смены
                        self.current_job_time_type,

                        self.last_change_data,
                        self.total_day_plane,
                        self.total_smena_delay,
                        # Время начала
                        break_day_one_start,
                        break_day_eat_start,
                        break_day_double_start,
                        break_day_third_start,
                        break_night_one_start,
                        break_night_eat_start,
                        break_night_double_start,
                        break_night_third_start,
                        # Длительность
                        break_day_one_len,
                        break_day_eat_len,
                        break_day_double_len,
                        break_day_third_len,

                        break_night_one_len,
                        break_night_eat_len,
                        break_night_double_len,
                        break_night_third_len,
                    )
                    for var in check_list:
                        if var is None:
                            Clog.lprint(f"CData -> get_data_for_line ->  Данные Не получены! ({check_list})")
                            return False

                    # #  Конверт в utc
                    # try:
                    #     self.start_job_day = CCommon.time_to_utc(self.start_job_day)
                    #     self.end_job_day = CCommon.time_to_utc(self.end_job_day)
                    #     self.start_job_night = CCommon.time_to_utc(self.start_job_night)
                    #     self.end_job_night = CCommon.time_to_utc(self.end_job_night)
                    #     break_day_one_start = CCommon.time_to_utc(break_day_one_start)
                    #     break_day_eat_start = CCommon.time_to_utc(break_day_eat_start)
                    #     break_day_double_start = CCommon.time_to_utc(break_day_double_start)
                    #     break_day_third_start = CCommon.time_to_utc(break_day_third_start)
                    #
                    #     break_night_one_start = CCommon.time_to_utc(break_night_one_start)
                    #     break_night_eat_start = CCommon.time_to_utc(break_night_eat_start)
                    #     break_night_double_start = CCommon.time_to_utc(break_night_double_start)
                    #     break_night_third_start = CCommon.time_to_utc(break_night_third_start)

                    # except ValueError:
                    #     print("Ошибка в конверте дат!")
                    #     return
                    if self.job_day_delay == 12:
                        self.break_time_day = (
                            (BREAK_TYPE.FIRST, break_day_one_len * 60, break_day_one_start),
                            (BREAK_TYPE.EAT, break_day_eat_len * 60, break_day_eat_start),
                            (BREAK_TYPE.DOUBLE, break_day_double_len * 60, break_day_double_start),
                            (BREAK_TYPE.LAST, break_day_third_len * 60, break_day_third_start)
                        )

                        self.break_time_night = (
                            (BREAK_TYPE.FIRST, break_night_one_len * 60, break_night_one_start),
                            (BREAK_TYPE.EAT, break_night_eat_len * 60, break_night_eat_start),
                            (BREAK_TYPE.DOUBLE, break_night_double_len * 60, break_night_double_start),
                            (BREAK_TYPE.LAST, break_night_third_len * 60, break_night_third_start)
                        )
                    elif self.job_day_delay == 9:
                        self.break_time_day = (
                            (BREAK_TYPE.FIRST, break_day_one_len * 60, break_day_one_start),
                            (BREAK_TYPE.EAT, break_day_eat_len * 60, break_day_eat_start),
                            (BREAK_TYPE.DOUBLE, break_day_double_len * 60, break_day_double_start),
                        )

                        self.break_time_night = (
                            (BREAK_TYPE.FIRST, break_night_one_len * 60, break_night_one_start),
                            (BREAK_TYPE.EAT, break_night_eat_len * 60, break_night_eat_start),
                            (BREAK_TYPE.DOUBLE, break_night_double_len * 60, break_night_double_start),
                        )

                    Clog.lprint(f"CData -> get_data_for_line ->  Данные получены! ({check_list})")
                    return True

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [get_data_for_line] [{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [get_data_for_line] [{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [get_data_for_line] [{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [get_data_for_line] [{err}]")

            finally:
                Clog.lprint(
                    f"Отключение от БД(CData -> get_data_for_line): CONNECT_DB_TYPE.LOCAL [sql_handle: {local_sql.get_sql_handle()}]")
                local_sql.disconnect_from_db()

        return False

    def get_break_delay_time(self, br_type: BREAK_TYPE, job_time: JOB_TYPE):
        """
        Returnet time in sec
        :param br_type:
        :param job_time:
        :return:
        """
        buffer_list = None

        if job_time == JOB_TYPE.DAY:
            buffer_list = self.break_time_day
        elif job_time == JOB_TYPE.NIGHT:
            buffer_list = self.break_time_night

        for break_time in buffer_list:
            if break_time[BREAK_ARRAY_DATA.BREAK_TYPE] == br_type:
                return break_time[BREAK_ARRAY_DATA.DELAY_SEC]

        return 0

    def get_break_start_string_time(self, br_type: BREAK_TYPE, job_time: JOB_TYPE) -> int | str:
        """
        Returnet time in sec
        :param br_type:
        :param job_time:
        :return:
        """
        buffer_list = None

        if job_time == JOB_TYPE.DAY:
            buffer_list = self.break_time_day
        elif job_time == JOB_TYPE.NIGHT:
            buffer_list = self.break_time_night

        for break_time in buffer_list:
            if break_time[BREAK_ARRAY_DATA.BREAK_TYPE] == br_type:
                return break_time[BREAK_ARRAY_DATA.START_TIME]

        return 0

    def get_all_breaks_delay_time(self, job_time: JOB_TYPE):
        """
        Returnet time in sec
        :param job_time:
        :return:
        """
        count = 0

        buffer_list = None

        if job_time == JOB_TYPE.DAY:
            buffer_list = self.break_time_day
        elif job_time == JOB_TYPE.NIGHT:
            buffer_list = self.break_time_night

        for break_time in buffer_list:
            count += break_time[BREAK_ARRAY_DATA.DELAY_SEC]

        return count

    def get_current_break_time(self, job_time: JOB_TYPE) -> list[int | int] | BREAK_TYPE:

        cdate = CCommon.get_current_time(self.current_time_zone)

        mins = cdate.minute
        hours = cdate.hour
        seconds = cdate.second
        #
        day = cdate.day
        month = cdate.month
        year = cdate.year

        buffer_list = None

        if job_time == JOB_TYPE.DAY:
            buffer_list = self.break_time_day
        elif job_time == JOB_TYPE.NIGHT:
            buffer_list = self.break_time_night

        if buffer_list is None:
            return BREAK_TYPE.NONE

        current_unix_time = int(cdate.timestamp())

        for break_arr in buffer_list:
            start_time = break_arr[BREAK_ARRAY_DATA.START_TIME]

            # start_date = cdate.strptime(f"{year}/{month}/{day} {CCommon.utc_to_current_zone_time(start_time, "0300")}/{seconds}", "%Y/%m/%d %H:%M/%S")
            start_date = cdate.strptime(
                f"{year}/{month}/{day} {start_time}/{seconds}",
                "%Y/%m/%d %H:%M/%S")

            # print("BSBGSBSFBFSBB   ", start_date, current_unix_time, CCommon.timestamp_ex(int(start_date.timestamp())))
            # print(start_date)
            if start_date:
                break_start_time_unix_time = CCommon.timestamp_ex(int(start_date.timestamp()))

                if break_start_time_unix_time > 0:
                    end_time = int(break_start_time_unix_time + break_arr[BREAK_ARRAY_DATA.DELAY_SEC])

                    # print(break_start_time_unix_time, current_unix_time, end_time)
                    # print("BSBGSBSFBFSBB   ", cdate.timestamp(), break_start_time_unix_time, end_time)
                    if break_start_time_unix_time <= current_unix_time <= end_time:

                        last_time = current_unix_time - break_start_time_unix_time
                        if last_time < 0:
                            last_time = 0

                        return [break_arr[BREAK_ARRAY_DATA.BREAK_TYPE], last_time]

        return BREAK_TYPE.NONE

    def get_day_total_plane(self):
        return int(self.total_day_plane)

    def get_day_plane_total_speed_for_hour(self, job_time: JOB_TYPE, job_day_delay: int):
        plane = self.total_day_plane

        all_job_time = self.get_all_job_time(job_time, job_day_delay)
        speed = 0

        if all_job_time > 0:
            speed = plane / (all_job_time / 3600)

        return int(speed)

    def get_all_job_time(self, job_time: JOB_TYPE, job_day_delay: int):
        buff = job_day_delay * 3600
        all_delays = self.get_all_breaks_delay_time(job_time)
        buff -= all_delays
        if buff < 0:
            buff = 0

        return buff  # результат в секундах

    def get_job_time_type(self):
        return self.current_job_time_type

    def get_job_time_unix_time(self, job_type: JOB_TIME, job_time: JOB_TYPE):

        cdate = CCommon.get_current_time(self.current_time_zone)

        mins = cdate.minute
        hours = cdate.hour
        seconds = cdate.second
        #
        day = cdate.day
        month = cdate.month
        year = cdate.year

        start_date = None
        if job_type == JOB_TIME.START:
            if job_time == JOB_TYPE.NIGHT:
                start_date = cdate.strptime(f"{year}/{month}/{day} "
                                            f"{self.start_job_night}/00", "%Y/%m/%d %H:%M/%S")

                # start_date = cdate.strptime(f"{year}/{month}/{day} "
                #                             f"{CCommon.utc_to_current_zone_time(self.start_job_night, "0300")}/00",
                #                             "%Y/%m/%d %H:%M/%S")

            elif job_time == JOB_TYPE.DAY:
                # start_date = cdate.strptime(f"{year}/{month}/{day} "
                #                             f"{CCommon.utc_to_current_zone_time(self.start_job_day, "0300")}/00", "%Y/%m/%d %H:%M/%S")

                start_date = cdate.strptime(f"{year}/{month}/{day} "
                                            f"{self.start_job_day}/00",
                                            "%Y/%m/%d %H:%M/%S")

        elif job_type == JOB_TIME.END:

            time_str = None
            if self.job_day_delay == 9:
                if job_time == JOB_TYPE.NIGHT:
                    time_str = "05:00"
                elif job_time == JOB_TYPE.DAY:
                    time_str = "17:00"
            elif self.job_day_delay == 12:
                if job_time == JOB_TYPE.NIGHT:
                    time_str = "08:00"
                elif job_time == JOB_TYPE.DAY:
                    time_str = "20:00"

            if job_time == JOB_TYPE.NIGHT:
                # start_date = cdate.strptime(f"{year}/{month}/{day} "
                #                             f"{CCommon.utc_to_current_zone_time(time_str, "0300")}/00", "%Y/%m/%d %H:%M/%S")
                start_date = cdate.strptime(f"{year}/{month}/{day} "
                                             f"{time_str}/00", "%Y/%m/%d %H:%M/%S")

            elif job_time == JOB_TYPE.DAY:
                # start_date = cdate.strptime(f"{year}/{month}/{day} "
                #                             f"{CCommon.utc_to_current_zone_time(time_str, "0300")}/00", "%Y/%m/%d %H:%M/%S")

                start_date = cdate.strptime(f"{year}/{month}/{day} "
                                            f"{time_str}/00",
                                            "%Y/%m/%d %H:%M/%S")
        if start_date is None:
            Clog.lprint(
                f"Ошибка!!! get_job_time_unix_time -> start_date -> None")
            return
        start_job_time = CCommon.timestamp_ex(int(start_date.timestamp()))
        if start_job_time < 0:
            start_job_time = 0

        return int(start_job_time)

    def get_break_unit_time(self, break_type: BREAK_TYPE, job_time: JOB_TYPE) -> bool | list:
        """Возврат времени unix time старта и конца перерыва"""
        string = self.get_break_start_string_time(break_type, job_time)
        if isinstance(string, str):

            cdate = CCommon.get_current_time(self.current_time_zone)

            mins = cdate.minute
            hours = cdate.hour
            seconds = cdate.second
            #
            day = cdate.day
            month = cdate.month
            year = cdate.year

            # start_date = int(cdate.strptime(f"{year}/{month}/{day} {CCommon.utc_to_current_zone_time(string, "0300")}/00", "%Y/%m/%d %H:%M/%S").timestamp())
            start_date = int(
                cdate.strptime(f"{year}/{month}/{day} {string}/00",
                               "%Y/%m/%d %H:%M/%S").timestamp())

            start_date = CCommon.timestamp_ex(start_date)

            # print("eqifuheqwuofgehewqg", CCommon.utc_to_current_zone_time(string, "0300"))
            if start_date < 0:
                start_date = 0

            delay = self.get_break_delay_time(break_type, job_time)
            start_date = [start_date, start_date + delay, delay]
            return start_date

        return False

    def get_compensace_start_to_now_time(self, job_time: JOB_TYPE) -> list[int]:
        """ Вычисляет компенсацию времени перерывов отнимая её от времени старта смены
        до текущей или от конца смены до текущей"""

        current_unix_time = CCommon.get_current_time(self.current_time_zone).timestamp()

        breaks = None
        if self.job_day_delay == 12:
            breaks = [
                BREAK_TYPE.FIRST,
                BREAK_TYPE.EAT,
                BREAK_TYPE.DOUBLE,
                BREAK_TYPE.LAST
                      ]
        elif self.job_day_delay == 9:
            breaks = [
                BREAK_TYPE.FIRST,
                BREAK_TYPE.EAT,
                BREAK_TYPE.DOUBLE
            ]

        time_job_start = self.get_job_time_unix_time(JOB_TIME.START, job_time)  # unix time

        start_to_now_sc = current_unix_time - time_job_start
        if start_to_now_sc < 0:
            start_to_now_sc = 0

        time_job_end = self.get_job_time_unix_time(JOB_TIME.END, job_time)  # unix time
        time_to_end_smena_sc = time_job_end - current_unix_time
        if time_to_end_smena_sc < 0:
            time_to_end_smena_sc = 0
        for br_type in breaks:
            br_params = self.get_break_unit_time(br_type, job_time)
            if isinstance(br_params, list):

                start = br_params[JOB_BREAK_ARRAY_DATA.START]
                end = br_params[JOB_BREAK_ARRAY_DATA.END]
                delay = br_params[JOB_BREAK_ARRAY_DATA.DELAY]

                # start to now
                if start < current_unix_time < end:
                    start_to_now_sc -= current_unix_time - start  # отнимаем сколько прошло
                    if start_to_now_sc < 0:
                        start_to_now_sc = 0
                elif current_unix_time > end:
                    start_to_now_sc -= delay
                # now to end

                if current_unix_time < start:
                    time_to_end_smena_sc -= delay
        # print(start_to_now_sc, time_to_end_smena_sc)
        return [start_to_now_sc, time_to_end_smena_sc]

    def get_break_last_time(self, break_type: BREAK_TYPE, job_time: JOB_TYPE) -> bool | int:
        """ Отсчёт времени перерыва = сколько осталось секунд """
        if break_type is not BREAK_TYPE.NONE:
            br_params = self.get_break_unit_time(break_type, job_time)
            if isinstance(br_params, list):

                current_unix_time = CCommon.get_current_time(self.current_time_zone).timestamp()

                start = br_params[JOB_BREAK_ARRAY_DATA.START]
                end = br_params[JOB_BREAK_ARRAY_DATA.END]
                # delay = br_params[JOB_BREAK_ARRAY_DATA.DELAY]

                if start <= current_unix_time <= end:
                    last = end - current_unix_time
                    if last < 0:
                        last = 0
                    return last
        return False

# unit = CData(TIME_ZONES.RUSSIA, LINE_ID.LINE_VRN_ONE)
# unit.get_data_for_line()
# # print(unit.get_current_break_time(JOB_TYPE.DAY))
