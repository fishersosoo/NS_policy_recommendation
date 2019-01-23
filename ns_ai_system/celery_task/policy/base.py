# coding=utf-8
from celery_task import celery_app


def get_pending_task(task_name=None):
    pending_task = []
    inspect = celery_app.control.inspect()
    for worker in inspect.scheduled():
        for work_name, worker_tasks in worker.items():
            for task in worker_tasks:
                print(task["request"]["name"])
                if task_name is not None and task["request"]["name"] != f"tasks.{task_name}":
                    continue
                else:
                    pending_task.append(task)
    return pending_task

