# coding=utf-8
from celery_task import celery_app


def get_pending_task(task_name=None):
    pending_task = []
    inspect=None
    while inspect is None or inspect.scheduled() is None:
        inspect = celery_app.control.inspect()
    print(inspect.scheduled())
    for worker,worker_tasks in inspect.scheduled().items():
        print(worker)
        for task in worker_tasks:
            print(task["request"]["name"])
            if task_name is not None and task["request"]["name"] != f"tasks.{task_name}":
                continue
            else:
                pending_task.append(task)
    return pending_task

