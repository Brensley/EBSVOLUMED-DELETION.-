import boto3
from pprint import pprint
import os
import datetime

#************ You can change Asge of EBS Volume here *******************#
age = 0

def days_old(date):
   date_obj = date.replace(tzinfo=None)
   diff = datetime.datetime.now() - date_obj
   return diff.days

def lambda_handler(event, handler):

    # create boto3 client for ec2
    client = boto3.client('ec2',region_name="us-east-1")

    # create a list where the volume ids of unused volumes will be stored
    volumes_to_delete = list()

    # call describe_volumes() method of client to get the details of all ebs volumes in given region
    # if you have large number of volumes then get the volume detail in batch by using nextToken and process accordingly
    volume_detail = client.describe_volumes()

    # process each volume in volume_detail
    if volume_detail['ResponseMetadata']['HTTPStatusCode'] == 200:
        for each_volume in volume_detail['Volumes']:
            DND = "Flase"
            if 'Tags' in each_volume:
                for tag in each_volume['Tags']:
                    #*********** You can change Tag and Value here *******************# Note: Give Tag Value in lowercase
                    if tag['Key'].lower() == 'dnd' and tag['Value'].lower() == 'true':
                        DND = "True"
            print(each_volume)
            # some logging to make things clear about the volumes in your existing system
            print("Working for volume with volume_id: ", each_volume['VolumeId'])
            print("State of volume: ", each_volume['State'])
            print("Attachment state length: ", len(each_volume['Attachments']))
            print(each_volume['Attachments'])
            print("--------------------------------------------")
            # figuring out the unused volumes
            # the volumes which do not have 'Attachments' key and their state is 'available' is considered to be unused
            print("Printing DND here Outside" + DND)
            if len(each_volume['Attachments']) == 0 and each_volume['State'] == 'available' and DND != "True":
                print("Printing DND here" + DND)
                vol_day_old = days_old(each_volume['CreateTime'])
                print(vol_day_old)
                if vol_day_old >= age:
                    volumes_to_delete.append(each_volume['VolumeId'])

    # these are the candidates to be deleted by maintaining waiters for them
    pprint(volumes_to_delete)

    # proceed for deletion
    for each_volume_id in volumes_to_delete:
        try:
            print("Deleting Volume with volume_id: " + each_volume_id)
            response = client.delete_volume(
                VolumeId=each_volume_id
            )
        except Exception as e:
            print("Issue in deleting volume with id: " + each_volume_id + "and error is: " + str(e))

    # waiters to verify deletion and keep alive deletion process until completed
    waiter = client.get_waiter('volume_deleted')
    try:
        waiter.wait(
            VolumeIds=volumes_to_delete,
        )
        print(volumes_to_delete)
        print("Successfully deleted all volumes")
    except Exception as e:
        print("Error in process with error being: " + str(e))

if __name__ == '__main__':
   lambda_handler('event', 'handler')
