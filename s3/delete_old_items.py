import boto3
import datetime
import pytz
import sys

# Check the number of arguments
if len(sys.argv) != 2:
    print('Missing command line arguments detected. Usage: python3 s3/delete_old_items.py <bucket-name>')
    sys.exit(1)

# Retrieve the argument
bucket_name = sys.argv[1]

# Create a connection to the S3 service
s3 = boto3.resource('s3')

# Get the current time
now = datetime.datetime.now(pytz.utc)

# Calculate the time 30 days ago
days_ago = now - datetime.timedelta(days=30)

# Iterate over all objects in the bucket
for obj in s3.Bucket(bucket_name).objects.all():
    # Check if the object was created or updated more than 30 days ago
    if obj.last_modified <= days_ago:
        # Delete the object
        obj.delete()
        # Print a message indicating that the object was deleted
        print(f'{obj.key} was deleted because it was last modified more than 30 days ago')
    else:
        # Print a message indicating that the object was not deleted
        print(f'{obj.key} was not deleted because it was last modified within the past 30 days')
