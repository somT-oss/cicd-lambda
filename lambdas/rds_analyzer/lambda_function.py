import boto3
import json
from datetime import datetime
from decimal import Decimal

def lambda_handler(event, context):
    """
    Analyze RDS instances and report on running instances with storage > 10GB.
    """
    rds = boto3.client('rds')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('CostOptimizerFindings')
    
    findings = []
    
    try:
        # Get all RDS instances
        response = rds.describe_db_instances()
        
        for db_instance in response['DBInstances']:
            db_identifier = db_instance['DBInstanceIdentifier']
            db_instance_class = db_instance['DBInstanceClass']
            engine = db_instance['Engine']
            status = db_instance['DBInstanceStatus']
            multi_az = db_instance['MultiAZ']
            storage_type = db_instance['StorageType']
            allocated_storage = db_instance['AllocatedStorage']
            
            # FILTER 1: Only check running instances (status = 'available')
            if status != 'available':
                print(f"Skipping {db_identifier} - not running (status: {status})")
                continue
            
            # FILTER 2: Only check instances with storage > 10GB
            if allocated_storage <= 10:
                print(f"Skipping {db_identifier} - storage too small ({allocated_storage}GB)")
                continue
            
            print(f"Found qualifying RDS instance: {db_identifier}")
            
            # Record the instance details
            finding = {
                'id': db_identifier,
                'resource_id': db_identifier,
                'resource_type': 'RDS',
                'issue': 'running_instance_over_10gb',
                'severity': 'info',
                'details': f'Running RDS instance with {allocated_storage}GB storage',
                'recommendation': 'Instance meets criteria: Running and >10GB storage',
                'metadata': {
                    'instance_class': db_instance_class,
                    'engine': engine,
                    'storage_gb': allocated_storage,
                    'storage_type': storage_type,
                    'multi_az': multi_az,
                    'status': status
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
                'message': f'Found {len(findings)} running RDS instances with storage > 10GB',
                'findings': findings
            }, default=str)
        }
        
    except Exception as e:
        print(f"Error analyzing RDS instances: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }