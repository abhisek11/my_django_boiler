# from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
# from attendance.attendence_mail_pending import my_attendence_mail_before_lock_job

# def start():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(my_attendence_mail_before_lock_job, 'interval', minutes=1)
#     scheduler.start()