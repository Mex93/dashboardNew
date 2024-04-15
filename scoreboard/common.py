from scoreboard.enums import LINE_ID
from sql.enums import TIME_ZONES
from datetime import datetime


class CCommon:
    @staticmethod
    def get_current_unix_time(obj=None) -> int:
        if obj is None:
            obj = datetime
        return int(int(obj.now().timestamp()))

    @staticmethod
    def get_line_id_for_sql(line_id: LINE_ID) -> int:

        match line_id:
            case LINE_ID.LINE_KZ_ONE:
                return 5
            case LINE_ID.LINE_VRN_ONE:
                return 1
            case LINE_ID.LINE_VRN_TWO:
                return 2
            case LINE_ID.LINE_VRN_TRI:
                return 3
            case LINE_ID.LINE_VRN_FOUR:
                return 4

    @staticmethod
    def convert_sec_to_hours(sec: int):
        if sec > 60:
            return sec / 60

    @staticmethod
    def get_time_zone_str_from_country_time_zone(time_zone: TIME_ZONES):
        if time_zone == TIME_ZONES.RUSSIA:
            return "0300"
        else:
            return "0600"
    @staticmethod
    def estimate(value: int, opt: int) -> str:
        # $value = intval($value); $opt = intval($opt);

        if value > (opt * 1.1):
            res = "_XL"
        elif value > (opt * 1.0):
            res = "_L"
        elif value > (opt * 0.80):
            res = "_M"
        elif value > (opt * 0.5):
            res = "_S"
        else:
            res = "_XS"

        return res

    @staticmethod
    def is_current_day_time() -> bool:
        """
            Проверка на часы работы линии. Учитывается день
        :return:
        """
        cdate = datetime.now()
        # mins = current_datetime.min
        hours = cdate.hour

        if ((hours >= 0) and (hours < 8)) or ((hours >= 21) and (hours <= 23)):
            return False
        else:
            return True
