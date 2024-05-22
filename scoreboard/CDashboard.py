
from datetime import timedelta
# Приём json запроса

from sql.CSQLAgent import CSqlAgent
from sql.enums import TIME_ZONES, CONNECT_DB_TYPE

from sql.sql_data import SQL_TABLE_NAME
from sql.sql_data import ASSEMBLED_TABLE_FIELDS
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData
from scoreboard.enums import JOB_TYPE, LINE_ID
from scoreboard.common import CCommon
from scoreboard.CData import CData

from log.Clog import Clog


# Подключение к бд со статой линии (настройки лежат в движке модуля бд)
# Подключение к бд

class CDashboard:
    def __init__(self, time_zone: TIME_ZONES, line_id: LINE_ID):
        self.current_time_zone = time_zone
        self.current_line = line_id

    def load_plan_settings(self) -> tuple | bool:

        plan_unit = CData(self.current_time_zone, self.current_line)

        result = plan_unit.get_data_for_line()
        if result is False:
            return False

        result_arr = self.get_points(plan_unit)
        if result_arr is False:
            return False

        # TODO логика работы:
        # 1 Получаем результат из бд
        # 2 Формируем шаблон времени для чисел результат
        # 3 Перезаписываем совпадающие значения в словаре шаблона из словаря результата
        # 4 Профит - отправляем словари часы минуты
        # print(result_arr)
        arr_size = result_arr.__len__()
        db_results_dict = dict()
        for i in range(arr_size):
            # Parsing даты
            string = str(result_arr[i]["ts_date_interval"])
            buff = string.split(" ")
            buff = str(buff[1]).split(":")
            buff = f"{int(buff[0]) + 0:02}" + ":" + buff[1]
            # -------------
            count = result_arr[i]["tv_count_on_5min"]  # 310 не поддерживает прямо в f строке
            # print(buff, count)
            db_results_dict.update({f"{buff}": f"{count}"})

        # Достанем данные из необработанного 8 часа, так как он не обрабатывается ниже в коде Лены и 8 час пустой
        # Просто производительность добавим за текущий момент в 5 минутах
        # Вытаскиваем данные из основного словаря за первый час
        first_hour_date_dict = dict()
        first_hour_date_main_list = list()

        for i in range(12):
            buff = f"08:{+ i * 5:02}"
            count = db_results_dict.get(buff, 0)
            first_hour_date_main_list.append(count)
        size = first_hour_date_main_list.__len__()
        # Вычисляем скорость каждой пятиминутки первого часа
        # Умножим количество на 12 (количество пятиминуток в часе)

        for index_main in range(size):
            buff = int(first_hour_date_main_list[index_main])
            if buff > 0:
                buff = buff * 12
                first_hour_date_main_list[index_main] = buff

        if len(first_hour_date_main_list) > 0:
            # Обновим значения в словаре выдранного часа из списка

            for i in range(size):
                buff = f"08:{+ i * 5:02}"
                first_hour_date_dict.update({buff: first_hour_date_main_list[i]})
            # Костыль для 9 00, получим из основного словаря ->
            # сложим с 8:55 -> if 0 then count(9:00) + lcount 8:55
            last_count = first_hour_date_main_list[-1]
            count = db_results_dict.get("09:00", 0)
            first_hour_date_dict.update({"09:00": int(count) + last_count})

        ###
        # print(first_hour_date_dict)

        # print(arr_size)
        # print(db_results_dict)
        # Общий шаблон для графика на 12 часов * 12 раз по 5 минут в часу (формирование)

        # Формирование шаблона времени
        # Забиваем список для дня
        list_hour_day = list()

        for count_hour in range(12):  # 12 hours
            list_hour_day.append(f"{8 + count_hour:02}")
        #
        # Список для ночи
        list_hour_night = ["20", "21", "22", "23", "00", "01", "02", "03", "04", "05", "06", "07"]
        # костыль, ну а чё !?? 0_0

        # Mins in hours
        list_mins = list()
        for count_mins in range(12):
            list_mins.append(f"{5 * count_mins:02}")

        # Соединяем в едино
        job_time = plan_unit.get_job_time_type()

        if job_time == JOB_TYPE.DAY:
            result_hour_list = list_hour_day.copy()
        else:
            result_hour_list = list_hour_night.copy()

        # Формируем полный список за смену с нулями
        result_time_dict_5mins = dict()
        for chour in range(12):
            for cmins in range(12):
                buff_dict = {f'{result_hour_list[chour]}:{list_mins[cmins]}': 0}
                result_time_dict_5mins.update(buff_dict)

        fivemins_max_empty_arr = result_time_dict_5mins.copy()

        count_in_hour = dict()
        # Получим за час и найдём скорость просто прибавляя количество за каждые 5 минут
        # независимый цикл для подсчёта именно часов
        buff_main_dict = dict()
        hours_max_empty_arr = dict()
        for hour in result_hour_list:
            buff_count = 0
            for mins_count in range(12):  # count mins in hour
                str_key = f"{hour}:{list_mins[mins_count]}"
                buff_count += int(db_results_dict.get(f"{str_key}", 0))
            count_in_hour.update({f"{hour}": buff_count})
            hours_max_empty_arr.update({f"{hour}": 0})

        last_data = ""
        # Расчёт основания для часов
        for hours in count_in_hour:
            value = count_in_hour.get(f"{hours}", 0)
            if value == 0:
                continue
            buff_main_dict.update({f"{hours}": value})
            last_data = f"{hours}"

        count_in_hour = buff_main_dict.copy()
        del buff_main_dict

        # TODO делаем основание с нулями с самого начала и добавляем новые значения
        buff_main_dict = dict()
        for key in hours_max_empty_arr:
            buff_main_dict.update({key: count_in_hour.get(key, 0)})
            if last_data == key:
                break

        count_in_hour = buff_main_dict.copy()
        del buff_main_dict
        # Результат из бд (Код Лены + мой )
        try:
            i = 12
            while i < arr_size:
                h = 0
                j = i - 12
                while j < i:
                    h += result_arr[j]["tv_count_on_5min"]
                    j += 1
                # parsing
                label_parced = str(result_arr[i]["ts_date_interval"]).split(" ")
                label_parced = label_parced[1].split(":")
                label_parced = f"{label_parced[0]}:{label_parced[1]}"
                #
                result_time_dict_5mins.update({f"{label_parced}": h})
                i += 1

            last_data = ""
            #  Получим последнюю дату минут если пустой массив result_time_dict_5mins
            #  Первый час - полтора массив пустой 8 -> ~ 9:30
            #  Нужно что бы шкалу лейбл правильную строить, а не за все 12 часов
            buff_main_dict = dict()

            if db_results_dict.__len__() > 0:
                last_data = list(db_results_dict)[-1]  # Найдём последний ключ

            # print(last_data)
            # Расчёт основания для минут

            for hours in result_time_dict_5mins:
                value = result_time_dict_5mins.get(f"{hours}", 0)

                if value == 0:
                    continue
                buff_main_dict.update({f"{hours}": value})

                last_data = f"{hours}"

            result_time_dict_5mins.clear()
            result_time_dict_5mins = buff_main_dict.copy()

            del buff_main_dict
            # print(last_data)

            # TODO делаем основание с нулями с самого начала и добавляем новые значения
            buff_main_dict = dict()

            for key in fivemins_max_empty_arr:
                buff_main_dict.update({key: result_time_dict_5mins.get(key, 0)})
                if last_data == key:
                    break

            result_time_dict_5mins.clear()
            result_time_dict_5mins = buff_main_dict.copy()

            del buff_main_dict
            if len(first_hour_date_dict) > 0:
                # Забуфим в общий словарь данные для первого часа
                for el in first_hour_date_dict:
                    result_time_dict_5mins.update({el: first_hour_date_dict.get(el, 0)})

        except IndexError as err:
            print(f"Внимание! Ошибка в CDashboard -> {err}")

            return False

        restup = (count_in_hour,
                  result_time_dict_5mins,
                  plan_unit.get_day_total_plane(),
                  plan_unit.get_day_plane_total_speed_for_hour(job_time, plan_unit.job_day_delay)
                  )

        return restup

    def get_points(self, cdata_unit: CData) -> list | bool:

        sql_line_id = CCommon.get_line_id_for_sql(self.current_line)
        if sql_line_id:
            global_sql = CSqlAgent(self.current_time_zone)
            try:
                result = global_sql.connect_to_db(CONNECT_DB_TYPE.LINE)
                sql_handle = global_sql.get_sql_handle()
                Clog.lprint(
                    f"Подключение к БД(CDashboard -> get_points): CONNECT_DB_TYPE.LINE [sql_handle: {sql_handle}]")

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

                        if job_time == JOB_TYPE.NIGHT:
                            if CCommon.is_night_job_hour(self.current_time_zone):
                                start_date = start_date - timedelta(days=1)
                                mins_correct = start_date.minute
                                hours_correct = start_date.hour
                                # seconds_correct = start_date.second
                                day_correct = start_date.day
                                month_correct = start_date.month
                                year_correct = start_date.year
                        else:
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

                        query_string = (
                            "SELECT "
                            f"date_bin('5 min',{ASSEMBLED_TABLE_FIELDS.fd_completed_date}, "
                            f"'2022-1-1') AS ts_date_interval, "
                            "COUNT(*) as tv_count_on_5min "
                            f"FROM {SQL_TABLE_NAME.assembled_tv} "
                            f"WHERE {ASSEMBLED_TABLE_FIELDS.fd_linefk} = {sql_line_id} "
                            f"AND {ASSEMBLED_TABLE_FIELDS.fd_completed_date} >= '{time_line_start}' "
                            "GROUP BY 1 "
                            "ORDER BY 1 "
                            "LIMIT 144")  # 12 * 12 сколько по 5 минут каждый час в часу

                    else:
                        query_string = (
                            f"SELECT "
                            f"date_bin('5 min', {ASSEMBLED_TABLE_FIELDS.fd_completed_date}, "
                            f"'2022-1-1') AS ts_date_interval, "
                            "COUNT(DISTINCT check_report.assy_id) as tv_count_on_5min"
                            "FROM check_report "
                            "JOIN check_description ON check_report.check_id = check_description.check_id "
                            "WHERE check_report.check_param_0 = 'PASS' AND "
                            "check_description.check_name = 'Completness check' AND "
                            f"check_report.check_timestamp >= '{time_line_start}' AND "
                            f"check_report.station_id = "
                            f"(SELECT station_id FROM stations WHERE station_line = 5 LIMIT 1) "
                            "GROUP BY 1 "
                            "ORDER BY 1 "
                            f"LIMIT 3000")

                    result = global_sql.sql_query_and_get_result(
                        sql_handle, query_string, (sql_line_id,), "_1", )  # Запрос типа аасоциативного массива
                    # print(result)
                    if result is False:  # Errorrrrrrrrrrrrr based data
                        return False

                    return result

            except NotConnectToDB as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NotConnectToDB [get_points] [{err}]")
            except ErrorSQLQuery as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLQuery [get_points] [{err}]")
            except ErrorSQLData as err:
                Clog.lprint(f"Внимание! Ошибка SQL: ErrorSQLData [get_points] [{err}]")
            except Exception as err:
                Clog.lprint(f"Внимание! Ошибка SQL: NonType [get_points] [{err}]")

            finally:
                Clog.lprint(f"Отключение от БД(CDashboard -> get_points): CONNECT_DB_TYPE.LINE [sql_handle: "
                            f"{global_sql.get_sql_handle()}]")
                global_sql.disconnect_from_db()
        return False
