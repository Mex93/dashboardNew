from flask import Flask, render_template, request, url_for, json
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = True
debug = False

lines_config = list()


@app.route('/logo.ico')
def favicon():
    return url_for('static', filename='/static/img/logo.ico')


@app.route('/ps')
def getsize():
    return render_template('psize.html')


@app.route('/scoreboard/<int:gmt_time>/<int:changed_line_id>')
@app.route('/sb/<int:gmt_time>/<int:changed_line_id>')
def scoreboard(gmt_time, changed_line_id):
    return render_template('scoreboard.html', time_gmt=gmt_time, line_id=changed_line_id)


@app.route('/engine_scripts/py/launch_scripts/scoreboard_get_stats.py', methods=['GET', 'POST'])
def scorebar():
    # надо как то запретить переход по прямой ссылке к файлу

    time_gmt = request.args['ctime_gmt']

    clineid = request.args['cline_id']

    result = get_result_scoreboard_json(clineid, time_gmt)
    return result


from scoreboard.CScore import CScore
from scoreboard.common import CCommon
from sql.enums import TIME_ZONES


def get_result_scoreboard_json(line_id: str, ctime_gmt: str) -> str:
    global debug
    if debug:
        input_line_id = 1
        time_zone = TIME_ZONES.RUSSIA
        input_time_gmt = 1
    else:
        input_line_id = int(line_id)
        input_time_gmt = int(ctime_gmt)

        if input_time_gmt == 1:
            time_zone = TIME_ZONES.RUSSIA
        else:
            time_zone = TIME_ZONES.KZ

    # Приём json запроса

    # -----------------VARS

    # Корректировка
    line_id = CCommon.get_line_id_type_from_line_id(input_line_id)
    if line_id is False:
        line_id = 1

    score_unit = CScore(time_zone, line_id)
    score_unit.load_data()

    ceh_name = score_unit.get_ceh_name()
    job_status_str = score_unit.get_job_status_string()  # Статус работы линии
    title_name = score_unit.get_title_name()

    if score_unit.get_result_status():  # 0 errors

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

        count_all_plan = score_unit.get_tv_current_count_for_day_plan()  # По факту всего собрано          (1)
        count_all_fact = score_unit.get_tv_current_count_for_day_fact()  # По факту всего собрано          (3)
        count_plan_on_hour = score_unit.get_tv_current_count_for_hour_plan()  # (2)
        average_fact_on_hour = score_unit.get_tv_current_count_average_speed_for_hour()  # (4)

        count_tv_average_ph_for_plan = score_unit.get_current_speed_for_last_hour()  # (5)
        count_tv_on_5min = score_unit.get_tv_speed_for_five_mins()  # (6)
        count_tv_forecast_on_day = score_unit.get_tv_count_day_forecast()  # (7)

        css = score_unit.get_current_css_styles()
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
            'checked_data': CCommon.get_random(100),
            'time_gmt': input_time_gmt,

            'error': f"All Data Stored(No Errors)"
        })
    else:  # Ошибка
        completedjson = json.dumps({
            'name': ceh_name,
            'status_txt': job_status_str,
            'title': title_name,
            'checked_data': -1,
            'time_gmt': input_time_gmt,
            'error': f"Error Load Data(Error name do Not detect)",
        })

    return completedjson


@app.route('/engine_scripts/py/launch_scripts/dashboard_get_stats.py', methods=['GET', 'POST'])
def dashboard_py():
    # надо как то запретить переход по прямой ссылке к файлу

    # time_gmt = request.args['ctime_gmt']
    # html_type = request.args['chtml_type']
    #
    # from engine_scripts.py.launch_scripts.dashboard_get_stats import get_result_json
    #
    # result = get_result_json(html_type, time_gmt)
    # return result
    return


@app.route('/dashboard_vrn/<int:gmt_time>')
@app.route('/db_vrn/<int:gmt_time>')
def dashboard_vrn(gmt_time):
    return render_template('dashboard_vrn.html', time_gmt=gmt_time)


@app.route('/dashboard_kz/<int:gmt_time>')
@app.route('/db_kz/<int:gmt_time>')
def dashboard_kz(gmt_time):
    return render_template('dashboard_kz.html', time_gmt=gmt_time)


@app.route('/dashboard_all/<int:gmt_time>')
@app.route('/db_all/<int:gmt_time>')
def dashboard_all(gmt_time):
    return render_template('dashboard_all.html', time_gmt=gmt_time)


@app.errorhandler(404)
def page_not_found(error_str):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
