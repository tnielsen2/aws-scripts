import argparse
import boto3
import logging
from datetime import datetime, timedelta
import pytz

# usage
# python3 ./aws-backup/delete_old_backup_recovery_points.py --region us-east-2 --profile yam-pxg --vault uat-a-us-east-2-backups-vault --plan uat-a-tier-3-archives
# Parse command line arguments
parser = argparse.ArgumentParser(description='Delete AWS backup recovery points that are more than 14 days old.')
parser.add_argument('--region', help='AWS region to use')
parser.add_argument('--profile', help='AWS profile to use')
parser.add_argument('--vault', help='Name of the backup vault to query')
#parser.add_argument('--plan', help='ID of the backup plan. Ex: 12345678-1234-1234-1234-123456789123')
args = parser.parse_args()

# set up logging to file
logging.basicConfig(filename='backup-deletion.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize AWS client
backup = boto3.Session(profile_name=args.profile).client('backup', region_name=args.region)

# Calculate days_ago
days_ago = datetime.now(pytz.utc) - timedelta(days=14)

# find all recovery points older than days_ago
response = backup.list_recovery_points_by_backup_vault(
    BackupVaultName=args.vault,
    ByCreatedBefore=days_ago
)

recovery_points = response['RecoveryPoints']
recovery_points_sorted = sorted(recovery_points, key=lambda rp: rp['CompletionDate'], reverse=True)

# delete the recovery points
for recovery_point in recovery_points_sorted:
    backup.delete_recovery_point(
        BackupVaultName=args.vault,
        RecoveryPointArn=recovery_point['RecoveryPointArn']
    )
    logging.info(f"Deleted recovery point {recovery_point['RecoveryPointArn']}, CompletionDate: {recovery_point['CompletionDate']}")

# find all snapshots older than days_ago
#response = backup.list_backup_plan_versions(
#    BackupPlanId=args.plan
#)

#if 'BackupPlanVersions' not in response:
#    print(f"No backup plan versions found for plan {args.plan}")
#    exit(0)
#else:
#    # iterate over all the available versions of the specified backup plan
#    for version in response['BackupPlanVersions']:
#        for backup_rule in version['BackupPlan']['Rules']:
#            if backup_rule['RuleName'] == 'my-snapshot-rule':
#                snapshot_id = backup_rule['TargetBackupVault']['RegexPattern']
#                backup.delete_backup(
#                    BackupVaultName=snapshot_id,
#                    BackupId=version['BackupPlanArn']
#                )
#                logging.info(f"Deleted snapshot {version['BackupPlanArn']} for {snapshot_id}")
