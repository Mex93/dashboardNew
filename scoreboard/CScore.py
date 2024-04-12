from datetime import datetime
from datetime import timedelta

from scoreboard.enums import JOB_TYPE, JOB_STATUS, LINE_ID, BREAK_TYPE, DATA_SCORE_TYPE, JOB_TIME, JOB_BREAK_ARRAY_DATA

from sql.enums import CONNECT_DB_TYPE, TIME_ZONES
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent
from sql.sql_data import PLAN_TABLE_FIELDS, SQL_TABLE_NAME, ASSEMBLED_TABLE_FIELDS
from log.Clog import Clog
from scoreboard.CData import CData

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

        # Данные смены
        self.job_break_type = BREAK_TYPE.NONE

        cdate = datetime.now()
        #
        day = cdate.day
        month = cdate.month
        year = cdate.year

        mins = cdate.minute
        hours = cdate.hour
        seconds = cdate.second

        c_job_time = JOB_TYPE.NONE
        if 8 <= hours <= 20:
            c_job_time = JOB_TYPE.DAY
        elif 21 <= hours <= 8:
            c_job_time = JOB_TYPE.NIGHT
        else:  # На всякий )))
            c_job_time = JOB_TYPE.NONE

        self.current_job_status = JOB_STATUS.NONE  # Тип смены закончена перерыв итд
        self.current_job_time = c_job_time  # Тип рабочего времени - день и ночь

    def reload_data(self):
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
        return False

    def get_hours_score(self, score_type: DATA_SCORE_TYPE, job_time: JOB_TYPE, break_params: list):
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

                    delay_for_break = 0
                    if isinstance(break_params, list):
                        if break_params[0] != BREAK_TYPE.NONE:
                            delay_for_break = break_params[1]

                    start_date = cdate.strptime(f"{year}/{month}/{day} {hours}/{mins}/{seconds}", "%Y/%m/%d %H/%M/%S")
                    start_ex_date = int()
                    if score_type == DATA_SCORE_TYPE.ONE_HOUR_DATA:
                        start_ex_date = start_date - timedelta(
                            seconds=(60 * 60) + delay_for_break)
                    elif score_type == DATA_SCORE_TYPE.FIVE_MINS_DATA:
                        start_ex_date = start_date - timedelta(
                            seconds=(60 * 5) + delay_for_break)

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

                    query_string = (f"SELECT COUNT(DISTINCT {ASSEMBLED_TABLE_FIELDS.fd_tv_sn}) as tv_count "
                                    f"FROM {SQL_TABLE_NAME.assembled_tv} "
                                    f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                    f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' LIMIT 300")

                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    devices_count = result[0].get("tv_count", None)
                    if devices_count is not None:

                        if score_type == DATA_SCORE_TYPE.ONE_HOUR_DATA:
                            self.assembled_speed_for_last_one_hour = devices_count
                        elif score_type == DATA_SCORE_TYPE.FIVE_MINS_DATA:
                            self.assembled_speed_for_last_five_mins = devices_count
                        Clog.lprint(f"CScore -> get_one_hours_data ->  Данные получены!")
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
        return False

    def clear_data(self):
        pass

    def load_data(self):
        if self.current_job_time == JOB_TYPE.NONE:
            Clog.lprint(f"Ошибка! Тип смены[День, ночь] не выбран!")
            return

        self.current_job_status = JOB_STATUS.JOB_IN_PROCESS  # Статус работы - закончена, идёт, перерыв итд

        data_unit = CData(self.current_time_zone, self.current_line)
        data_unit.get_data_for_line()
        break_list = data_unit.get_current_break_time(self.current_job_time)

        self.total_day_plan = data_unit.get_day_total_plane()  # Дневной план
        self.total_day_plan_speed = data_unit.get_day_plane_total_speed_for_hour(
            self.current_job_time)  # Расчётная скорость телеков в час

        self.__get_12hours_data(self.current_job_time)
        self.get_hours_score(DATA_SCORE_TYPE.ONE_HOUR_DATA, self.current_job_time, break_list)
        self.get_hours_score(DATA_SCORE_TYPE.FIVE_MINS_DATA, self.current_job_time, break_list)

        # расчёт типа смены[день ночь] и статуса[перерыв, работа итд]
        if self.current_job_time == JOB_TYPE.NIGHT:
            if self.assembled_speed_for_last_one_hour == 0:
                self.current_job_status = JOB_STATUS.JOB_END
            else:
                self.current_job_status = JOB_STATUS.JOB_IN_PROCESS

        elif self.current_job_time == JOB_TYPE.DAY:
            self.current_job_status = JOB_STATUS.JOB_IN_PROCESS

        is_break = False
        if self.current_job_status == JOB_STATUS.JOB_IN_PROCESS:

            if isinstance(break_list, list):
                ctype = break_list[0]
                if ctype != JOB_STATUS.NONE:
                    self.current_job_status = JOB_STATUS.JOB_BREAK
                    self.job_break_type = ctype
                    is_break = True

            if is_break is False:
                self.current_job_status = JOB_STATUS.JOB_IN_PROCESS
                self.job_break_type = BREAK_TYPE.NONE

        # время от старта смены и до текущего момента с компенсацией перерыва
        compensace_list = data_unit.get_compensace_start_to_now_time(self.current_job_time)
        start_to_now_compensace = compensace_list[
            0]  # время от старта смены и до текущего момента с компенсацией перерыва
        now_to_end_compensace = compensace_list[1]  # время от конца смены до текущего момента

        # Компенсация времени перерыва если он начат

        compensace_sec_current_break = 0
        if is_break is True:
            compensace_sec_current_break = data_unit.get_break_last_time(self.job_break_type, self.current_job_time)

        # Скорость дневного плана в час
        self.assembled_device_speed = int(
            self.assembled_device / ((start_to_now_compensace - compensace_sec_current_break) / 3600))

        # Прогноз за день
        hour_nte = now_to_end_compensace / 3600  # Количетво часов из оставшегося времени до конца смены
        forecast_day_for_day_nte = int(self.assembled_device_speed * hour_nte)
        self.assembled_forecast_for_day = self.assembled_device + forecast_day_for_day_nte

        # расчёт цветов для фронтенда

        print("Перерыв " + str(break_list))
        # слева
        print("Дневной план " + str(self.total_day_plan))
        print("Скорость дневного плана в час " + str(self.total_day_plan_speed))

        # справа
        print("Собрали по факту " + str(self.assembled_device))
        print("Скорость сборки за час от факта " + str(self.assembled_device_speed))

        # Снизу
        print("За последние пять минут " + str(self.assembled_speed_for_last_five_mins))
        print("За последний час " + str(self.assembled_speed_for_last_one_hour))
        print("Прогноз за день " + str(self.assembled_forecast_for_day))


#
unit = CScore(TIME_ZONES.RUSSIA, LINE_ID.LINE_VRN_ONE)
unit.load_data()
