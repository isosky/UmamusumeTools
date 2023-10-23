
import os.path
import json
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)

UMA_NAME_SCORE: dict = {}
UMA_FILE_LIST: dict = {}
UMA_DATA_INFO: dict = {}
UMAMUSUME_RACE_TEMPLATE_PATH = "userdata/" + CONFIG.role_name


def load_uma_list():
    log.info("开始加载马娘数据")
    files = os.listdir(UMAMUSUME_RACE_TEMPLATE_PATH)
    for file in files:
        if 'unknown' in file:
            os.remove(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file))
            log.info(f"{file} 中存在未识别的马娘，先移除")
            continue
        if 'json' in file:
            with open(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file), 'r', encoding='utf-8') as f:
                temp = json.load(f)
            for v in temp['relation'].values():
                if 'unknown' in v['uma_name'] or 'unknown' in v['bb']['uma_name'] or 'unknown' in v['mm']['uma_name']:
                    os.remove(os.path.join(UMAMUSUME_RACE_TEMPLATE_PATH, file))
                    log.info(f"{file} 中存在未识别的马娘，先移除")
                    continue
                UMA_DATA_INFO[v['md5']] = v
            fn = '_'.join(file.split("_")[:2])
            if fn not in UMA_NAME_SCORE:
                UMA_NAME_SCORE[fn] = []
            UMA_NAME_SCORE[fn].append(file.split('.')[0])
            UMA_FILE_LIST[file.split('.')[0]] = ''
    log.info(f"马娘父辈总数为：{len(UMA_DATA_INFO.values())}")
    log.info("结束加载马娘数据")


load_uma_list()
