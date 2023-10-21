import os
from config import CONFIG

base_path = "userdata"


def folder_check():
    if not os.path.exists('userdata/'+CONFIG.role_name):
        os.makedirs('userdata/'+CONFIG.role_name)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    if not os.path.exists('resource/unknown_factor'):
        os.makedirs('resource/unknown_factor')
    if not os.path.exists('resource/unknown_uma'):
        os.makedirs('resource/unknown_uma')


folder_check()
