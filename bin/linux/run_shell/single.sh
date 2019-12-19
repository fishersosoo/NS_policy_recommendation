#!/bin/bash
nohup python -u NS_policy_recommendation/ns_ai_system/service/rabbitmq/runserver.py -q single_guide_task > /home/web/NS_policy_recommendation/ns_ai_system/logs/single_guide_task.log 2>&1 &
nohup python -u NS_policy_recommendation/ns_ai_system/service/rabbitmq/runserver.py -q single_guide_task > /home/web/NS_policy_recommendation/ns_ai_system/logs/single_guide_task.log 2>&1 &
exit 0

