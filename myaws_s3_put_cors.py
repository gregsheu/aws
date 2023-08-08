import boto3

s3_c = boto3.client('s3')
s3_c.create_bucket(Bucket='ksdevgpswest2', ACL='private', CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})
s3_c.put_bucket_cors(Bucket='ksdevgpswest2', CORSConfiguration={'CORSRules': [{ 'AllowedHeaders': [ '*' ], 'AllowedMethods': [ 'GET', 'HEAD' ], 'AllowedOrigins': [ '*' ]}]})

#AWS.config.update({accessKeyId: 'AKIASBV5ATXYHLWJB4QH', secretAccessKey: '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'});

