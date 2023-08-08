import base64
import boto3
import docker

def create_myecr(ecr_name):
    print('Creating ECR %s...' % ecr_name)
    ecr_c = boto3.client('ecr')
    resp = ecr_c.create_repository(repositoryName=ecr_name, tags=[{'Key': 'Name', 'Value': ecr_name.upper()}], imageScanningConfiguration={'scanOnPush': False})
    regi_id = resp['repository']['registryId']
    repo_name = resp['repository']['repositoryName']
    repo_uri = resp['repository']['repositoryUri']
    print('Ecr created %s %s %s ...' % (regi_id, repo_name, repo_uri))
    return (regi_id, repo_name, repo_uri)


def describe_myecr(ecr_name):
    ecr_c = boto3.client('ecr')
    resp = ecr_c.describe_repositories(repositoryNames=[ecr_name])
    regi_id = resp['repositories'][0]['registryId']
    repo_name = resp['repositories'][0]['repositoryName']
    repo_uri = resp['repositories'][0]['repositoryUri']
    return (regi_id, repo_name, repo_uri)

def get_myecr_cred(regi_id):
    ecr_c = boto3.client('ecr')
    resp = ecr_c.get_authorization_token(registryIds=[regi_id])
    auths = base64.b64decode(resp['authorizationData'][0]['authorizationToken']).decode('utf-8').split(':')
    return auths

def push_local_ecr(auth_creds, repo_uri, image_name):
    print('Docker login ecr...')
    user = auth_creds[0]
    passwd = auth_creds[1]
    dkr_c = docker.from_env()
    dkr_c.login(username=user, password=passwd, registry=repo_uri)
    img = dkr_c.images.get('local:%s' % image_name)
    print(img.tags)
    img.tag(repository=repo_uri, tag=image_name)
    print('Uploading...')
    for l in dkr_c.images.push(repository=repo_uri, tag=image_name, stream=True, auth_config={'username': user, 'password': passwd}, decode=True):
        print(l)
    print('Uploaded...')

def pull_ecr_local(auth_creds, repo_uri, image_name):
    print('Docker login ecr...')
    print(repo_uri)
    user = auth_creds[0]
    passwd = auth_creds[1]
    dkr_c = docker.from_env()
    dkr_c.login(username=user, password=passwd, registry=repo_uri)
    print('Downloading...')
    dkr_c.images.pull(repository=repo_uri, tag=image_name, auth_config={'username': user, 'password': passwd}, decode=True)
    print('Downloaded...')
    img = dkr_c.images.get('%s:%s' % (repo_uri, image_name))
    img.tag(repository='local', tag=image_name)

def delete_ecr_image(regi_id, repo_name, image_name):
    print('Deleting %s on %s %s' % (image_name, regi_id, repo_name))
    ecr_c = boto3.client('ecr')
    resp = ecr_c.list_images(registryId=regi_id, repositoryName=repo_name)
    print(resp)
    image_ids = ''
    for i in resp['imageIds']:
        for k, v in i.items():
            #if image_name in i['imageTag']:
            if image_name in v:
                image_ids = i
                print(image_ids)
    resp = ecr_c.batch_delete_image(registryId=regi_id, repositoryName=repo_name, imageIds=[image_ids])
    print('Deleted')

def main():
    ecr_name = 'ksdevecr'
    #image_name = 'nginxrtmpfargate'
    #image_name = 'gunicornfargate'
    image_name = 'gunicorn'
    #regi_id, repo_name, repo_uri = create_myecr('ksdevecr')
    regi_id, repo_name, repo_uri = describe_myecr('ksdevecr')
    auths = get_myecr_cred(regi_id)
    print(repo_uri)
    #delete_ecr_image(regi_id, repo_name, image_name)
    push_local_ecr(auths, repo_uri, image_name)
    image_name = 'nginxrtmpfargate'
    push_local_ecr(auths, repo_uri, image_name)
    image_name = 'nginxrtmp'
    push_local_ecr(auths, repo_uri, image_name)
    #pull_ecr_local(auths, repo_uri, image_name)

if __name__ == '__main__':
    main()
