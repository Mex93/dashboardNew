from scoreboard.enum_defines import LINE_ID, BREAK_TYPE
from sql.enum_defines import TIME_ZONES

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

        for line in LINE_ID:
            if line == line_id:
                return line.value

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

        elif line_id in (
                       LINE_ID.LINE_LINE_REZERV_1,
                       LINE_ID.LINE_LINE_REZERV_2,
                       LINE_ID.LINE_LINE_REZERV_3,
                       LINE_ID.LINE_LINE_REZERV_4,
                       LINE_ID.LINE_LINE_REZERV_5,
                       LINE_ID.LINE_LINE_REZERV_6,
                       LINE_ID.LINE_LINE_REZERV_7,
                       LINE_ID.LINE_LINE_REZERV_8,
                       LINE_ID.LINE_LINE_REZERV_9,
                       ):
            return TIME_ZONES.RUSSIA
        else:
            return TIME_ZONES.NONE

    @staticmethod
    def get_line_id_type_from_line_id(line_id: int) -> LINE_ID | bool:

        for line in LINE_ID:  # line.name ?
            if line.value == line_id:
                return line
        return False

    @staticmethod
    def convert_sec_to_hours(sec: int):
        if sec > 60:
            return sec / 60

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

    @classmethod
    def is_night_job_hour(cls, time_zone: TIME_ZONES) -> bool:
        """
            Проверка на часы работы линии. Учитывается день
        :return:
        """
        cdate = cls.get_current_time(time_zone)
        # mins = current_datetime.min
        hours = cdate.hour

        if (hours == 0 or
                hours == 1 or
                hours == 2 or
                hours == 3 or
                hours == 4 or
                hours == 5 or
                hours == 6 or
                hours == 7):
            return True
        else:
            return False

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
