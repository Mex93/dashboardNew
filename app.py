from flask import Flask, render_template, request, url_for, json
from datetime import datetime
import threading

from enums import LINE_DATA

app = Flask(__name__)

app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = True
debug = False

load_scoreboard = 0
load_dashboard = 0

@app.route('/logo.ico')
def favicon():
    return url_for('static', filename='/static/img/logo.ico')


@app.route('/ps')
def getsize():
    return render_template('psize.html')


@app.route('/kz')
def get_kz():
    return render_template('scoreboard.html', time_gmt="2", line_id="5")


@app.route('/get_score_line_<int:line_id>')
def get_line_scorebar(line_id):
    if 1 <= line_id <= 5:
        time_gmt = "1"
        if line_id == 5:
            time_gmt = "2"
        return render_template('scoreboard.html', time_gmt=time_gmt, line_id=str(line_id))

    return render_template('scoreboard.html', time_gmt="1", line_id="1")


@app.route('/engine_scripts/py/launch_scripts/scoreboard_get_stats.py', methods=['GET', 'POST'])
def scorebar():
    # надо как то запретить переход по прямой ссылке к файлу

    clineid = request.args['cline_id']

    lines_list_unit = LinesScoreboard.get_lines_list()

    for current_unit in lines_list_unit:
        if current_unit.get_line_id_str() == clineid:
            return current_unit.get_score_data()

    return json.dumps({
        'name': "Цех: -",
        'time_mins': "-",
        'time_hours': "-",
        'status_txt': "Error Check Data...",
        'title': "Цех: -",
        'checked_data': -1,
        'time_gmt': "0300",
        'error': f"Error Load Data(Error name do Not detect)",
    })


@app.route('/get_dashb_line_vrn')
@app.route('/gdb_vrn')
def dashboard_vrn():
    return render_template('dashboard_vrn.html')


@app.route('/get_dashb_line_kz')
@app.route('/gdb_kz')
def dashboard_kz():
    return render_template('dashboard_kz.html')


@app.route('/get_dashb_line_all')
@app.route('/gdb_all')
def dashboard_all():
    return render_template('dashboard_all.html')


@app.route('/engine_scripts/py/launch_scripts/dashboard_get_stats.py', methods=['GET', 'POST'])
def dashboard():
    # надо как то запретить переход по прямой ссылке к файлу

    chtml_type = request.args['chtml_type']

    html_type = int(chtml_type)
    if html_type == 1:
        html_type = "kz"
    elif html_type == 2:
        html_type = "vrn"
    else:
        html_type = "all"

    lines_list_unit = LinesDashboard.get_lines_list()

    if html_type == "kz":
        lines = ['5']
    elif html_type == "vrn":
        lines = ['1', '2', '3', '4']
    elif html_type == "all":
        lines = ['1', '2', '3', '4', '5']
    else:
        return False

    def get_find(lineslist: list, cur_lines: str) -> bool:
        for line in lineslist:
            if line == cur_lines:
                return True
        return False

    results_line = []
    for current_unit in lines_list_unit:
        cline_id = current_unit.get_line_id_str()
        if get_find(lines, cline_id):
            dbdata = current_unit.get_dashb_data()
            results_line.append([dbdata])

    return json.dumps(results_line)


from scoreboard.CScoreboard import CScore
from scoreboard.CDashboard import CDashboard
from scoreboard.common import CCommon
from sql.enums import TIME_ZONES


def get_result_dashboard_json(line_id: str, time_zone: TIME_ZONES) -> list:
    global debug

    if debug:
        input_line_id = 1
        time_zone = TIME_ZONES.RUSSIA
    else:
        input_line_id = int(line_id)

    # Приём json запроса

    # -----------------VARS

    # Корректировка
    line_id = CCommon.get_line_id_type_from_line_id(input_line_id)
    if line_id is False:
        line_id = 1

    score_unit = CDashboard(time_zone, line_id)
    dashb_data = score_unit.load_plan_settings()

    count_in_hour = {'08': 0}
    result_time_dict_5mins = {'08:00': 0}
    day_plane = 777
    sql_line_id = CCommon.get_line_id_for_sql(line_id)
    hour_plane = 122
    if dashb_data is False:
        print(f"Получение результата DASHB по умолчанию. Линия '{line_id}'")
    else:
        print(f"Получение результата DASHB. Линия '{line_id}'")
        count_in_hour, result_time_dict_5mins, day_plane, hour_plane = dashb_data
    return [count_in_hour, result_time_dict_5mins, day_plane, hour_plane, sql_line_id]


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

        completedjson = json.dumps({
            'name': ceh_name,
            'status_txt': job_status_str,
            'title': title_name,
            'time_mins': score_unit.get_mins(),
            'time_hours': score_unit.get_hours(),
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
            'time_mins': "-",
            'time_hours': "-",
            'status_txt': job_status_str,
            'title': title_name,
            'checked_data': -1,
            'time_gmt': input_time_gmt,
            'error': f"Error Load Data(Error name do Not detect)",
        })

    return completedjson


@app.errorhandler(404)
def page_not_found(error_str):
    # return render_template('404.html')
    return render_template('scoreboard.html', time_gmt="2", line_id="5")


class LinesScoreboard:
    active_lines = list()
    UPDATE_SECS = 10

    def __init__(self, line_id: int, line_enum: LINE_DATA, line_id_str: str, time_zone: TIME_ZONES):
        self.unix_last_update_time = 0
        self.time_zone = time_zone
        self.line_data_dict = json.dumps({
            'name': "Цех: -",
            'time_mins': "-",
            'time_hours': "-",
            'status_txt': "-",
            'title': "Цех: -",
            'checked_data': -1,
            'time_gmt': "0300",
            'error': f"Error Load Data(Error name do Not detect)",
        })
        self.line_id_str = line_id_str
        self.line_enum = line_enum
        self.line_id = line_id

        self.update_time()
        self.save_line(self)
        print(f"Линия создана scoreb. LINE_ID: {line_id}")

    #####################################################
    def get_line_id_str(self) -> str:
        return self.line_id_str

    def get_time_zone(self):
        return self.time_zone

    def get_line_id(self) -> int:
        return self.line_id

    @classmethod
    def save_line(cls, unitssss) -> None:
        cls.active_lines.append(unitssss)

    @classmethod
    def get_lines_list(cls):
        return cls.active_lines

    #####################################################
    def update_score_data(self, new_data: dict) -> None:
        self.line_data_dict = new_data
        print(f"Инфа Scoreb обновлена. LINE_ID: {self.get_line_id()}")

    def get_score_data(self):
        print(f"Старая инфа Scoreb предоставлена. LINE_ID: {self.get_line_id()}")
        return self.line_data_dict

    #####################################################
    def update_time(self) -> int:
        self.unix_last_update_time = get_current_unix_time() + self.UPDATE_SECS
        print(f"Unix Time Инфа обновлена scoreb. LINE_ID: {self.get_line_id()}")
        return self.get_time()

    def get_time(self) -> int:
        return self.unix_last_update_time

    #####################################################


class LinesDashboard:
    active_lines = list()
    UPDATE_SECS = 3

    def __init__(self, line_id: int, line_enum: LINE_DATA, line_id_str: str, time_zone: TIME_ZONES):
        self.unix_last_update_time = 0

        self.line_data_dict = json.dumps({
            'in_hour': {'08': 0},
            'in_five_mins': {'08:00': 0},
            'day_plane': 777,
            'line_id': 0
        })
        self.time_zone = time_zone
        self.line_id_str = line_id_str
        self.line_enum = line_enum
        self.line_id = line_id

        self.update_time()
        self.save_line(self)
        print(f"Линия создана dashb. LINE_ID: {line_id}")

    #####################################################
    def get_line_id_str(self) -> str:
        return self.line_id_str

    def get_time_zone(self):
        return self.time_zone

    def get_line_id(self) -> int:
        return self.line_id

    @classmethod
    def save_line(cls, unitssss) -> None:
        cls.active_lines.append(unitssss)

    @classmethod
    def get_lines_list(cls):
        return cls.active_lines

    #####################################################

    def update_dashb_data(self, new_data: dict) -> None:
        self.line_data_dict = new_data
        print(f"Инфа dashb обновлена. LINE_ID: {self.get_line_id()}")

    def get_dashb_data(self):
        print(f"Старая инфа dashb предоставлена. LINE_ID: {self.get_line_id()}")
        return self.line_data_dict

    #####################################################
    def update_time(self) -> int:
        self.unix_last_update_time = get_current_unix_time() + self.UPDATE_SECS
        print(f"Unix Time Инфа dashb обновлена. LINE_ID: {self.get_line_id()}")
        return self.get_time()

    def get_time(self) -> int:
        return self.unix_last_update_time

    #####################################################


def get_current_unix_time() -> int:
    unix_time = datetime.now()
    return int(unix_time.timestamp())


def start_timers(type_of_data: int):
    if type_of_data == 1 or type_of_data == 3:
        timer_id = threading.Timer(10, lambda: on_update_scorebar(),
                                   args=None, kwargs=None)
        timer_id.start()

    if type_of_data == 2 or type_of_data == 3:
        timer_id = threading.Timer(10, lambda: on_update_dashboard(),
                                   args=None, kwargs=None)
        timer_id.start()


def on_update_scorebar():
    # надо как то запретить переход по прямой ссылке к файлу

    global load_scoreboard
    if load_scoreboard == 0:
        LinesScoreboard(1, LINE_DATA.LINE_VRN_0, "1", TIME_ZONES.RUSSIA)
        LinesScoreboard(2, LINE_DATA.LINE_VRN_1, "2", TIME_ZONES.RUSSIA)
        LinesScoreboard(3, LINE_DATA.LINE_VRN_2, "3", TIME_ZONES.RUSSIA)
        LinesScoreboard(4, LINE_DATA.LINE_VRN_3, "4", TIME_ZONES.RUSSIA)

        LinesScoreboard(5, LINE_DATA.LINE_KZ_0, "5", TIME_ZONES.KZ)
        load_scoreboard = 1

    lines_list_unit = LinesScoreboard.get_lines_list()
    for current_unit in lines_list_unit:
        clineid = current_unit.get_line_id_str()
        time_zone = current_unit.get_time_zone()
        current_unit.update_time()
        result = get_result_scoreboard_json(clineid, time_zone)
        current_unit.update_score_data(result)
    start_timers(1)


def on_update_dashboard():

    global load_dashboard
    if load_dashboard == 0:
        LinesDashboard(1, LINE_DATA.LINE_VRN_0, "1", TIME_ZONES.RUSSIA)
        LinesDashboard(2, LINE_DATA.LINE_VRN_1, "2", TIME_ZONES.RUSSIA)
        LinesDashboard(3, LINE_DATA.LINE_VRN_2, "3", TIME_ZONES.RUSSIA)
        LinesDashboard(4, LINE_DATA.LINE_VRN_3, "4", TIME_ZONES.RUSSIA)

        LinesDashboard(5, LINE_DATA.LINE_KZ_0, "5", TIME_ZONES.KZ)
        load_dashboard = 1

    lines_list_unit = LinesDashboard.get_lines_list()

    results_line = []
    for current_unit in lines_list_unit:
        cline_id = current_unit.get_line_id_str()
        time_zone = current_unit.get_time_zone()
        result = get_result_dashboard_json(cline_id, time_zone)
        current_unit.update_dashb_data(result)
        results_line.append([result])

    start_timers(2)


if __name__ == "__main__":
    start_timers(3)
    app.run(debug=False)
