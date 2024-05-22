import psycopg2.extras
import sql.enum_defines as cenum


class NotConnectToDB(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class ErrorSQLQuery(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class ErrorSQLData(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class csql_eng:

    def __init__(self):
        self.__db_connect_data = dict
        self.__db_connect_success = False
        self.__db_handle = None
        self.__db_data_success = False
        self.__sql_error_log = True

        self.__KEY_VALUE_NAME_DATABASE = "database"
        self.__KEY_VALUE_NAME_USER = "user"
        self.__KEY_VALUE_NAME_HOST = "host"
        self.__KEY_VALUE_NAME_PORT = "port"
        self.__KEY_VALUE_NAME_PASS = "password"

    def __del__(self):
        # Деконструктор сам убьёт поток, если где то закрытие sql проебал, как только уничтожится экземпляр класса
        if self.__db_connect_success is True:
            if str(self.__db_handle).find(", closed: 0") != -1:
                # print(str("in destr:" + str(self.__db_handle)))
                self.sql_disconnect()
                # print("Я закрылся")

    """
    Проверка инфы на подключение к БД
    
    """

    def get_value_name_database(self):
        return self.__KEY_VALUE_NAME_DATABASE

    def get_value_name_user(self):
        return self.__KEY_VALUE_NAME_USER

    def get_value_name_host(self):
        return self.__KEY_VALUE_NAME_HOST

    def get_value_name_port(self):
        return self.__KEY_VALUE_NAME_PORT

    def get_value_name_pass(self):
        return self.__KEY_VALUE_NAME_PASS

    def is_valid_saved_connect_data(self) -> bool:  # Проверит сохранённую инфу о подключении

        if self.check_connect_data(cenum.SQL_CONNECT_DATA_TYPE.DB_NAME,
                                   str(self.__db_connect_data[self.__KEY_VALUE_NAME_DATABASE])) is None:
            return False
        if self.check_connect_data(cenum.SQL_CONNECT_DATA_TYPE.DB_NAME,
                                   str(self.__db_connect_data[self.__KEY_VALUE_NAME_USER])) is None:
            return False
        if self.check_connect_data(cenum.SQL_CONNECT_DATA_TYPE.DB_NAME,
                                   str(self.__db_connect_data[self.__KEY_VALUE_NAME_HOST])) is None:
            return False
        if self.check_connect_data(cenum.SQL_CONNECT_DATA_TYPE.DB_NAME,
                                   str(self.__db_connect_data[self.__KEY_VALUE_NAME_PORT])) is None:
            return False
        if self.check_connect_data(cenum.SQL_CONNECT_DATA_TYPE.DB_NAME,
                                   str(self.__db_connect_data[self.__KEY_VALUE_NAME_PASS])) is None:
            return False

        return True

    @staticmethod
    def check_connect_data(stype: cenum.SQL_CONNECT_DATA_TYPE,
                           pstring: str) -> bool:  # Проверит входящий параметр для подключения
        """
        Не дописал. Потом с регулярками запарюсь
        Проверит строку на соответствие каждому типу данных подключения БД

        :param stype:
        :param pstring:
        :return:
        """
        if stype is not cenum.SQL_CONNECT_DATA_TYPE or stype is None:  # Проверить как себя вести будет
            return False
        if pstring is False:
            return False

        match stype:
            case cenum.SQL_CONNECT_DATA_TYPE.PORT:
                if pstring.isnumeric() is False and pstring.__len__() > 11:
                    # На всякий, так как не помню каков должен быть порт
                    return False
            case cenum.SQL_CONNECT_DATA_TYPE.USER_NAME:
                if pstring.__len__() >= 30:
                    return False
            case cenum.SQL_CONNECT_DATA_TYPE.PASSWORD:
                if pstring.__len__() >= 64:
                    return False
            case cenum.SQL_CONNECT_DATA_TYPE.DB_NAME:
                if pstring.__len__() >= 30:
                    return False
            case cenum.SQL_CONNECT_DATA_TYPE.HOST:
                if pstring.__len__() >= 36:
                    return False
            case _:
                return False
        return True

    def get_connect_data(self) -> dict:
        return dict(self.__db_connect_data)

    def set_connect_data(self, new_connect_dict=dict) -> bool:
        """
        Задаёт новые данные для подключения.
        Принимает словарь и из него вытаскивает данные

        :param new_connect_dict:
        :return:
        """
        if new_connect_dict is False:  # If data is empty
            return False

        if self.__db_connect_success is True:
            return False

        buff_dict = self.__db_connect_data  # задампим старые

        self.__db_connect_data = new_connect_dict  # обмен и проверка
        if self.is_valid_saved_connect_data() is False:
            if self.__db_data_success is True:
                self.__db_connect_data = buff_dict
                return False
        self.__db_data_success = True
        return True

    """ SQL движжж """

    def sql_connect(self, time_zone: cenum.TIME_ZONES) -> bool | object:

        if self.is_valid_saved_connect_data() is False:
            return True

        if self.__db_connect_success is True:
            return False

        try:
            # print(self.__db_connect_data)

            connect_handle = psycopg2.connect(host=self.__db_connect_data[self.__KEY_VALUE_NAME_HOST],
                                              database=self.__db_connect_data[self.__KEY_VALUE_NAME_DATABASE],
                                              user=self.__db_connect_data[self.__KEY_VALUE_NAME_USER],
                                              password=self.__db_connect_data[self.__KEY_VALUE_NAME_PASS],
                                              port=self.__db_connect_data[self.__KEY_VALUE_NAME_PORT])

            cur = connect_handle.cursor()

            if time_zone == cenum.TIME_ZONES.RUSSIA:
                cur.execute("SET TIME ZONE 'Europe/Moscow'")
            else:
                cur.execute("SET TIME ZONE 'Asia/Almaty'")
            # cur.execute("SET TIME ZONE 'UTC'")
            self.__db_connect_success = True
            self.__db_handle = connect_handle
            self.__db_data_success = True

            return connect_handle

        except Exception as err:
            if self.__sql_error_log is True:
                self.set_sql_console_log(str(err))
            raise NotConnectToDB("Not Connect To DB!")

    def set_sql_console_log(self, text: str):
        err_str = f"[SQL ERROR] Handle: [{str(self.sql_get_handle())}] Error: {str(text)}"
        print(err_str)

    def clear_db_handle_data(self):

        self.__db_handle = None
        self.__db_connect_success = False
        self.__db_data_success = False

    def sql_disconnect(self):
        if self.__db_connect_success is False:
            return False

        self.__db_handle.close()
        self.clear_db_handle_data()

    def sql_get_handle(self):
        if self.__db_connect_success is False:
            return False

        return self.__db_handle

    def sql_query_and_get_result(self,
                                 sql_handle: psycopg2,
                                 query_str: str,
                                 args: tuple = None,
                                 mode="_a",
                                 count_rows: int = 1) -> bool | tuple | dict:

        """
        Runs SQL request $query by default returns all result raws as an array returns FALSE if query result is empty
        Логика автора и код сохранён
        Аналог функции ms(не нативная) из php из жены Юры скрипта
        Быстрый запрос и результат в массиве, в нашем случае список или словарь
        Только SELECT запросы, остальные нафиг

        :param args:
        :param count_rows:
        :param sql_handle:
        :param query_str:
        :param mode:
        :return:
        """
        s = False  # Результат

        if self.__db_connect_success is False:
            return False

        if len(query_str) == 0:
            return False

        if sql_handle is False:
            """
             Если подключения нет, хендл пришёл пустой или False, 
             так как connect вернёт False если нет удастся подключиться
            """
            return False

        if mode == '_1':
            # Вернёт список кортежей с данными [название строки в бд, данные] (?????)
            # Наподобие ассоциативного массива
            # Проверил. Работает

            if query_str.find("SELECT") == -1:
                return False
            """
            fetch a result row as an associative array. Return false if it's empty 
            
            RealDictCursor — это курсор, который использует реальный dict в качестве базового типа для строк. 
            Этот курсор не позволяет выполнять обычную индексацию для получения данных. 
            данные можно получить только с помощью ключей имен столбцов таблицы.
            """
            try:
                cursor = sql_handle.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cursor.execute(query_str, args)
                #
                s = cursor.fetchall()
                if len(s) == 0:  # Если список пуст, то вернёт 0
                    return False

            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")

            # print(str(s[0]['text'])) - обращение
            #
            #   count_rows = len(s)
            #   print(count_rows)
            #   Количество результата

            # $s = mysqli_fetch_assoc($sql);
            # if (empty($s)) $s = false;

        elif mode == '_l':  # Большой запрос вернёт большой tuple

            # fetch ALL rows. Return first value of a first row
            # Получит все строки. Вернёт первое значение первой строки

            if query_str.find("SELECT") == -1:
                return False

            try:
                cursor = sql_handle.cursor()
                cursor.execute(query_str, args)

                s = cursor.fetchmany(count_rows)

                if len(s) == 0:  # Если список пуст, то вернёт 0
                    return False

            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")

            # $s = mysqli_fetch_all($sql);
            # if (empty($s[0][0])) $s= false;
            # else $s=$s[0][0];
        elif mode == '_u':  # Запрос на обновление или INSERT

            # fetch ALL rows. Return first value of a first row
            # Получит все строки. Вернёт первое значение первой строки
            if query_str.find("UPDATE") == -1:
                return False

            try:

                cursor = sql_handle.cursor()
                cursor.execute(query_str, args)
                sql_handle.commit()
                s = True
            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")
        elif mode == '_d':  # Запрос на delete

            # fetch ALL rows. Return first value of a first row
            # Получит все строки. Вернёт первое значение первой строки
            if query_str.find("DELETE") == -1:
                return False

            try:

                cursor = sql_handle.cursor()
                cursor.execute(query_str, args)
                sql_handle.commit()
                s = True
            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")

        elif mode == '_i':  # Запрос INSERT

            # fetch ALL rows. Return first value of a first row
            # Получит все строки. Вернёт первое значение первой строки
            if query_str.find("INSERT") == -1:
                return False

            try:
                cursor = sql_handle.cursor()
                cursor.execute(query_str, args)
                sql_handle.commit()
                s = cursor.fetchmany(count_rows)

            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")
        else:  # Вернёт все строки в tuple(кортежах)
            # by default: Return all rows as an array
            # В нашем исполнении вернёт список кортежей
            if query_str.find("SELECT") == -1:
                return False

            try:
                cursor = sql_handle.cursor()
                cursor.execute(query_str, args)

                s = cursor.fetchall()

                # print(s)
                if len(s) == 0:  # Если список пуст, то вернёт 0 (в оригинале нет проверки имменно тут на пустой)
                    return False

            except Exception as err:
                if self.__sql_error_log is True:
                    self.set_sql_console_log(str(err))
                    self.sql_disconnect()
                    raise ErrorSQLQuery("Error SQL: Error in query!")

            # $s = array();
            # while ($p=mysqli_fetch_assoc($sql)) $s[]=$p;

        return s
