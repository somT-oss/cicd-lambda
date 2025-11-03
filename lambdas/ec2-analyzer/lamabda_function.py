import boto3
import json
from datetime import datetime, timedelta
from decimal import Decimal


def lambda_handler(event, context):
    """
    Analyze EC2 instances - check running instances with basic useful metrics.
    """
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CostOptimizerFindings')
    
    findings = []
    
    try:
        # Get all EC2 instances
        response = ec2.describe_instances()
       
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                state = instance['State']['Name']
                launch_time = instance['LaunchTime']
                
                # Get instance name from tags
                instance_name = 'N/A'
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                
                # FILTER: Only check running instances
                if state != 'running':
                    print(f"Skipping {instance_id} - not running (status: {state})")
                    continue
                
                print(f"Analyzing EC2 instance: {instance_id} ({instance_name})")
                
                # Get basic useful metrics
                cpu_utilization = get_cpu_utilization(cloudwatch, instance_id)
                network_in = get_network_traffic(cloudwatch, instance_id, 'NetworkIn')
                network_out = get_network_traffic(cloudwatch, instance_id, 'NetworkOut')
                
                # Calculate instance age
                age_days = (datetime.now(launch_time.tzinfo) - launch_time).days
                
                # Record the instance with metrics
                finding = {
                    "id": instance_id,
                    'resource_id': instance_id,
                    'resource_type': 'EC2',
                    'issue': 'running_instance',
                    'severity': 'info',
                    'details': f'Running EC2 instance: {instance_name}',
                    'recommendation': f'CPU Avg: {cpu_utilization:.1f}%',
                    'metadata': {
                        'instance_name': instance_name,
                        'instance_type': instance_type,
                        'state': state,
                        'age_days': age_days,
                        'cpu_avg_percent': Decimal(str(round(cpu_utilization, 2))),
                        'network_in_mb': Decimal(str(round(network_in / (1024 * 1024), 2))),
                        'network_out_mb': Decimal(str( round(network_out / (1024 * 1024), 2))),
                        'launch_time': launch_time.isoformat()
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
                'message': f'Analyzed {len(findings)} running EC2 instances',
                'findings': findings
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error analyzing EC2 instances: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


def get_cpu_utilization(cloudwatch, instance_id, days=7):
    """Get average CPU utilization over the last 7 days."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,  # 1 day
            Statistics=['Average']
        )
        
        if response['Datapoints']:
            avg_cpu = sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints'])
            return avg_cpu
        
        return 0.0
    except Exception as e:
        print(f"Error getting CPU metrics for {instance_id}: {str(e)}")
        return 0.0


def get_network_traffic(cloudwatch, instance_id, metric_name, days=7):
    """Get total network traffic (NetworkIn or NetworkOut) in bytes."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
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
        print(f"Error getting network metrics for {instance_id}: {str(e)}")
        return 0.0


if __name__ == "__main__":
    print(lambda_handler({}, {}))