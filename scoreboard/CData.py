from scoreboard.enums import LINE_ID
from common import CCommon
from sql.enums import CONNECT_DB_TYPE
from sql.CSQL import NotConnectToDB, ErrorSQLQuery, ErrorSQLData

from sql.CSQLAgent import CSqlAgent

from log.Clog import Clog

class CData:
    def __init__(self, country_name: str):

        self.country_name = country_name  # Название страны
        self.last_change_data = None  # Дата обновления последняя
        self.total_day_plane = 0  # Дневной план
        self.current_line_id = LINE_ID.LINE_NONE  # Текущая линия
        self.total_smena_delay = 0  # Дневная смена в часах


    def get_data_for_line(self, line_id: LINE_ID):

        self.current_line_id = line_id

        sql_line_id = CCommon.get_line_id_for_sql(line_id)
        if sql_line_id:

            local_sql = CSqlAgent(self.country_name)
            try:
                result = local_sql.connect_to_db(CONNECT_DB_TYPE.LOCAL)
                sql_handle = local_sql.get_sql_handle()
                Clog.lprint(f"Подключение к БД: CONNECT_DB_TYPE.LOCAL [sql_handle: {sql_handle}]")
                if result:

                    query_string = (f"SELECT veh_id FROM {sql_table_vehicles} "
                                    f"WHERE veh_id = %s "
                                    f"LIMIT 1")

                    curs = connect_handle.cursor()
                    curs.execute(query_string, [vehicle_id])



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
