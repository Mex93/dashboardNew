from datetime import datetime
from datetime import timedelta

from scoreboard.enums import JOB_TYPE, JOB_STATUS, LINE_ID

from sql.enums import CONNECT_DB_TYPE, TIME_ZONES
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent
from sql.sql_data import PLAN_TABLE_FIELDS, SQL_TABLE_NAME, ASSEMBLED_TABLE_FIELDS
from log.Clog import Clog

from common import CCommon


class CScore:
    def __init__(self, time_zone: TIME_ZONES, line_id: LINE_ID):

        self.current_time_zone = time_zone
        self.current_line = line_id

        # Основное с вывода табло

        # слева табло
        self.total_day_plan = 0  # Дневной план
        self.total_day_plan_speed = 0  # Расчётная скорость телеков в час
        # относительно дневного плана (Меняыется только со сменой плана)
        # справа табло
        self.assembled_device = 0  # Собранных на текущий момент
        self.assembled_device_speed = 0  # Скорость в час относительно собранных по факту

        # футер
        self.assembled_speed_for_last_five_mins = 0  # Собрано за последние 5 минут
        self.assembled_speed_for_last_one_hour = 0  # Собрано за последний час
        self.assembled_forecast_for_day = 0  # Прогноз за день

        self.current_job_time = JOB_TYPE.NONE  # Тип рабочего времени - день и ночь
        self.current_job_status = JOB_STATUS.NONE  # Статус работы - закончена, идёт, перерыв итд

    def reload_data(self):
        pass

    def load_data(self):
        pass

    def __get_12hours_data(self, job_time: JOB_TYPE):

        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:

            global_sql = CSqlAgent(self.current_time_zone)
            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД(CScore): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")
                if result:

                    cdate = datetime.now()
                    #
                    day = cdate.day
                    month = cdate.month
                    year = cdate.year

                    time_line_start = str()
                    time_zone_str = CCommon.get_time_zone_str_from_country_time_zone(self.current_time_zone)

                    if job_time == JOB_TYPE.DAY:
                        time_line_start = (
                            f"{year}-{month}-{day} 08:00:00.0+"
                            f"{time_zone_str}")

                    elif job_time == JOB_TYPE.NIGHT:  # Ночь
                        time_line_start = (
                            f"{year}-{month}-{day} 20:00:00.0+"
                            f"{time_zone_str}")

                    query_string = (f"SELECT COUNT(DISTINCT {ASSEMBLED_TABLE_FIELDS.fd_tv_sn}) as tv_all_count "
                                    f"FROM {SQL_TABLE_NAME.assembled_tv} "
                                    f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                    f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' LIMIT 3000")

                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    devices_count = result[0].get("tv_all_count", None)
                    if devices_count is not None:

                        self.assembled_device = devices_count
                        print(devices_count)
                        Clog.lprint(f"CScore -> get_12hours_data ->  Данные получены!")
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
                Clog.lprint(f"Отключение от БД(CScore): CONNECT_DB_TYPE.LOCAL [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()

    def get_one_hours_data(self, job_time: JOB_TYPE):
        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:

            global_sql = CSqlAgent(self.current_time_zone)
            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД(CScore): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")
                if result:

                    cdate = datetime.now()

                    mins = cdate.minute
                    hours = cdate.hour
                    seconds = cdate.second
                    #
                    day = cdate.day
                    month = cdate.month
                    year = cdate.year

                    time_line_start = str()
                    time_zone_str = CCommon.get_time_zone_str_from_country_time_zone(self.current_time_zone)


                    start_date = cdate.strptime(f"{year}/{month}/{day} {hours}/{mins}/{seconds}", "%Y/%m/%d %H/%M/%S")
                    start_ex_date = start_date - timedelta(
                        seconds=60 * 60)
                    mins_correct_start = start_ex_date.minute
                    hours_correct_start = start_ex_date.hour
                    seconds_correct_start = start_ex_date.second
                    day_correct_start = start_ex_date.day
                    mon_correct_start = start_ex_date.month


                    if job_time == JOB_TYPE.DAY:
                        time_line_start = (
                            f"{year}-{mon_correct_start}-{day_correct_start} {hours_correct_start}:{mins_correct_start}:{seconds_correct_start}.0+"
                            f"{time_zone_str}")

                    elif job_time == JOB_TYPE.NIGHT:  # Ночь
                        time_line_start = (
                            f"{year}-{mon_correct_start}-{day_correct_start} {hours_correct_start}:{mins_correct_start}:{seconds_correct_start}.0+"
                            f"{time_zone_str}")

                    query_string = (f"SELECT COUNT(DISTINCT {ASSEMBLED_TABLE_FIELDS.fd_tv_sn}) as tv_lh_count "
                                    f"FROM {SQL_TABLE_NAME.assembled_tv} "
                                    f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                    f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' LIMIT 300")

                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    devices_count = result[0].get("tv_lh_count", None)
                    if devices_count is not None:
                        self.assembled_device = devices_count
                        print(devices_count)
                        Clog.lprint(f"CScore -> get_12hours_data ->  Данные получены!")
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
                Clog.lprint(f"Отключение от БД(CScore): CONNECT_DB_TYPE.LOCAL [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()

    def clear_data(self):
        pass

#
# unit = CScore(TIME_ZONES.RUSSIA, LINE_ID.LINE_VRN_TRI)
# unit.get_12hours_data(JOB_TYPE.NIGHT)
