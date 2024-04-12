from datetime import datetime
from datetime import timedelta

from scoreboard.enums import LINE_ID
from common import CCommon
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

        # список с перерывами
        self.break_time_night = tuple()
        # день
        self.break_time_day = tuple()

    def get_data_for_line(self):

        sql_line_id = CCommon.get_line_id_for_sql(self.current_line_id)
        if sql_line_id:

            local_sql = CSqlAgent(self.current_time_zone)
            try:
                result = local_sql.connect_to_db(CONNECT_DB_TYPE.LOCAL)
                sql_handle = local_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД(CData): CONNECT_DB_TYPE.LOCAL [sql_handle: {sql_handle}]")
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

                    check_list = (
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

                    Clog.lprint(f"CData -> get_data_for_line ->  Данные получены! ({check_list})")
                    return True

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [{err}]")

            finally:
                Clog.lprint(
                    f"Отключение от БД(CData): CONNECT_DB_TYPE.LOCAL [sql_handle: {local_sql.get_sql_handle()}]")
                local_sql.disconnect_from_db()

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

    def get_break_start_time(self, br_type: BREAK_TYPE, job_time: JOB_TYPE):
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

    def get_current_break_time(self, job_time: JOB_TYPE):

        cdate = datetime.now()

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

        current_unix_time = CCommon.get_current_unix_time(cdate)
        for break_arr in buffer_list:
            start_time = break_arr[BREAK_ARRAY_DATA.START_TIME]

            start_date = cdate.strptime(f"{year}/{month}/{day} {start_time}/{seconds}", "%Y/%m/%d %H:%M/%S")
            # print(start_date)
            if start_date:
                break_start_time_unix_time = int(start_date.timestamp())
                if break_start_time_unix_time > 0:
                    end_time = int(break_start_time_unix_time + break_arr[BREAK_ARRAY_DATA.DELAY_SEC])

                    # print(break_start_time_unix_time, current_unix_time, end_time)
                    if break_start_time_unix_time <= current_unix_time <= end_time:
                        return break_arr[BREAK_ARRAY_DATA.BREAK_TYPE]

        return BREAK_TYPE.NONE



unit = CData(TIME_ZONES.RUSSIA, LINE_ID.LINE_VRN_ONE)
unit.get_data_for_line()
# print(unit.get_current_break_time(JOB_TYPE.DAY))

