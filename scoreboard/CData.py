from scoreboard.enums import LINE_ID
from common import CCommon
from sql.enums import CONNECT_DB_TYPE
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent
from sql.sql_data import PLAN_TABLE_FIELDS, SQL_TABLE_NAME

from log.Clog import Clog


class CData:
    def __init__(self, country_name: str):

        self.country_name = country_name  # Название страны
        self.last_change_data = None  # Дата обновления последняя
        self.total_day_plane = 0  # Дневной план
        self.current_line_id = LINE_ID.LINE_NONE  # Текущая линия
        self.total_smena_delay = 0  # Дневная смена в часах

    def get_data_for_line(self, line_id: LINE_ID):

        sql_line_id = CCommon.get_line_id_for_sql(line_id)
        if sql_line_id:

            local_sql = CSqlAgent(self.country_name)
            try:
                result = local_sql.connect_to_db(CONNECT_DB_TYPE.LOCAL)
                sql_handle = local_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД: CONNECT_DB_TYPE.LOCAL [sql_handle: {sql_handle}]")
                if result:

                    query_string = (f"SELECT {PLAN_TABLE_FIELDS.fd_change_date}, "
                                    f"{PLAN_TABLE_FIELDS.fd_plan_current}, "
                                    f"{PLAN_TABLE_FIELDS.fd_time_hours_on_smena}"
                                    f" FROM {SQL_TABLE_NAME.local_db_plan_table} "
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

                    self.current_line_id = line_id

                    self.last_change_data = result[0].get(PLAN_TABLE_FIELDS.fd_change_date, None)
                    self.total_day_plane = result[0].get(PLAN_TABLE_FIELDS.fd_plan_current, 1200)
                    self.total_smena_delay = result[0].get(PLAN_TABLE_FIELDS.fd_time_hours_on_smena, 0)

                    Clog.lprint(f"CData -> get_data_for_line ->  Данные получены!")
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
                Clog.lprint(f"Отключение от БД: CONNECT_DB_TYPE.LOCAL [sql_handle: {local_sql.get_sql_handle()}]")
                local_sql.disconnect_from_db()





# unit = CData("Russia")
#
# unit.get_data_for_line(LINE_ID.LINE_VRN_ONE)
