###########
# IMPORTS
###########
import json
from datetime import datetime
import argparse
import boto3
import sys
import time

ssm = boto3.client('ssm', region_name='us-east-1')

def testLulu(instanceId):
    """ What does it do?

    :param ?: ?
    :returns: ?
    """

    command = "sudo touch lulu.txt"
    print("==== Starting All Services ====")
    ssm_response_start = sendSSM(instanceId, command, 'Testing WMS application')
    if (not ssm_response_start):
        print("==== Fail to test WMS application on instance %s ====" % (instanceId))
        sys.exit(1)

def sendMessage(subject, message):
    """ Send a message to SNS topic

    :param subject: The topic subject
    :param message: The topic message
    :returns: none
    """

    print('==== Publishing a message on SNS ====')
    try:
        self.sns.publish(
            TopicArn=self.topicarn,
            Message=str(message),
            Subject=subject
        )
    except Exception as e:
        raise Exception('==== An exception occurred: %s ====' % e)        
    
def sendSSM(instanceId, command, stage):
    """ What does it do?

    :param ?: ?
    :returns: ?
    """

    print("==== Running SSM Commands ====")
    try:
        response = ssm.send_command(
            InstanceIds=[instanceId],
            DocumentName="AWS-RunShellScript",
            Comment="sdn Patch",
            Parameters={
                'commands': [command]
            },
            CloudWatchOutputConfig={
                'CloudWatchLogGroupName': 'SSM',
                'CloudWatchOutputEnabled': True
            }
        )
        time.sleep(5)
        status = True
        return_status = True
        while (status):
            response1 = ssm.list_command_invocations(CommandId=response['Command']['CommandId'])
            s = response1['CommandInvocations'][0]['Status']
            print("==== SSM Command Status: %s ====" % s)
            if ((s != 'Success') and (s != 'Failed') and (s != 'Cancelled') and (s != 'TimedOut')):
                status = True
            elif ((s == 'Failed') or (s == 'Cancelled') or (s == 'TimedOut')):
                print("==== %s stage on instance with id %s failed, hence exiting the system ====" % (stage, instanceId))
                return_status = False
                subject = "%s stage on instance with id %s failed" % (stage, instanceId)
                message = """
{a:<20} : {r_time}
{b:<20} : {r_instance}
{c:<20} : {r_status}
{d:<20} : {r_detail}
""".format(a='Time', b='Instance Id', c='Status', d='Status Detail', r_time=response1['CommandInvocations'][0]['RequestedDateTime'], r_instance=instanceId, r_status=s, r_detail='For more information, please see CloudWatch Log Group SSM')
                sendMessage(subject, message)
                break
            elif (s == 'Success'):
                status = False
            time.sleep(2)
        return return_status
    except Exception as e:
        raise Exception('An exception occurred: %s' % e)
        
        
testLulu("i-00d5893b93af036cd")
