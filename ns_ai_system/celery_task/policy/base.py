# coding=utf-8
from celery_task import celery_app
from celery_task.policy.tasks import check_single_guide


def get_pending_task(task_name=None):
    pending_task = []
    inspect = None
    while inspect is None or inspect.scheduled() is None:
        inspect = celery_app.control.inspect()
    # print(inspect.reserved().items())
    for worker, worker_tasks in inspect.reserved().items():
        print(len(worker_tasks))
        for task in worker_tasks:
            # print(task["name"])
            if task_name is not None and task["name"] != f"celery_task.policy.tasks.{task_name}":
                continue
            else:
                pending_task.append(task)
    return pending_task


if __name__ == '__main__':
    pass
#     print(celery_app.conf.get("CELERYD_CONCURRENCY"))
#     print(check_single_guide.__name__)
#     get_pending_task("check_single_guide")
# a = {'id': '2701ba99-c189-49ac-97fe-f773547e3458',
#      'name': 'celery.chord_unlock',
#      'args': "('bac9adab-31ee-4afd-9a84-e2ffd3daba0b', {'task': 'celery_task.policy.tasks.check_single_guide_batch_companies_callback', 'args': [], 'kwargs': {'companies': [...], 'guide_id': '115', 'url': 'http://47.107.224.132/enterprise_integrated_services_backstage/matters/smart_push', 'task_id': '6723ccf6-6dc7-11e9-9d5c-00163e06cdb5', 'threshold': 0.0}, 'options': {'max_retries': 1, 'task_id': '6cb4a362-2d4e-45bc-87d2-7fb99690ac2b', 'reply_to': '8e01b9aa-6fb2-3c57-b2f0-65a7a323bec2'}, 'subtask_type': None, 'chord_size': 10, 'immutable': False})",
#      'kwargs': "{'interval': None, 'max_retries': 1, 'result': [[[...], None], [[...], None], [[...], None], [[...], None], [[...], None], [[...], None], [[...], None], [[...], None], [[...], None], [[...], None]]}",
#      'type': 'celery.chord_unlock',
#      'hostname': 'celery@iZwz947of4lcxjw3c833lzZ',
#      'time_start': None,
#      'acknowledged': False,
#      'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': None}, 'worker_pid': None}
