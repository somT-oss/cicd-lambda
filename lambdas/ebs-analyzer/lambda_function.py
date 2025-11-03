import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal

def lambda_handler(event, context):
    """
    Analyze EBS volumes - check all volumes with basic useful metrics.
    """
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CostOptimizerFindings')
    
    findings = []
    
    try:
        # Get all EBS volumes
        response = ec2.describe_volumes()
        
        for volume in response['Volumes']:
            volume_id = volume['VolumeId']
            volume_type = volume['VolumeType']
            size_gb = volume['Size']
            state = volume['State']
            create_time = volume['CreateTime']
            iops = volume.get('Iops', 0)
            throughput = volume.get('Throughput', 0)
            
            # Check if volume is attached
            is_attached = len(volume['Attachments']) > 0
            attached_to = None
            
            if is_attached:
                attached_to = volume['Attachments'][0]['InstanceId']
            
            # Get volume name from tags
            volume_name = 'N/A'
            if 'Tags' in volume:
                for tag in volume['Tags']:
                    if tag['Key'] == 'Name':
                        volume_name = tag['Value']
                        break
            
            print(f"Analyzing EBS volume: {volume_id} ({volume_name})")
            
            # Get basic useful metrics (only for attached volumes)
            read_ops = 0
            write_ops = 0
            read_bytes = 0
            write_bytes = 0
            
            if is_attached:
                read_ops = get_volume_ops(cloudwatch, volume_id, 'VolumeReadOps')
                write_ops = get_volume_ops(cloudwatch, volume_id, 'VolumeWriteOps')
                read_bytes = get_volume_bytes(cloudwatch, volume_id, 'VolumeReadBytes')
                write_bytes = get_volume_bytes(cloudwatch, volume_id, 'VolumeWriteBytes')
            
            # Calculate volume age
            age_days = (datetime.now(create_time.tzinfo) - create_time).days
            
            # Record the volume with metrics
            finding = {
                "id":volume_id,
                'resource_id': volume_id,
                'resource_type': 'EBS',
                'issue': 'ebs_volume',
                'severity': 'info',
                'details': f'EBS Volume: {volume_name} ({state})',
                'recommendation': f'Attached: {is_attached}, Size: {size_gb}GB',
                'metadata': {
                    'volume_name': volume_name,
                    'volume_type': volume_type,
                    'size_gb': size_gb,
                    'state': state,
                    'is_attached': is_attached,
                    'attached_to': attached_to,
                    'age_days': age_days,
                    'iops': iops,
                    'throughput_mbps': throughput,
                    'read_ops_7d': int(read_ops),
                    'write_ops_7d': int(write_ops),
                    'read_gb_7d': Decimal(str(round(read_bytes / (1024**3), 2))),
                    'write_gb_7d': Decimal(str(round(write_bytes / (1024**3), 2))),
                    'create_time': create_time.isoformat()
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
                'message': f'Analyzed {len(findings)} EBS volumes',
                'findings': findings
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error analyzing EBS volumes: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def get_volume_ops(cloudwatch, volume_id, metric_name, days=7):
    """Get total volume operations (read or write) over the last 7 days."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName=metric_name,
            Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Sum']
        )
        
        if response['Datapoints']:
            total_ops = sum(d['Sum'] for d in response['Datapoints'])
            return total_ops
        
        return 0.0
    except Exception as e:
        print(f"Error getting volume ops for {volume_id}: {str(e)}")
        return 0.0


def get_volume_bytes(cloudwatch, volume_id, metric_name, days=7):
    """Get total volume data transfer (read or write) in bytes."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName=metric_name,
            Dimensions=[{'Name': 'VolumeId', 'Value': volume_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Sum']
        )
        
        if response['Datapoints']:
            total_bytes = sum(d['Sum'] for d in response['Datapoints'])
            return total_bytes
        
        return 0.0
    except Exception as e:
        print(f"Error getting volume bytes for {volume_id}: {str(e)}")
        return 0.0
    
if __name__ == "__main__":
    print(lambda_handler({}, {}))