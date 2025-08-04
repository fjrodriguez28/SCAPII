from app.core import celery
from app.worker.database_worker import DataTransferWorker

@celery.task(bind=True, name="parallel_transfer")
def execute_parallel_transfer(self, transfer_config, task_id):
    worker = ParallelTransferWorker(transfer_config, task_id, self)
    return worker.execute()

class ParallelTransferWorker:
    def execute(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        tables = self.config["tables"]
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            futures = {
                executor.submit(
                    self.transfer_single_table, 
                    table_config
                ): table_config["source_table"]
                for table_config in tables
            }
            
            for future in as_completed(futures):
                table_name = futures[future]
                try:
                    results[table_name] = future.result()
                except Exception as e:
                    results[table_name] = {"status": "FAILED", "error": str(e)}
        
        return {
            "status": "COMPLETED",
            "table_results": results,
            "stats": self.stats
        }
    
    def transfer_single_table(self, table_config):
        # Reutilizar la lógica de transferencia de DataTransferWorker
        table_worker = DataTransferWorker(
            self.config, 
            self.task_id, 
            self.celery_task
        )
        table_worker.connect_databases()
        result = table_worker.transfer_table(table_config)
        table_worker.disconnect()
        return result