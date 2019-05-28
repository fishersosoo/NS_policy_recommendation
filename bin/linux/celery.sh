#!/bin/bash

arg_help="0"
function parse_arguments() {
  local helperKey="";
  local helperValue="";
  local current="";

  while [ "$1" != "" ]; do
      current=$1;
      helperKey=${current#*--};
      helperKey=${helperKey%%=*};
      helperKey=$(echo "$helperKey" | tr '-' '_');
      helperValue=${current#*=};
      if [ "$helperValue" == "$current" ]; then
        helperValue="1";
      fi
      #echo "eval arg_$helperKey=\"$helperValue\"";

      eval "arg_$helperKey=\"$helperValue\"";
      shift
  done
}

function print_help() {
  cat <<EOF
Usage: ./celery.sh [command] [project path]

Param:
    command      : start | stop | restart | kill
    project path : path to ns_ai_system

   --help  - prints help screen

EOF
}

function start() {
	echo "Starting"
	echo "----------------"
	celery multi start \
	    understand_worker -A celery_task -c 2 -Q understand --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi start \
	    batch_check_callback_worker -A celery_task -c 4 -Q batch_check_callback --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi start \
	    check_single_guide_worker -A celery_task -c 10 -Q check_single_guide --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi start \
	    recommend_task_worker -A celery_task -c 10 -Q recommend_task --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
}

function stop() {
	echo "Warm shutdown. Waiting for tasks to complete."
	echo "(Use 'kill' to perform the cold shutdown)"
	echo "----------------"
	celery multi stop \
	    understand_worker -A celery_task -c 2 -Q understand --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -TERM
	celery multi stop \
	    batch_check_callback_worker -A celery_task -c 4 -Q batch_check_callback --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -TERM
	celery multi stop \
	    check_single_guide_worker -A celery_task -c 10 -Q check_single_guide --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -TERM
	celery multi stop \
	    recommend_task_worker -A celery_task -c 10 -Q recommend_task --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -TERM
}

function killProsess() {
    echo "Cold shutdown. All running task will be lost."
	echo "----------------"
	celery multi stop \
	    understand_worker -A celery_task -c 2 -Q understand --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -QUIT
	celery multi stop \
	    batch_check_callback_worker -A celery_task -c 4 -Q batch_check_callback --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -QUIT
	celery multi stop \
	    check_single_guide_worker -A celery_task -c 10 -Q check_single_guide --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -QUIT
	celery multi stop \
	    recommend_task_worker -A celery_task -c 10 -Q recommend_task --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid -QUIT
}


function restart() {
	echo "restart"
	echo "----------------"
	celery multi restart \
	    understand_worker -A celery_task -c 2 -Q understand --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi restart \
	    batch_check_callback_worker -A celery_task -c 4 -Q batch_check_callback --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi restart \
	    check_single_guide_worker -A celery_task -c 10 -Q check_single_guide --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
    celery multi restart \
	    recommend_task_worker -A celery_task -c 10 -Q recommend_task --logfile=logs/%n.log -l warning --pidfile=pid/%n.pid
}


parse_arguments
if [ "$arg_help" != "0" ]; then
    print_help;
     exit 1;
fi
cd $2
case "$1" in
	start )
		echo "****************"
		mkdir logs
		mkdir pid
		start
		echo "****************"
		;;
	stop )
		echo "****************"
		stop
		echo "****************"
		;;
	restart )
		echo "****************"
		restart
		echo "****************"
		;;
	kill )
		echo "****************"
		killProsess
		echo "****************"
		;;
	* )
		print_help
		;;
esac
