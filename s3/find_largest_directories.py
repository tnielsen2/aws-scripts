from boto3 import Session
from botocore.exceptions import UnauthorizedSSOTokenError
import sys


def bytes_to_megabytes(bytes_value):
    megabytes = bytes_value / 1000000
    return megabytes

# Check the number of arguments
if len(sys.argv) != 3:
    print('Missing command line arguments detected. Usage: python3 find_largest_directories.py <aws profile> <bucket-name>')
    sys.exit(1)

# Retrieve the argument
bucket_name = sys.argv[2]
profile = sys.argv[1]

try:
    print('The bucket-name is:', bucket_name)
    print('The profile is:', profile)

    # Create the session
    session = Session(profile_name=profile)
    # Create the connection
    conn = session.client('s3')
    # Create new empty dictionary
    top_level_folders = dict()
    for key in conn.list_objects(Bucket=bucket_name)['Contents']:

        folder = key['Key'].split('/')[0]
        print(f'Key {key["Key"]} in folder {folder}. {bytes_to_megabytes(key["Size"])} MB')

        if folder in top_level_folders:
            top_level_folders[folder] += bytes_to_megabytes(key['Size'])
        else:
            top_level_folders[folder] = bytes_to_megabytes(key['Size'])


    for folder, size in top_level_folders.items():
        print(f'Folder: {folder}, size: {bytes_to_megabytes(size)}')
except UnauthorizedSSOTokenError:
    raise ValueError(f'The SSO session associated with this profile has expired or is otherwise invalid. To refresh this SSO session run `AWS_DEFAULT_PROFILE={profile} aws sso login` with the corresponding profile.')