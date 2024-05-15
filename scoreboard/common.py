from scoreboard.enums import LINE_ID, BREAK_TYPE
from sql.enums import TIME_ZONES

from datetime import timedelta
from datetime import datetime, timezone


from random import randint


class CCommon:
    # @staticmethod
    # def get_current_unix_time(obj=None) -> int:
    #     if obj is None:
    #         obj = datetime
    #     unix_time = obj.now(timezone.utc)
    #     return int(unix_time.timestamp())   # в utc- (3600 * 3)

    @classmethod
    def get_current_time(cls, time_zone: TIME_ZONES) -> datetime:
        hours_add = 0
        if time_zone == TIME_ZONES.RUSSIA:
            hours_add = 3
        elif time_zone == TIME_ZONES.KZ:
            hours_add = 5
        delta = timedelta(hours=hours_add, minutes=0)
        return datetime.now(timezone.utc) + delta

    @staticmethod
    def timestamp_ex(unix_utc: int) -> int:
        # Независимо от пояса - проверено, так как скрипт работает на GMT 3 сервере и следовательно нужно прибавить 3
        # (хз почему 3)
        sec_add = 3 * 3600
        res = unix_utc + sec_add
        return res

    @staticmethod
    def get_line_id_for_sql(line_id: LINE_ID) -> int | bool:

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
        return False

    @staticmethod
    def get_current_time_zone_for_current_line(line_id: LINE_ID) -> TIME_ZONES:

        if line_id in (LINE_ID.LINE_VRN_ONE,
                       LINE_ID.LINE_VRN_TWO,
                       LINE_ID.LINE_VRN_TRI,
                       LINE_ID.LINE_VRN_FOUR
                       ):
            return TIME_ZONES.RUSSIA
        elif line_id == LINE_ID.LINE_KZ_ONE:
            return TIME_ZONES.KZ
        else:
            return TIME_ZONES.NONE

    @staticmethod
    def get_line_id_type_from_line_id(line_id: int) -> LINE_ID | bool:

        match line_id:
            case 5:
                return LINE_ID.LINE_KZ_ONE
            case 1:
                return LINE_ID.LINE_VRN_ONE
            case 2:
                return LINE_ID.LINE_VRN_TWO
            case 3:
                return LINE_ID.LINE_VRN_TRI
            case 4:
                return LINE_ID.LINE_VRN_FOUR
        return False

    @staticmethod
    def convert_sec_to_hours(sec: int):
        if sec > 60:
            return sec / 60

    @staticmethod
    def get_time_zone_str_from_country_time_zone(time_zone: TIME_ZONES):
        if time_zone == TIME_ZONES.RUSSIA:
            return "0300"  # "0300"
        else:
            return "0500"  # 0500

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

    @classmethod
    def is_current_day_time(cls, time_zone: TIME_ZONES) -> bool:
        """
            Проверка на часы работы линии. Учитывается день
        :return:
        """
        cdate = cls.get_current_time(time_zone)
        # mins = current_datetime.min
        hours = cdate.hour

        if ((hours >= 0) and (hours < 8)) or ((hours >= 21) and (hours <= 23)):
            return False
        else:
            return True

    @staticmethod
    def get_breaks_name(break_type: BREAK_TYPE):
        match break_type:
            case BREAK_TYPE.FIRST:
                return "Время первого перерыва"
            case BREAK_TYPE.EAT:
                return "Время обеда"
            case BREAK_TYPE.DOUBLE:
                return "Время второго перерыва"
            case BREAK_TYPE.LAST:
                return "Время третьего"

    @staticmethod
    def get_random(max_value: int) -> int:
        return randint(1, max_value)

    @staticmethod
    def time_to_utc(time_str: str):
        if time_str.find(":") == -1:
            raise ValueError(f"Ошибка даты {time_str}!")

        time = datetime.strptime(time_str, "%H:%M")
        utc_time = time - timedelta(hours=3)
        return utc_time.strftime("%H:%M")

    @staticmethod
    def utc_to_current_zone_time(time_str: str, current_time_zone: str):
        if time_str.find(":") == -1:
            raise ValueError(f"Ошибка даты {time_str}!")

        time = datetime.strptime(time_str, "%H:%M")
        utc_time = None
        if current_time_zone == "0300":
            utc_time = time + timedelta(hours=3)
        elif current_time_zone == "0500":
            utc_time = time + timedelta(hours=5)
        return utc_time.strftime("%H:%M")
