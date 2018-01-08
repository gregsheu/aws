#!/usr/bin/ruby
require 'aws-sdk'
s3 = Aws::S3::Client.new
resp = s3.create_bucket(bucket: "elasticbeanstalk-python")
#resp = s3.delete_bucket(bucket: "elasticbeanstalk-python")
