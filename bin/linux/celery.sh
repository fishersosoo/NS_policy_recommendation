!/bin/bash

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
Usage: ./celery.sh [command] [project path] [log path]

Param:
    command      : start | stop | restart | kill
    project path : path to ns_ai_system

   --help  - prints help screen

EOF
}

function start() {
	echo "Starting"
	echo "----------------"
	celery multi start\
	    understand_worker batch_check_callback_worker check_single_guide_worker recommend_task_worker \
	    -A celery_task --logfile=/data/logs/%n.log -l warning --pidfile=pid/%n.pid \
	    -c:understand_worker 2 -c:batch_check_callback_worker 4 -c:check_single_guide_worker 10 -c:recommend_task_worker 10 \
	    -Q:understand_worker understand -Q:batch_check_callback_worker batch_check_callback \
	    -Q:check_single_guide_worker check_single_guide -Q:recommend_task_worker recommend_task
}

function stop() {
	echo "Warm shutdown. Waiting for tasks to complete."
	echo "(Use 'kill' to perform cold shutdown)"
	echo "----------------"
	celery multi stop\
	    understand_worker batch_check_callback_worker check_single_guide_worker recommend_task_worker \
	    -A celery_task --logfile=/data/logs/%n.log -l warning --pidfile=pid/%n.pid \
	    -c:understand_worker 2 -c:batch_check_callback_worker 4 -c:check_single_guide_worker 10 -c:recommend_task_worker 10 \
	    -Q:understand_worker understand -Q:batch_check_callback_worker batch_check_callback \
	    -Q:check_single_guide_worker check_single_guide -Q:recommend_task_worker recommend_task \
	    -TERM
}

function killProsess() {
    echo "Cold shutdown. All running task will be lost."
	echo "----------------"
	celery multi stop\
	    understand_worker batch_check_callback_worker check_single_guide_worker recommend_task_worker \
	    -A celery_task --logfile=/data/logs/%n.log -l warning --pidfile=pid/%n.pid \
	    -c:understand_worker 2 -c:batch_check_callback_worker 4 -c:check_single_guide_worker 10 -c:recommend_task_worker 10 \
	    -Q:understand_worker understand -Q:batch_check_callback_worker batch_check_callback \
	    -Q:check_single_guide_worker check_single_guide -Q:recommend_task_worker recommend_task \
	    -QUIT
}


function restart() {
	echo "Restarting. Warm shutdown before restart. "
	echo "(Manually use 'kill' and 'start' to perform cold shutdown)"
	echo "----------------"
	celery multi restart\
	    understand_worker batch_check_callback_worker check_single_guide_worker recommend_task_worker \
	    -A celery_task --logfile=/data/logs/%n.log -l warning --pidfile=pid/%n.pid \
	    -c:understand_worker 2 -c:batch_check_callback_worker 4 -c:check_single_guide_worker 10 -c:recommend_task_worker 10 \
	    -Q:understand_worker understand -Q:batch_check_callback_worker batch_check_callback \
	    -Q:check_single_guide_worker check_single_guide -Q:recommend_task_worker recommend_task
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
		mkdir /data/logs
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
