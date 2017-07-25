#!/usr/bin/env python3

import os

def ensure_file_exists_in_path(file_name):

    for folder_path in os.environ["PATH"].split(os.pathsep):
        folder_path = folder_path.strip('"')
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            return

    raise Exception("%(file_name)s not found in ${PATH}" % { 'file_name': file_name })
