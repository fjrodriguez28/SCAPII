#!/usr/bin/env python
"""
Main entry point for Celery workers
"""
import os
from app.core.celery import celery_app
from app.core.config import settings

# Configuración importante para el worker
if __name__ == "__main__":
    # Configurar el nivel de logging
    os.environ.setdefault('CELERY_LOG_LEVEL', 'INFO')
    os.environ.setdefault('CELERY_LOG_FILE', 'celery_worker.log')
    
    # Iniciar el worker con configuración personalizada
    celery_app.start(argv=[
        'worker',
        '--loglevel=' + os.getenv('CELERY_LOG_LEVEL', 'INFO'),
        '--concurrency=' + str(settings.CELERY_CONCURRENCY),
        '--hostname=' + settings.CELERY_WORKER_PREFIX + '@%h',
        '--queues=' + settings.CELERY_QUEUES,
        '--max-tasks-per-child=' + str(settings.CELERY_MAX_TASKS_PER_CHILD),        
        '--without-gossip',
        '--without-mingle',
        '--without-heartbeat',
        '--events'
    ])
    # celery_app.start(argv=[
    #     'worker',
    #     '--loglevel=' + os.getenv('CELERY_LOG_LEVEL', 'INFO'),
    #     '--concurrency=' + str(settings.CELERY_CONCURRENCY),
    #     '--hostname=' + settings.CELERY_WORKER_PREFIX + '@%h',
    #     '--queues=' + settings.CELERY_QUEUES,
    #     '--max-tasks-per-child=' + str(settings.CELERY_MAX_TASKS_PER_CHILD),
    #     '--max-memory-per-child=' + str(settings.CELERY_MAX_MEMORY_PER_CHILD),
    #     '--without-gossip',
    #     '--without-mingle',
    #     '--without-heartbeat',
    #     '--events'
    # ])