import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal

def lambda_handler(event, context):
    """
    Analyze S3 buckets - check all buckets with basic useful metrics.
    """
    s3 = boto3.client('s3')
    cloudwatch = boto3.client('cloudwatch')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CostOptimizerFindings')
    
    findings = []
    
    try:
        # Get all S3 buckets
        response = s3.list_buckets()
        
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            creation_date = bucket['CreationDate']
            
            print(f"Analyzing S3 bucket: {bucket_name}")
            
            # Get bucket region
            try:
                location = s3.get_bucket_location(Bucket=bucket_name)
                region = location['LocationConstraint'] or 'us-east-1'
            except Exception as e:
                print(f"Error getting location for {bucket_name}: {str(e)}")
                region = 'unknown'
            
            # Get bucket size and object count
            bucket_size_bytes, object_count = get_bucket_size(cloudwatch, bucket_name)
            bucket_size_gb = bucket_size_bytes / (1024**3)
            
            # Get storage class breakdown
            storage_classes = get_storage_class_breakdown(s3, bucket_name)
            
            # Check versioning
            versioning_status = get_versioning_status(s3, bucket_name)
            
            # Check public access
            is_public = check_public_access(s3, bucket_name)
            
            # Get request metrics (last 7 days)
            get_requests = get_request_metrics(cloudwatch, bucket_name, 'GetRequests')
            put_requests = get_request_metrics(cloudwatch, bucket_name, 'PutRequests')
            
            # Calculate bucket age
            age_days = (datetime.now(creation_date.tzinfo) - creation_date).days
            
            # Record the bucket with metrics
            finding = {
                "id": bucket_name,
                'resource_id': bucket_name,
                'resource_type': 'S3',
                'issue': 's3_bucket',
                'severity': 'info',
                'details': f'S3 Bucket: {bucket_name}',
                'recommendation': f'Size: {bucket_size_gb:.2f}GB, Objects: {object_count:,}',
                'metadata': {
                    'bucket_name': bucket_name,
                    'region': region,
                    'age_days': age_days,
                    'size_gb': Decimal(str(round(bucket_size_gb, 2))),
                    'object_count': object_count,
                    'storage_classes': storage_classes,
                    'versioning_enabled': versioning_status,
                    'is_public': is_public,
                    'get_requests_7d': int(get_requests),
                    'put_requests_7d': int(put_requests),
                    'creation_date': creation_date.isoformat()
                },
                'timestamp': datetime.now().isoformat()
            }
            findings.append(finding)
        
        # Store findings in DynamoDB
        for finding in findings:
            table.put_item(Item=finding)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'findings_count': len(findings),
                'message': f'Analyzed {len(findings)} S3 buckets',
                'findings': findings
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error analyzing S3 buckets: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def get_bucket_size(cloudwatch, bucket_name):
    """Get bucket size in bytes and number of objects from CloudWatch."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    try:
        # Get bucket size
        size_response = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='BucketSizeBytes',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'StandardStorage'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=['Average']
        )
        
        bucket_size = 0
        if size_response['Datapoints']:
            bucket_size = size_response['Datapoints'][0]['Average']
        
        # Get object count
        count_response = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='NumberOfObjects',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=['Average']
        )
        
        object_count = 0
        if count_response['Datapoints']:
            object_count = int(count_response['Datapoints'][0]['Average'])
        
        return bucket_size, object_count
        
    except Exception as e:
        print(f"Error getting bucket size for {bucket_name}: {str(e)}")
        return 0, 0


def get_storage_class_breakdown(s3, bucket_name):
    """Get breakdown of storage classes in the bucket (sample of first 1000 objects)."""
    storage_classes = {}
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1000)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                storage_class = obj.get('StorageClass', 'STANDARD')
                storage_classes[storage_class] = storage_classes.get(storage_class, 0) + 1
        
        return storage_classes
        
    except Exception as e:
        print(f"Error getting storage classes for {bucket_name}: {str(e)}")
        return {}


def get_versioning_status(s3, bucket_name):
    """Check if versioning is enabled on the bucket."""
    try:
        response = s3.get_bucket_versioning(Bucket=bucket_name)
        status = response.get('Status', 'Disabled')
        return status == 'Enabled'
    except Exception as e:
        print(f"Error checking versioning for {bucket_name}: {str(e)}")
        return False


def check_public_access(s3, bucket_name):
    """Check if bucket has public access."""
    try:
        response = s3.get_public_access_block(Bucket=bucket_name)
        config = response['PublicAccessBlockConfiguration']
        
        # If all public access is blocked, bucket is not public
        all_blocked = (
            config.get('BlockPublicAcls', False) and
            config.get('IgnorePublicAcls', False) and
            config.get('BlockPublicPolicy', False) and
            config.get('RestrictPublicBuckets', False)
        )
        
        return not all_blocked
        
    except Exception as e:
        # If no public access block is configured, assume potentially public
        print(f"Error checking public access for {bucket_name}: {str(e)}")
        return True


def get_request_metrics(cloudwatch, bucket_name, metric_name, days=7):
    """Get total S3 requests (GET or PUT) over the last 7 days."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName=metric_name,
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Sum']
        )
        
        if response['Datapoints']:
            total_requests = sum(d['Sum'] for d in response['Datapoints'])
            return total_requests
        
        return 0
    except Exception as e:
        print(f"Error getting request metrics for {bucket_name}: {str(e)}")
        return 0

if __name__ == "__main__":
    print(lambda_handler({}, {}))