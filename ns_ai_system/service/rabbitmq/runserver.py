from service.rabbitmq.comsumer import start_consuming,single_guide_callback,multi_guide_callback
import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-q', '--queue', type=str)
	args = parser.parse_args()
	if args.queue == 'single_guide_task':
		start_consuming(single_guide_callback, 'single_guide_task')
	elif args.queue == 'multi_guide_task':
		start_consuming(multi_guide_callback, 'multi_guide_task')
	else:
		print('只能输入single和multi')
