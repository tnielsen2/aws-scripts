import argparse
import boto3
from datetime import datetime, timedelta
import pytz

# Parse command line arguments
parser = argparse.ArgumentParser(description='Delete AWS backup recovery points that are more than 14 days old.')
parser.add_argument('--region', help='AWS region to use')
parser.add_argument('--profile', help='AWS profile to use')
args = parser.parse_args()

# Initialize AWS clients
ec2 = boto3.Session(profile_name=args.profile).client('ec2', region_name=args.region)
backup = boto3.Session(profile_name=args.profile).client('backup', region_name=args.region)
rds = boto3.Session(profile_name=args.profile).client('rds', region_name=args.region)

# Calculate 14 days ago
days_ago = datetime.now(pytz.utc) - timedelta(days=14)

# Open log files
ami_log_file = open('ami.log', 'w')
volume_log_file = open('volumes.log', 'w')
rds_log_file = open('rds.log', 'w')

# Loop through all EBS snapshots and print recovery points that are more than 14 days old
snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
snapshots = sorted(snapshots, key=lambda x: x['StartTime'])
for snapshot in snapshots:
    snapshot_date = snapshot['StartTime'].replace(tzinfo=pytz.utc)
    if snapshot_date < days_ago:
        backup_id = snapshot['Description']
        creation_time = snapshot['StartTime'].strftime('%Y-%m-%d %H:%M:%S %Z')
        volume_log_file.write(f"Recovery point {backup_id} for EBS snapshot {snapshot['SnapshotId']} created on {creation_time} will be deleted.\n")
        # Uncomment the following line to delete the EBS snapshot
        # ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])

# Loop through all AMIs and print recovery points that are more than 14 days old
images = ec2.describe_images(Owners=['self'])['Images']
images = sorted(images, key=lambda x: datetime.strptime(x['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))
for image in images:
    image_date = datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
    if image_date < days_ago:
        backup_id = image['ImageId']
        creation_time = image['CreationDate'].replace('T', ' ').replace('Z', ' UTC')
        ami_log_file.write(f"Recovery point {backup_id} for AMI {image['ImageId']} created on {creation_time} will be deleted.\n")
        # Uncomment the following line to deregister the AMI
        # ec2.deregister_image(ImageId=image['ImageId'])

# Loop through all RDS snapshots and print those that are more than 14 days old
db_snapshots = rds.describe_db_snapshots(SnapshotType='all')['DBSnapshots']
db_snapshots = sorted(db_snapshots, key=lambda x: x['SnapshotCreateTime'])
for db_snapshot in db_snapshots:
    snapshot_date = db_snapshot['SnapshotCreateTime'].replace(tzinfo=pytz.utc)
    if snapshot_date < days_ago:
        snapshot_id = db_snapshot['DBSnapshotIdentifier']
        creation_time = db_snapshot['SnapshotCreateTime'].strftime('%Y-%m-%d %H:%M:%S %Z')
        rds_log_file.write(f"Snapshot {snapshot_id} for RDS instance {db_snapshot['DBInstanceIdentifier']} created on {creation_time} will be deleted.\n")
        # Uncomment the following line to remove the snapshot
        # rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
