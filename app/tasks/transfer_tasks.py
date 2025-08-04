from celery import shared_task
from app.worker.database_worker import DataTransferWorker

@shared_task(bind=True, name="transfer_task")
def start_transfer(self, transfer_config,db_task_id):
    worker = DataTransferWorker(transfer_config, db_task_id,self)
    return worker.execute_transfer()

