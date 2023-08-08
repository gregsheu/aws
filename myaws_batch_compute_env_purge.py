import boto3
import botocore.waiter

def update_jobqueue(queue_name, env_name):
    print('Update job queue %s to disabled state...' % queue_name)
    bch_c = boto3.client('batch')
    bch_c.update_job_queue(jobQueue=queue_name, state='DISABLED')

def delete_jobqueue(queue_name):
    print('Deleting job queue %s...' % queue_name)
    bch_c = boto3.client('batch')
    bch_c.delete_job_queue(jobQueue=queue_name)

def update_env(env_name):
    print('Update compute env %s to disabled state...' % env_name)
    bch_c = boto3.client('batch')
    bch_c.update_compute_environment(computeEnvironment=env_name, state='DISABLED')

def delete_env(env_name):
    print('Deleting compute env %s...' % env_name)
    bch_c = boto3.client('batch')
    bch_c.delete_compute_environment(computeEnvironment=env_name)

def get_waiter(types):
    bch_c = boto3.client('batch')
    if types == 'queue':
        waiter_id = 'JobQueueWaiter'
        operations = 'DescribeJobQueues'
        argument = 'jobQueues[].status'
    if types == 'env':
        waiter_id = 'ComputeEnvWaiter'
        operations = 'DescribeComputeEnvironments'
        argument = 'computeEnvironments[].status'
    model = botocore.waiter.WaiterModel({
        'version': 2,
        'waiters': {
            waiter_id: {
                'delay': 10,
                'operation': operations,
                'maxAttempts': 10,
                'acceptors': [
                    {
                        'expected': 'VALID',
                        'matcher': 'pathAll',
                        'state': 'success',
                        'argument': argument
                    },
                    {
                        'expected': [],
                        'matcher': 'path',
                        'state': 'success',
                        'argument': argument
                    },
                ]
            }
        }
    })
    waiter = botocore.waiter.create_waiter_with_client(waiter_id, model, bch_c)
    return waiter

def main():
    queue_name = 'KsDevBatchEnvQueue'
    env_name = 'KsDevBatchEnv'
    waiter = get_waiter('queue')
    update_jobqueue(queue_name, env_name)
    waiter.wait(jobQueues=[queue_name])
    delete_jobqueue(queue_name)
    waiter.wait(jobQueues=[queue_name])
    print('Deleted')
    waiter = get_waiter('env')
    update_env(env_name)
    waiter.wait(computeEnvironments=[env_name])
    delete_env(env_name)
    waiter.wait(computeEnvironments=[env_name])
    print('Deleted')

if __name__ == '__main__':
    main()
