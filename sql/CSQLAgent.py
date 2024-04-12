from sql.CSQL import csql_eng, ErrorSQLData, ErrorSQLQuery, NotConnectToDB
import sql.enums as cenum
from sql.config import db_standart_connect_params, db_assembly_connect_params


class CSqlAgent(csql_eng):
    def __init__(self, time_zone: cenum.TIME_ZONES):
        super().__init__()

        self.__connect_handle = False

        self.__sql_data_line = db_assembly_connect_params
        self.__sql_data_local = db_standart_connect_params
        self.__time_zone = time_zone

    def get_sql_handle(self):
        return self.__connect_handle

    def connect_to_db(self, connect_db_type: cenum.CONNECT_DB_TYPE) -> bool:
        if self.__connect_handle is False:

            if connect_db_type == cenum.CONNECT_DB_TYPE.LINE:
                self.set_connect_data(self.__sql_data_line)
            elif connect_db_type == cenum.CONNECT_DB_TYPE.LOCAL:
                self.set_connect_data(self.__sql_data_local)
            else:
                raise ErrorSQLData("Error SQL | db changed connect type!")
            if self.is_valid_saved_connect_data() is False:  # Saved in config data is NOT correct
                raise ErrorSQLData("Error SQL | incomming connections data!")

            connect_handle = self.sql_connect(self.__time_zone)
            if connect_handle is False:  # Connecting not successful
                raise NotConnectToDB("Error SQL | db not connect!")

            self.__connect_handle = connect_handle
            return True

        return False

    def disconnect_from_db(self) -> bool:
        if self.__connect_handle is not False:
            self.sql_disconnect()
            self.__connect_handle = False
            return True
        return False
