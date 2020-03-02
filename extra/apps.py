from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'

    # def ready(self):
    #     import shedular
    #     shedular.start()