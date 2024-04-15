import json
from engine_scripts.py.core.functions_other import get_random, get_correct_line_id
from engine_scripts.py.core.linestats_engine import stats as cstats
from engine_scripts.py.core.enums import ERROR_TYPE
import sys
from datetime import datetime
debug = False


def get_result_json(line_id: str, ctime_gmt: str) -> str:
    global debug

    if debug:
        input_line_id = 1
        input_time_gmt = "0300"
    else:
        input_line_id = int(line_id)
        input_time_gmt = int(ctime_gmt)

        if input_time_gmt == 1:
            input_time_gmt = "0300"
        else:
            input_time_gmt = "0600"

    # Приём json запроса

    # -----------------VARS

    # Корректировка
    result = get_correct_line_id(input_line_id)
    if result is False:
        line_id = 1
    else:
        line_id = result

    cmain_stats = cstats(line_id, input_time_gmt)
    ceh_name = cmain_stats.get_ceh_name()
    job_status_str = cmain_stats.get_line_status_name()  # Статус работы линии
    title_name = cmain_stats.get_title_name()

    if cmain_stats.get_class_error_type() == ERROR_TYPE.RESULT_NONE:  # 0 errors

        # ceh_name: str = "-"
        # line_status: str = "-"
        # title_name: str = "-"
        # job_status_str: str = "-"  # Статус работы линии
        # current_line_status_id: int = 0
        # count_all_fact: int = 0  # По факту всего собрано
        # average_fact_on_hour: int = 0  # Всего тв по факту за час прямой выборкой из бд
        # count_tv_average_ph_for_plan: int = 0
        # # Собрано тв за последний час из расчёта фактическего объёма тв
        # # собранного за день и по времени
        #
        # count_tv_forecast_on_day: int = 0  # Прогноз всего тв за день на основании динамических данных факта
        # count_tv_on_5min: int = 0  # Скорость сборки за последние 5 минут прямая выборка с бд
        # average_fact_on_hour_css: str = "-"  # Стиль
        # count_tv_average_ph_for_plan_css: str = "-"  # Стиль
        # count_tv_on_5min_css: str = "-"  # Стиль
        # count_tv_forecast_on_day_css: str = "-"  # Стиль
        # count_all_plan: int = 0  # Всего TV за день по плану
        # count_plan_on_hour: int = 0  # Всего тв в час по плану

        """
        (1) 1200(план факт)                  (3) 40(собрали по факту)
        (2) 30(скорость за день за час)      (4) 20(скорость сборки в час)
        (5) 14(скорость за час выборка)      (6) 5(мин)       (7) 1100 (прогноз)
        """

        # job_status_str = f"{cmain_stats.get_line_status_name()} [{cmain_stats.break_time_stop_sec}]"

        count_all_plan = cmain_stats.get_tv_current_count_for_day_plan()  # По факту всего собрано          (1)
        count_all_fact = cmain_stats.get_tv_current_count_for_day_fact()  # По факту всего собрано          (3)
        count_plan_on_hour = cmain_stats.get_tv_current_count_for_hour_plan()  # (2)
        average_fact_on_hour = cmain_stats.get_tv_current_count_average_speed_for_hour()  # (4)

        count_tv_average_ph_for_plan = cmain_stats.get_current_speed_for_last_hour()  # (5)
        count_tv_on_5min = cmain_stats.get_tv_speed_for_five_mins()  # (6)
        count_tv_forecast_on_day = cmain_stats.get_tv_count_day_forecast()  # (7)

        css = cmain_stats.get_current_css_styles()
        average_fact_on_hour_css = css['average_fact_on_hour_css']
        count_tv_average_ph_for_plan_css = css['count_tv_average_ph_for_plan_css']
        count_tv_on_5min_css = css['count_tv_on_5min_css']
        count_tv_forecast_on_day_css = css['count_tv_forecast_on_day_css']

        cdate = datetime.now()

        mins = cdate.minute
        hours = cdate.hour

        completedjson = json.dumps({
            'name': ceh_name,
            'status_txt': job_status_str,
            'ctime': f"{hours}:{mins}",
            'title': title_name,
            'plan': count_all_plan,
            'TV': count_all_fact,
            'opt_speed': count_plan_on_hour,
            'av_speed': average_fact_on_hour,
            'av_speed_css': average_fact_on_hour_css,
            'h1_TV': count_tv_average_ph_for_plan,
            'h1_TV_css': count_tv_average_ph_for_plan_css,
            'm5_TV': count_tv_on_5min,
            'm5_TV_css': count_tv_on_5min_css,
            'forecast_TV': count_tv_forecast_on_day,
            'tv_forecast_total_css': count_tv_forecast_on_day_css,
            'tv_line_id': line_id,
            'checked_data': get_random(100),
            'time_gmt': input_time_gmt,

            'error': f"All Data Stored({cmain_stats.get_class_error_type()})"
        })
    else:  # Ошибка
        completedjson = json.dumps({
            'name': ceh_name,
            'status_txt': job_status_str,
            'title': title_name,
            'checked_data': -1,
            'time_gmt': input_time_gmt,
            'error': f"Error Load Data({cmain_stats.get_class_error_type()})"
        })

    return completedjson
