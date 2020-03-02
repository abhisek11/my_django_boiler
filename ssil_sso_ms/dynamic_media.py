import os
from PIL import Image

def get_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    file_extension = os.path.splitext(filename)
    if file_extension[1] in ['.jpg','.png','.jpeg']:
        dir = 'Images'
    elif file_extension[1] in ['.csv','.pdf','.doc','.docx','.xlsx','.xls'] :
        dir = 'Documents'
    elif file_extension[1] in ['.mp4'] :
        dir = 'Videos'
    else:
        dir="others"
    app_name = instance._meta.app_label
    model_name = instance._meta.object_name
    path = '{0}/{1}/{2}/{3}'.format(app_name,model_name,dir, filename)

    # print('app_name: ', instance._meta.app_label)
    # print('xgshcxg: ', instance._meta.object_name)

    return path