import argparse
import boto3
from datetime import datetime, timedelta

# Parse command line arguments
parser = argparse.ArgumentParser(description='Delete AWS backup recovery points that are more than 14 days old.')
parser.add_argument('--region', help='AWS region to use')
parser.add_argument('--profile', help='AWS profile to use')
args = parser.parse_args()

# Initialize AWS clients
ec2 = boto3.Session(profile_name=args.profile).client('ec2', region_name=args.region)
backup = boto3.Session(profile_name=args.profile).client('backup', region_name=args.region)

# Calculate 14 days ago
days_ago = datetime.now() - timedelta(days=14)

# Get list of all EBS snapshots
snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']

# Get list of all AMIs
images = ec2.describe_images(Owners=['self'])['Images']

# Loop through all snapshots and print recovery points that are more than 14 days old
for snapshot in snapshots:
    snapshot_date = snapshot['StartTime']
    if snapshot_date < days_ago:
        backup_id = snapshot['Description']
        print(f"Recovery point {backup_id} for EBS snapshot {snapshot['SnapshotId']} will be deleted.")

# Loop through all images and print recovery points that are more than 14 days old
for image in images:
    image_date = datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if image_date < days_ago:
        backup_id = image['ImageId']
        print(f"Recovery point {backup_id} for AMI {image['ImageId']} will be deleted.")
