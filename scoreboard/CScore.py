from scoreboard.enums import JOB_TYPE, JOB_STATUS

class CSore:
    def __init__(self):
        # Основное с вывода табло

        # слева табло
        self.total_day_plan = 0  # Дневной план
        self.total_day_plan_speed = 0  # Расчётная скорость телеков в час относительно дневного плана (Меняыется только со сменой плана)
        # справа табло
        self.assembled_device = 0  # Собранных на текущий момент
        self.assembled_device_speed = 0  # Скорость в час относительно собранных по факту

        # футер
        self.assembled_speed_for_last_five_mins = 0  # Собрано за последние 5 минут
        self.assembled_speed_for_last_one_hour = 0  # Собрано за последний час
        self.assembled_forecast_for_day = 0  # Прогноз за день

        self.current_job_time = JOB_TYPE.NONE  # Тип рабочего времени - день и ночь
        self.current_job_status = JOB_STATUS.NONE  # Статус работы - закончена, идёт, перерыв итд


    def reload_data(self):
        pass

    def get_12hours_data(self):
        pass

    def get_one_hours_data(self):
        pass
    def clear_data(self):
        pass



