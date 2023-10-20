
import os.path
import json
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)

UMA_LIST: dict = {}
UMAMUSUME_RACE_TEMPLATE_PATH = "userdata/" + CONFIG.role_name


def load_uma_data():
    files = os.listdir(UMAMUSUME_RACE_TEMPLATE_PATH)
    for file in files:
        if 'unknown' in file:
            os.remove(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file))
            log.info(f"{file} 中存在未识别的马娘，先移除")
            continue
        if 'json' in file:
            with open(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file), 'r', encoding='utf-8') as f:
                temp = json.load(f)
            temp_parent = [x['uma_name'] for x in temp['relation'].values()]
            if 'unknown' in temp_parent:
                os.remove(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file))
                log.info(f"{file} 中存在未识别的马娘，先移除")
                continue
            UMA_LIST[file.split(".")[0]] = ""


load_uma_data()
