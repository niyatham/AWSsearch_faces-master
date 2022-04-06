from pathlib import Path  # for platform-specific path separators
from pprint import pprint
from glob import glob
import graphical_utils as gu
import image_loaders as img_ld
import boto3
from typing import List
from pathlib import Path
from pprint import pprint
# note for my Cloud Computing students,
# image_loaders.py is the new name for image_helpers.py
from image_loaders import get_image

# Note: the face_collections module is in
#       the file face_collections.py included
#       in this project.
# Note: using as below simply means we can
#       reference anything from face_collections
#       by just saying fcol., so for example,
#       to use the create_collection function, we
#       would write fcol.create_collection
#import face_collections as fcol

# since we will be referring to it
# frequently, create a global variable
# to store the name of the collection we are usingg
# Note: Python does NOT have constants
#       but we are using the programming convention
#       of all uppercase name to denote a constant
COLLECT_NAME: str = 'testing'

# variables for the different images directories
REF_FACE_DIR = 'reference_faces'  # contains images to be added to the collection
FACE_SEARCH_DIR = 'faces_to_match'  # contains images that will be used to find a match in the collection

def list_collections() -> List[str]:
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


def list_faces(coll_name: str) -> List[dict]:
    """
    Return a list of faces in the specified collection.
    :param coll_name: the collection.
    :return: a list of faces in the specified collection.
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/list-faces-in-collection-procedure.html
    # last access 3/5/2019

    client = boto3.client('rekognition')
    response = client.list_faces(CollectionId=coll_name)
    tokens = True
    result = []

    while tokens:

        faces = response['Faces']
        result.extend(faces)

        if 'NextToken' in response:
            next_token = response['NextToken']
            response = client.list_faces(CollectionId=coll_name,
                                         NextToken=next_token)
        else:
            tokens = False

    return result

def add_face(coll_name: str, image: str):
    """
    Adds the specified face image to the specified collection.
    :param coll_name: the collection to add the face to
    :param image: the face image (either filename or URL)
    """

    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/add-faces-to-collection-procedure.html
    # last access 3/5/2019

    # nested function
    def extract_filename(fname_or_url: str) -> str:
        """
        Returns the last component of file path or URL.
        :param fname_or_url: the filename or url.
        :return: the last component of file path or URL.
        """
        import re
        return re.split('[\\\/]', fname_or_url)[-1]

    # rest of the body of add_face
    client = boto3.client('rekognition')
    rekresp = client.index_faces(CollectionId=coll_name,
                                 Image={'Bytes': get_image(image)},
                                 ExternalImageId=extract_filename(image))

    if rekresp['FaceRecords'] == []:
        raise Exception('No face found in the image')


def find_face(coll_name: str, face_to_find: str) -> List[dict]:
    """
    Searches for the specified face in the collection.
    :param face_to_find: a string that is either the filename or URL to the image containing the face to search for.
    :return: a list of face info dictionaries
    """
    # lightly edited version of
    # https://docs.aws.amazon.com/rekognition/latest/dg/search-face-with-image-procedure.html
    # last access 3/5/2019
    client = boto3.client('rekognition')

    rekresp = client.search_faces_by_image(CollectionId=coll_name,
                                           Image={'Bytes': get_image(face_to_find)},
                                           MaxFaces=1
                                          )

    return rekresp['FaceMatches']




def collection_exists(coll_name: str) -> bool:
    """
    Checks to see if the collection exists
    :param coll_name: the name of the collection to check
    :return: true iff the collection already exists
    """
    return coll_name in list_collections()

# check if the collection exists
# Note: strictly not necessary, since
#       create_collection will only create
#       the collection if it does not already
#       exist
print('Does ' + COLLECT_NAME + ' collection exist? ',
      'Yes' if collection_exists(COLLECT_NAME) else 'No')

# collection needs to exist first
print('Creating collection' + COLLECT_NAME)
create_collection(COLLECT_NAME)

# faces need to be added to the collection
print('Faces currently in the collection:')
pprint(list_faces(COLLECT_NAME))
print()

# checking to see if we need to add the faces,
# to the collection
if len(list_faces(COLLECT_NAME)) < 3:

    # We want to add a platform-specific
    # file separator for the filenames
    # so on Windows the file separator is \
    # whereas on Linux and Mac the file separator is /
    # here is the latest Pythonic way to do this

    # 1) create a path for the reference faces directory
    ref_images_dir = Path(REF_FACE_DIR)

    # create a list of filenames with the path
    # 2) notice the use of /
    # face_fnames = [str(ref_images_dir / fname)
    #                for fname in
    #                ['gaspar.jpg', 'small.jpg', 'ventura.jpg']]

    # alternatively, use glob to grab all JPEGs in the folder
    face_fnames = glob(REF_FACE_DIR + '/*.jpg')
    print('Here is the list of filenames: ', end='')
    pprint(face_fnames)
    for fname in face_fnames:
        add_face(COLLECT_NAME, fname)

    # print the face info in the collection
    print('Faces added to ' + COLLECT_NAME + ':')
    pprint(list_faces(COLLECT_NAME))

# # show the reference faces
# print('Showing reference faces')
# for face_info in fcol.list_faces(COLLECT_NAME):
#     # pprint(face)
#     img_fname = str(Path(REF_FACE_DIR) / face_info['ExternalImageId'])
#     img = gu.create_pillow_img(img_ld.get_image(img_fname))
#     gu.draw_box(img, face_info['BoundingBox']).show()

# now we can search faces
# create a variable to store the filename of the image
img_fname = str(Path(FACE_SEARCH_DIR) /'test.jpg')

print('Searching collection for', img_fname)

# gu.create_pillow_img(img_fname).show()
# try to find the face in the collection
faces_info = find_face(COLLECT_NAME,
                            img_fname)

print('Found', len(faces_info),
      'match' + ('' if len(faces_info) == 1 else 's'))
# Extract the name of the reference image(s) that were matched
pprint([face_info['Face']['ExternalImageId'] for face_info in faces_info])
print()
print(type([face_info['Face']['ExternalImageId'] for face_info in faces_info]))

a = [face_info['Face']['ExternalImageId'] for face_info in faces_info]

def check(ds):
    return "".join(ds)

b = check(a)

print(b)
c = b.split('.')[0]

print(c)