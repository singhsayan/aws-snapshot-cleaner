import boto3
from datetime import datetime, timezone, timedelta

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    sns = boto3.client('sns')

    SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:<Your Account Id>:snapshot-alerts'
    COST_PER_GB = 0.05  # USD/month
    AGE_THRESHOLD_DAYS = 30

    deleted_snapshots = []
    total_estimated_savings = 0.0

    # Get current time
    now = datetime.now(timezone.utc)

    # Get all snapshots owned by you
    response = ec2.describe_snapshots(OwnerIds=['self'])

    for snapshot in response['Snapshots']:
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')
        start_time = snapshot['StartTime']
        age = (now - start_time).days

        # Only consider if older than threshold
        if age < AGE_THRESHOLD_DAYS:
            continue

        size_gb = snapshot['VolumeSize']

        try:
            if not volume_id:
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                deleted_snapshots.append(f"{snapshot_id} (no volume, age: {age} days)")
                total_estimated_savings += size_gb * COST_PER_GB
            else:
                volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                if not volume_response['Volumes'][0]['Attachments']:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(f"{snapshot_id} (volume not attached, age: {age} days)")
                    total_estimated_savings += size_gb * COST_PER_GB
        except ec2.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                deleted_snapshots.append(f"{snapshot_id} (volume not found, age: {age} days)")
                total_estimated_savings += size_gb * COST_PER_GB

    # Send SNS alert
    if deleted_snapshots:
        message = (
            "Deleted the following stale EBS Snapshots:\n\n" +
            "\n".join(deleted_snapshots) +
            f"\n\n Estimated Monthly Savings: ${total_estimated_savings:.2f}"
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EBS Snapshot Cleanup & Cost Savings",
            Message=message
        )
