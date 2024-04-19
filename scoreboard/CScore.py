from datetime import timedelta

from scoreboard.enums import JOB_TYPE, JOB_STATUS, LINE_ID, BREAK_TYPE, DATA_SCORE_TYPE

from sql.enums import CONNECT_DB_TYPE, TIME_ZONES
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent
from sql.sql_data import SQL_TABLE_NAME, ASSEMBLED_TABLE_FIELDS
from log.Clog import Clog
from scoreboard.CData import CData

from scoreboard.common import CCommon


class CScore:
    def __init__(self, time_zone: TIME_ZONES, line_id: LINE_ID):

        self.current_time_zone = time_zone
        self.current_line = line_id
        self.__is_result_stored = False
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

        self.current_job_status = JOB_STATUS.NONE  # Тип смены закончена перерыв итд
        self.current_job_time = JOB_TYPE.NONE  # Тип рабочего времени - день и ночь

        # ticks

        self.count_tv_on_5min_css = ""  # Скорость за 5 минут

        self.average_fact_on_hour_css = ""  # css средней скорости

        self.count_tv_average_ph_for_plan_css = ""  # css выборки за час

        self.count_tv_forecast_on_day_css = ""  # Прогноз за день

    def __get_12hours_data(self, cdata_unit: CData):

        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:

            global_sql = CSqlAgent(self.current_time_zone)
            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(
                    f"Подключение к БД(CScore -> get_12hours_data): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")
                if result:
                    time_zone_str = CCommon.get_time_zone_str_from_country_time_zone(self.current_time_zone)
                    cdate = CCommon.get_current_time(self.current_time_zone)
                    #
                    day = cdate.day
                    month = cdate.month
                    year = cdate.year

                    time_line_start = str()

                    job_time = cdata_unit.get_job_time_type()

                    if job_time == JOB_TYPE.DAY:
                        time_line_start = (
                            f"{year}-{month}-{day} {cdata_unit.start_job_day}:00.0+"
                            f"{time_zone_str}")

                    elif job_time == JOB_TYPE.NIGHT:  # Ночь
                        time_line_start = (
                            f"{year}-{month}-{day} {cdata_unit.start_job_night}:00.0+"
                            f"{time_zone_str}")

                    if self.current_line != LINE_ID.LINE_KZ_ONE:
                        query_string = (f"SELECT COUNT(DISTINCT {ASSEMBLED_TABLE_FIELDS.fd_tv_sn}) as tv_all_count "
                                        f"FROM {SQL_TABLE_NAME.assembled_tv} "
                                        f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                        f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' "
                                        f"LIMIT 3000")
                    else:
                        query_string = (f"SELECT COUNT(DISTINCT check_report.assy_id) AS tv_all_count "
                                        "FROM check_report "
                                        "JOIN check_description ON check_report.check_id = check_description.check_id "
                                        "WHERE check_report.check_param_0 = 'PASS' AND "
                                        "check_description.check_name = 'Completness check' AND "
                                        f"check_report.check_timestamp >= '{time_line_start}' AND "
                                        f"check_report.station_id = "
                                        f"(SELECT station_id FROM stations WHERE station_line = 5 LIMIT 1) "
                                        f"LIMIT 3000")

                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (
                        ), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(query_string)
                    devices_count = result[0].get("tv_all_count", None)
                    if devices_count is not None:
                        self.assembled_device = devices_count
                        Clog.lprint(f"CScore -> get_12hours_data ->  Данные получены!")
                        return True

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [get_12hours_data][{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [get_12hours_data][{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [get_12hours_data][{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [get_12hours_data][{err}]")

            finally:
                Clog.lprint(f"Отключение от БД(CScore -> get_12hours_data): CONNECT_DB_TYPE.LOCAL [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()
        return False

    def get_hours_score(self, score_type: DATA_SCORE_TYPE, break_params: list, cdata_unit: CData):
        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:

            global_sql = CSqlAgent(self.current_time_zone)
            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(
                    f"Подключение к БД(CScore -> get_hours_score): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")
                if result:
                    time_zone_str = CCommon.get_time_zone_str_from_country_time_zone(self.current_time_zone)
                    cdate = CCommon.get_current_time(self.current_time_zone)

                    seconds = cdate.second
                    hours = cdate.hour
                    mins = cdate.minute
                    #
                    day = cdate.day
                    month = cdate.month
                    year = cdate.year

                    delay_last_time = 0
                    if isinstance(break_params, list):
                        if break_params[0] != BREAK_TYPE.NONE:
                            delay_last_time = break_params[1]
                    # job_time = cdata_unit.get_job_time_type()

                    start_date = cdate.strptime(
                        f"{year}/{month}/{day} {hours}:{mins}/{seconds}",
                        "%Y/%m/%d %H:%M/%S")
                    # print("тут9шки", start_date)

                    start_ex_date = int()
                    if score_type == DATA_SCORE_TYPE.ONE_HOUR_DATA:
                        start_ex_date = start_date - timedelta(seconds=(60 * 60) + delay_last_time)
                    elif score_type == DATA_SCORE_TYPE.FIVE_MINS_DATA:
                        start_ex_date = start_date - timedelta(seconds=(60 * 5) + delay_last_time)

                    # print("тутушки  ", start_ex_date, "erdgdgyvwigw", delay_last_time)

                    # if self.current_line != LINE_ID.LINE_KZ_ONE:
                    #     start_ex_date = start_ex_date + timedelta(hours=3)
                    # else:
                    #     start_ex_date = start_ex_date + timedelta(hours=5)

                    mins_correct_start = start_ex_date.minute
                    hours_correct_start = start_ex_date.hour
                    seconds_correct_start = start_ex_date.second
                    day_correct_start = start_ex_date.day
                    mon_correct_start = start_ex_date.month

                    time_line_start = (
                        f"{year}-{mon_correct_start}-{day_correct_start} {hours_correct_start}:"
                        f"{mins_correct_start}:{seconds_correct_start}.0+"
                        f"{time_zone_str}")

                    # print(f"{hours_correct_start}:{mins_correct_start}")

                    if self.current_line != LINE_ID.LINE_KZ_ONE:

                        query_string = (f"SELECT COUNT(DISTINCT {ASSEMBLED_TABLE_FIELDS.fd_tv_sn}) as tv_count "
                                        f"FROM {SQL_TABLE_NAME.assembled_tv} "
                                        f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                        f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' LIMIT 300")
                        #print(query_string)
                    else:
                        query_string = (f"SELECT COUNT(DISTINCT check_report.assy_id) AS tv_count "
                                        "FROM check_report "
                                        "JOIN check_description ON check_report.check_id = check_description.check_id "
                                        "WHERE check_report.check_param_0 = 'PASS' AND "
                                        "check_description.check_name = 'Completness check' AND "
                                        f"check_report.check_timestamp >= '{time_line_start}' AND "
                                        f"check_report.station_id = "
                                        f"(SELECT station_id FROM stations WHERE station_line = 5 LIMIT 1) "
                                        f"LIMIT 300")


                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    devices_count = result[0].get("tv_count", None)
                    if devices_count is not None:

                        if score_type == DATA_SCORE_TYPE.ONE_HOUR_DATA:
                            self.assembled_speed_for_last_one_hour = devices_count
                            # print(query_string)
                        elif score_type == DATA_SCORE_TYPE.FIVE_MINS_DATA:
                            self.assembled_speed_for_last_five_mins = devices_count
                        Clog.lprint(f"CScore -> get_one_hours_data ->  Данные получены!")
                        return True

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [get_hours_score][{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [get_hours_score][{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [get_hours_score][{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [get_hours_score][{err}]")

            finally:
                Clog.lprint(f"Отключение от БД(CScore -> get_hours_score): CONNECT_DB_TYPE.LOCAL [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()
        return False

    def get_end_job_score(self, cdata_unit: CData):
        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:
            global_sql = CSqlAgent(self.current_time_zone)

            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(
                    f"Подключение к БД(CScore -> get_end_job_score): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")
                if result:

                    time_zone_str = CCommon.get_time_zone_str_from_country_time_zone(self.current_time_zone)
                    cdate = CCommon.get_current_time(self.current_time_zone)
                    #
                    day = cdate.day
                    month = cdate.month
                    year = cdate.year

                    mins = cdate.minute
                    hours = cdate.hour

                    mins_correct = mins
                    hours_correct = hours

                    day_correct = day
                    month_correct = month
                    year_correct = year

                    job_time = cdata_unit.get_job_time_type()

                    start_date = None
                    if job_time == JOB_TYPE.DAY:

                        start_date = cdate.strptime(f"{year}/{month}/{day} {cdata_unit.start_job_day}:00",
                                                    "%Y/%m/%d %H:%M:%S")

                    elif job_time == JOB_TYPE.NIGHT:

                        start_date = cdate.strptime(f"{year}/{month}/{day} {cdata_unit.start_job_night}:00",
                                                    "%Y/%m/%d %H:%M:%S")
                    if start_date is not None:
                        if ((job_time == JOB_TYPE.DAY and not CCommon.is_current_day_time(self.current_time_zone)) or
                                (job_time == JOB_TYPE.NIGHT and CCommon.is_current_day_time(self.current_time_zone))):

                            start_date = start_date - timedelta(days=1)
                            mins_correct = start_date.minute
                            hours_correct = start_date.hour
                            # seconds_correct = start_date.second
                            day_correct = start_date.day
                            month_correct = start_date.month
                            year_correct = start_date.year

                    time_line_start = (
                        f"{year_correct}-{month_correct}-{day_correct} {hours_correct}:{mins_correct}:00+"
                        f"{time_zone_str}")

                    sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
                    # Получим количество телеков всего по факту за смену по интервалу от начала смены до конца

                    if self.current_line != LINE_ID.LINE_KZ_ONE:

                        query_string = (f"SELECT COUNT(*) as tv_all_count FROM {SQL_TABLE_NAME.assembled_tv} "
                                        f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                                        f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' LIMIT 3000")
                    else:
                        query_string = (f"SELECT COUNT(DISTINCT check_report.assy_id) AS tv_all_count "
                                        "FROM check_report "
                                        "JOIN check_description ON check_report.check_id = check_description.check_id "
                                        "WHERE check_report.check_param_0 = 'PASS' AND "
                                        "check_description.check_name = 'Completness check' AND "
                                        f"check_report.check_timestamp >= '{time_line_start}' AND "
                                        f"check_report.station_id = "
                                        f"(SELECT station_id FROM stations WHERE station_line = 5 LIMIT 1) "
                                        f"LIMIT 3000")

                    result = global_sql.sql_query_and_get_result(

                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False
                    # print(result)

                    devices_count = result[0].get("tv_all_count", None)
                    if devices_count is not None:
                        self.assembled_device = devices_count

                        Clog.lprint(f"CScore -> get_one_hours_data ->  Данные получены!")
                        return True

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [get_end_job_score] [{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [get_end_job_score] [{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [get_end_job_score] [{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [get_end_job_score] [{err}]")

            finally:
                Clog.lprint(f"Отключение от БД(CScore -> get_end_job_score): CONNECT_DB_TYPE.LOCAL [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()
        return False

    def load_data(self):
        if self.current_job_time != JOB_TYPE.NONE:
            Clog.lprint(f"Ошибка! Тип смены[День, ночь] не выбран!")
            return

        # cdata
        data_unit = CData(self.current_time_zone, self.current_line)
        data_unit.get_data_for_line(self.current_time_zone)

        current_job_time = data_unit.get_job_time_type()
        self.current_job_time = current_job_time

        break_list = data_unit.get_current_break_time(current_job_time)

        # code

        self.total_day_plan = data_unit.get_day_total_plane()  # Дневной план

        self.get_hours_score(DATA_SCORE_TYPE.ONE_HOUR_DATA, break_list, data_unit)

        # расчёт типа смены[день ночь] и статуса[перерыв, работа итд]
        if current_job_time == JOB_TYPE.DAY:
            #  Может как то лучше сделать тут расчёт >?
            if not CCommon.is_current_day_time(self.current_time_zone):
                if self.assembled_speed_for_last_one_hour == 0:
                    self.current_job_status = JOB_STATUS.JOB_END
                else:
                    self.current_job_status = JOB_STATUS.JOB_IN_PROCESS
            else:
                self.current_job_status = JOB_STATUS.JOB_IN_PROCESS

        elif current_job_time == JOB_TYPE.NIGHT:
            self.current_job_status = JOB_STATUS.JOB_IN_PROCESS

            if CCommon.is_current_day_time(self.current_time_zone):
                if self.assembled_speed_for_last_one_hour == 0:
                    self.current_job_status = JOB_STATUS.JOB_END
                else:
                    self.current_job_status = JOB_STATUS.JOB_IN_PROCESS
            else:
                self.current_job_status = JOB_STATUS.JOB_IN_PROCESS

        if self.current_job_status == JOB_STATUS.JOB_IN_PROCESS or self.current_job_status == JOB_STATUS.JOB_BREAK:

            self.__get_12hours_data(data_unit)
            self.get_hours_score(DATA_SCORE_TYPE.ONE_HOUR_DATA, break_list, data_unit)
            self.get_hours_score(DATA_SCORE_TYPE.FIVE_MINS_DATA, break_list, data_unit)

            is_break = False

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
            compensace_list = data_unit.get_compensace_start_to_now_time(current_job_time)
            start_to_now_compensace = compensace_list[0]
            # время от старта смены и до текущего момента с компенсацией перерыва
            now_to_end_compensace = compensace_list[1]  # время от конца смены до текущего момента

            self.total_day_plan_speed = data_unit.get_day_plane_total_speed_for_hour(
                current_job_time, data_unit.job_day_delay)  # Расчётная скорость телеков в час

            # Компенсация времени перерыва если он начат

            compensace_sec_current_break = 0
            if is_break is True:
                compensace_sec_current_break = data_unit.get_break_last_time(self.job_break_type, current_job_time)
            else:
                compensace_sec_current_break = 0

            # Скорость дневного плана в час

            if self.assembled_device == 0:
                self.assembled_device_speed = 0
            else:
                # print(start_to_now_compensace, compensace_sec_current_break)
                self.assembled_device_speed = int(
                    self.assembled_device / ((start_to_now_compensace + compensace_sec_current_break) / 3600))

            # Прогноз за день
            hour_nte = now_to_end_compensace / 3600  # Количетво часов из оставшегося времени до конца смены
            forecast_day_for_day_nte = int(self.assembled_device_speed * hour_nte)
            self.assembled_forecast_for_day = self.assembled_device + forecast_day_for_day_nte

        elif self.current_job_status == JOB_STATUS.JOB_END:
            # TODO Блок показа общего плана за смену

            self.get_end_job_score(data_unit)

        # расчёт цветов для фронтенда
        self.get_speed_ticks(data_unit)

        # print("Перерыв " + str(break_list))
        # print("Тип смены " + str(self.current_job_status))
        #
        # # слева
        # print("Дневной план " + str(self.total_day_plan))
        # print("Скорость дневного плана в час " + str(self.total_day_plan_speed))
        #
        # # справа
        # print("Собрали по факту " + str(self.assembled_device))
        # print("Скорость сборки за час от факта " + str(self.assembled_device_speed))
        #
        # # Снизу
        # print("За последние пять минут " + str(self.assembled_speed_for_last_five_mins))
        # print("За последний час " + str(self.assembled_speed_for_last_one_hour))
        # print("Прогноз за день " + str(self.assembled_forecast_for_day))

        self.__is_result_stored = True

    def get_result_status(self):
        return self.__is_result_stored

    def get_speed_ticks(self, cdata_unit):
        """
        Вычисление тиков для вычислений цветов ксс
        :return:
        """

        # ---------------------------- Высчитываем такты
        """ 
        h1_tact: Оптимальный такст для выпуска тв за час
        opt_tact:  Оптимальный такст количество секунд затраченное на 1 телек
        opt_speed:  Оптимальная скорость для всей смены
        """
        current_job_time = cdata_unit.get_job_time_type()
        all_job_time_sec = cdata_unit.get_all_job_time(current_job_time, cdata_unit.job_day_delay)

        if self.current_job_status == JOB_STATUS.JOB_IN_PROCESS or self.current_job_status == JOB_STATUS.JOB_BREAK:

            # TODO Работа в процессе

            # opt_time_for_hour = int((self.total_day_plan / all_job_time_sec) * 5 * 60)
            # # int(count_all_plan / (all_job_time_hours * 3600) * 3600)
            # self.opt_time_for_hour = opt_time_for_hour

            # buff = 1 if self.assembled_speed_for_last_one_hour == 0 else self.assembled_speed_for_last_one_hour
            # # Деление на ноль исключаем
            # h1_tact = int(3600 / buff)

            # buff = 1 if self.total_day_plan == 0 else self.total_day_plan
            # # Деление на ноль исключаем
            # opt_tact = int(all_job_time_sec / buff)

            # Оптимальная скорость для всей смены за час
            opt_speed = int(self.total_day_plan / all_job_time_sec * 3600)

            opt_time_for_fivem = int(self.total_day_plan / all_job_time_sec * 5 * 60)

            # ------------------ Получение css относительно количества

            self.count_tv_on_5min_css = CCommon.estimate(self.assembled_speed_for_last_five_mins, opt_time_for_fivem)
            # Скорость за 5 минут

            self.average_fact_on_hour_css = CCommon.estimate(self.assembled_device_speed,
                                                             opt_speed)  # css средней скорости

            self.count_tv_average_ph_for_plan_css = CCommon.estimate(self.assembled_speed_for_last_one_hour, opt_speed)
            # css выборки за час

            self.count_tv_forecast_on_day_css = CCommon.estimate(self.assembled_forecast_for_day, self.total_day_plan)
            # Прогноз за день

        elif self.current_job_status == JOB_STATUS.JOB_END:

            count_tv_average_ph_for_plan = int(
                self.assembled_device / (
                        all_job_time_sec / 3600))  # int(count_tv_forecast_on_day / (all_job_time_mins / 60))

            self.total_day_plan_speed = count_tv_average_ph_for_plan

            # ------------------ Получение css относительно количества
            self.count_tv_on_5min_css = "-"  # Скорость за 5 минут

            opt_speed = int(self.total_day_plan / all_job_time_sec * 3600)

            self.average_fact_on_hour_css = CCommon.estimate(count_tv_average_ph_for_plan, opt_speed)
            # class_func.estimate(int((1 / h1_tact) * 10000), int((1 / opt_tact) * 10000))  # css средней скорости

            self.count_tv_average_ph_for_plan_css = "-"
            # css выборки за час

            self.assembled_speed_for_last_five_mins = 0
            self.assembled_forecast_for_day = 0
            self.assembled_speed_for_last_one_hour = 0

            self.count_tv_forecast_on_day_css = "-"

    def get_ceh_name(self):
        if self.current_line == LINE_ID.LINE_KZ_ONE:
            return f"Цех №: Казахстан"
        else:
            sql_line_id = CCommon.get_line_id_for_sql(self.current_line)

            return f"Цех №: {sql_line_id}"

    def get_title_name(self):

        return f"Статистика {self.get_ceh_name()}"

    def get_job_status_string(self) -> str:
        """
        Возврат названия статуса смены
        :param brake_type:
        :return:
        """
        if self.current_job_status == JOB_STATUS.JOB_IN_PROCESS:
            if self.current_job_time == JOB_TYPE.NIGHT:
                return "Ночная смена"
            else:
                return "Текущая смена"
        elif self.current_job_status == JOB_STATUS.JOB_BREAK:
            return CCommon.get_breaks_name(self.job_break_type)
        elif self.current_job_status in (JOB_STATUS.JOB_END, JOB_STATUS.NONE):
            return "Смена окончена"

        return "Неизвестно"

    def get_tv_current_count_for_day_plan(self):
        return self.total_day_plan

    def get_tv_current_count_for_day_fact(self):  # По факту всего собрано          (3)
        return self.assembled_device

    def get_tv_current_count_for_hour_plan(self):  # (2)
        return self.total_day_plan_speed

    def get_tv_current_count_average_speed_for_hour(self):  # (4)
        return self.assembled_device_speed

    def get_current_speed_for_last_hour(self):  # (5)
        return self.assembled_speed_for_last_one_hour

    def get_tv_speed_for_five_mins(self):  # (6)
        return self.assembled_speed_for_last_five_mins

    def get_tv_count_day_forecast(self):  # (7)
        return self.assembled_forecast_for_day

    def get_current_css_styles(self):
        res = {
            'count_tv_on_5min_css': self.count_tv_on_5min_css,
            'count_tv_average_ph_for_plan_css': self.count_tv_average_ph_for_plan_css,
            'average_fact_on_hour_css': self.average_fact_on_hour_css,
            'count_tv_forecast_on_day_css': self.count_tv_forecast_on_day_css,
        }
        return res
