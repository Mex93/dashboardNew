from flask import Flask, render_template, request, url_for

import config as conf

app = Flask(__name__)


app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{conf.db_standart_connect_params[conf.KEY_VALUE_NAME_USER]}:"
                                         f"{conf.db_standart_connect_params[conf.KEY_VALUE_NAME_PASS]}@"
                                         f"{conf.db_standart_connect_params[conf.KEY_VALUE_NAME_HOST]}:"
                                         f"{conf.db_standart_connect_params[conf.KEY_VALUE_NAME_PORT]}/"
                                         f"{conf.db_standart_connect_params[conf.KEY_VALUE_NAME_DATABASE]}")


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

    from engine_scripts.py.launch_scripts.scoreboard_get_stats import get_result_json

    result = get_result_json(clineid, time_gmt)
    return result


@app.route('/engine_scripts/py/launch_scripts/dashboard_get_stats.py', methods=['GET', 'POST'])
def dashboard_py():
    # надо как то запретить переход по прямой ссылке к файлу

    time_gmt = request.args['ctime_gmt']
    html_type = request.args['chtml_type']

    from engine_scripts.py.launch_scripts.dashboard_get_stats import get_result_json

    result = get_result_json(html_type, time_gmt)
    return result


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
    app.run(host='0.0.0.0', debug=True)
    # socketio.run(app, debug=True)  # Отключен из за вареника так как сыпал вареник на исполнение в
    # IDE а не веб сервере
