from scoreboard.enums import LINE_ID


class CCommon:

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
