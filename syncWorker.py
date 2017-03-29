import schedule
import time
from syncJobStorage import storage_number_sync_main_job

def sync_job_storage():
    #print("I'm working...")
    storage_number_sync_main_job()

#schedule.every(10).seconds.do(job)
#schedule.every().hour.do(sync_job_storage)
#schedule.every().day.at("10:30").do(job)
#schedule.every().monday.do(job)
#schedule.every().wednesday.at("13:15").do(job)

#while True:
#    schedule.run_pending()
#    time.sleep(1)
sync_job_storage()