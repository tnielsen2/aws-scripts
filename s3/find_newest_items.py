import boto3
import datetime
import pytz
import sys

# Check the number of arguments
if len(sys.argv) != 2:
    print('Missing command line arguments detected. Usage: python3 s3/find_newest_items.py <bucket-name>')
    sys.exit(1)

# Retrieve the argument
bucket_name = sys.argv[1]

# Create a connection to the S3 service
s3 = boto3.resource('s3')

# Get the current time
now = datetime.datetime.now(pytz.utc)

# Calculate the time 24 hours ago
days_ago = now - datetime.timedelta(days=4)

# Iterate over all objects in the bucket
for obj in s3.Bucket(bucket_name).objects.all():
    # Check if the object was created or updated within the past 24 hours
    if obj.last_modified >= days_ago:
        # Print the object key and last modified time
        print(f'{obj.key} was last modified at {obj.last_modified}')
