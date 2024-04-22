from enum import IntEnum


class LINE_ID(IntEnum):
    LINE_NONE = -1,
    LINE_VRN_ONE = 0,
    LINE_VRN_TWO = 1,
    LINE_VRN_TRI = 3,
    LINE_VRN_FOUR = 4,
    LINE_KZ_ONE = 5


class JOB_TYPE(IntEnum):
    NONE = 0,
    DAY = 1,
    NIGHT = 2


class JOB_TIME(IntEnum):
    NONE = 0,
    START = 1,
    END = 2


class JOB_BREAK_ARRAY_DATA(IntEnum):
    START = 0,
    END = 1,
    DELAY = 2


class JOB_STATUS(IntEnum):
    NONE = 0,
    JOB_IN_PROCESS = 1,
    JOB_BREAK = 2,
    JOB_END = 3


class BREAK_TYPE(IntEnum):
    NONE = 0,
    FIRST = 1,
    EAT = 2,
    DOUBLE = 3,
    LAST = 4


class BREAK_ARRAY_DATA(IntEnum):
    BREAK_TYPE = 0,
    DELAY_SEC = 1,
    START_TIME = 2,


class DATA_SCORE_TYPE(IntEnum):
    NONE = 0,
    ONE_HOUR_DATA = 1,
    FIVE_MINS_DATA = 2,
