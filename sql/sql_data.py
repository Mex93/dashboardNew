# Название всех таблиц скрипта
class SQL_TABLE_NAME:
    user_accounts = "acp_users"
    assembled_tv = "assembled_tv"
    asr_tv = "unfinished_tv"
    tv_model_info_tv = "tv"
    user_logs = "acp_log"
    local_db_plan_table = "plan_settings"


# Название полей в конфиге готовых тв
class PLAN_TABLE_FIELDS:
    fd_line_id = "line_id"
    fd_plan_current = "plan_current"
    fd_change_date = "last_change_date"
    fd_change_user_id = "change_user_id"
    fd_primary_key = "auto_idx"

    # Время старта перерывов в часах:минутах
    # Хранится просто в строке
    fd_brake_first_time_day_start = "brake_first_time_day_start"
    fd_brake_eat_time_day_start = "brake_eat_time_day_start"
    fd_brake_double_time_day_start = "brake_double_time_day_start"
    fd_brake_third_time_day_start = "brake_third_time_day_start"

    fd_brake_first_time_night_start = "brake_first_time_night_start"
    fd_brake_eat_time_night_start = "brake_eat_time_night_start"
    fd_brake_double_time_night_start = "brake_double_time_night_start"
    fd_brake_third_time_night_start = "brake_third_time_night_start"

    # Время длительности перерывов в минутах
    # Хранится просто в integer

    fd_brake_first_time_day_len = "brake_first_time_day_len"
    fd_brake_eat_time_day_len = "brake_eat_time_day_len"
    fd_brake_double_time_day_len = "brake_double_time_day_len"
    fd_brake_third_time_day_len = "brake_third_time_day_len"

    fd_brake_first_time_night_len = "brake_first_time_night_len"
    fd_brake_eat_time_night_len = "brake_eat_time_night_len"
    fd_brake_double_time_night_len = "brake_double_time_night_len"
    fd_brake_third_time_night_len = "brake_third_time_night_len"

    fd_time_hours_on_smena = "smena_hours"

    # Время в час:минута
    fd_time_day_job_start = "smena_day_time_start"
    fd_time_day_job_end = "smena_day_time_end"

    fd_time_night_job_start = "smena_night_time_start"
    fd_time_night_job_end = "smena_night_time_end"

    fd_mena_start_job_date_stamp = "smena_start_job_date"
    fd_smena_start_job_type = "smena_start_job_type"
