#!/usr/bin/ruby
require 'json'
require 'yaml'
require 'aws-sdk'
#credreg = JSON.load(File.read('aws_key.json'))
credreg = YAML.load(File.read('aws_key.yml'))
Aws.config[:region] = credreg['Region']
Aws.config[:credentials] = Aws::Credentials.new(credreg['AccessKeyId'], credreg['SecretAccessKey'])
s3 = Aws::S3::Client.new
#resp = s3.create_bucket(bucket: "elasticbeanstalk-python")
#myfile_name = "ruby.zip"
#myfile = File.new("/home/greg/ruby.zip")
#resp = s3.create_multipart_upload(bucket: "elasticbeanstalk-python", key: myfile_name)
#myupload_id = resp[:upload_id]
#resp = s3.upload_part(bucket: "elasticbeanstalk-python", key: myfile_name, part_number: 1, upload_id: myupload_id, body: myfile)
#myetag = resp[:etag]
#resp = s3.complete_multipart_upload(bucket: "elasticbeanstalk-python", key: myfile_name, multipart_upload: {parts: [{etag: myetag, part_number: 1}]}, upload_id: myupload_id)
resp = s3.delete_object(bucket: "/elasticbeanstalk-us-east-1-310601264354", key: ".elasticbeanstalk")
resp = s3.delete_bucket(bucket: "/elasticbeanstalk-us-east-1-310601264354")
#resp = s3.delete_object(bucket: "/elasticbeanstalk-python", key: "ruby.zip")
#resp = s3.delete_bucket(bucket: "/elasticbeanstalk-python")
