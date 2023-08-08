import boto3

def sub_n_del(queueurl):
    sqs_c = boto3.client('sqs')
    while True:
        try:
            resp = sqs_c.receive_message(QueueUrl=queueurl)
            message = resp['Messages'][0]['Body']
            receipt_handle = resp['Messages'][0]['ReceiptHandle']
            print(message)
            sqs_c.delete_message(QueueUrl=queueurl, ReceiptHandle=receipt_handle)
        except:
            print('Waiting')

def main():
    queueurl = 'https://sqs.us-east-2.amazonaws.com/141056581104/KsDevQ1'
    sub_n_del(queueurl)

if __name__ == '__main__':
    main()
