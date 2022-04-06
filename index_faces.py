#Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
from pathlib import Path
from pprint import pprint
from botocore.exceptions import ClientError

# note for my Cloud Computing students,
# image_loaders.py is the new name for image_helpers.py
#from image_loaders import get_image
from typing import List

def add_faces_to_collection(bucket,photo,collection_id):


    
    client=boto3.client('rekognition')

    response=client.index_faces(CollectionId=collection_id,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])
    print(response)
    print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         print('  Face ID: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])

def main(a=None,bucket = 'rekognition-yash',collection_id='faces_mathco_test6'):
    """
    Function adds images to the specified collection

    Parameters
    ----------
    a : List
    List of the images from S3 bucket
    bucket : str
    Specify the bucket name
    collection_id: str
    Specify the collection ID to which you want to add images
    
    Usage
    -----
    main(a=['image1.jpg',image2.jpg],bucket ='test_bucket',collection_id='faces')


    """
    bucket=bucket
    collection_id=collection_id
    photo=a
    
    for i in photo:
        print(i)
        indexed_faces_count=add_faces_to_collection(bucket, i, collection_id)
        print("Faces indexed count: " + str(indexed_faces_count))




def describe_collection(collection_id):

    print('Attempting to describe collection ' + collection_id)
    client=boto3.client('rekognition')

    try:
        response=client.describe_collection(CollectionId=collection_id)
        print("Collection Arn: "  + response['CollectionARN'])
        print("Face Count: "  + str(response['FaceCount']))
        print("Face Model Version: "  + response['FaceModelVersion'])
        print("Timestamp: "  + str(response['CreationTimestamp']))

        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The collection ' + collection_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
    print('Done...')

def collection_exists(coll_name: str) -> bool:
    """
    Checks to see if the collection exists
    :param coll_name: the name of the collection to check
    :return: true iff the collection already exists
    """
    return coll_name in list_collections()



def create_collection(coll_name: str):
    """
    Creates a collection with the specified name, if it does not already exist
    :param coll_name: the name of the collection to create
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/create-collection-procedure.html,
    # last access 3/5/2019

    client = boto3.client('rekognition')
    if not collection_exists(coll_name):
        response = client.create_collection(CollectionId=coll_name)
        print('Collection ARN: ' + response['CollectionArn'])
        print('Status code: ' + str(response['StatusCode']))
        print('Done...')
        if response['StatusCode'] != 200:
            raise 'Could not create collection, ' + coll_name \
                  + ', status code: ' + str(response['StatusCode'])


def list_collections():
    """
    Returns a list of the names of the existing collections
    :return: a list of the names of the existing collections
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/list-collection-procedure.html,
    # last access 3/5/2019

    client = boto3.client('rekognition',region_name='ap-south-1')
    response = client.list_collections()
    result = []
    while True:
        collections = response['CollectionIds']
        result.extend(collections)

        # if more results than maxresults
        if 'NextToken' in response:
            next_token = response['NextToken']
            response = client.list_collections(NextToken=next_token)
            pprint(response)
        else:
            break
    return result

def delete_collection(coll_name: str):
    """
    Attempts to delete the specified collection.
    Raises an error if the collection does not exist.
    :param coll_name: the name of the collection
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/delete-collection-procedure.html,
    # last access 3/5/2019

    from botocore.exceptions import ClientError

    client = boto3.client('rekognition')
    try:
        client.delete_collection(CollectionId=coll_name)
    except ClientError as e:
        raise e.response['Error']['Code']


# if __name__ == "__main__":
#     main()