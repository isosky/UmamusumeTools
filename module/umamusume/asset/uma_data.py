
import os.path
import json
import bot.base.log as logger
from config import CONFIG
from bot.base.resource import Template
from module.cal_compatibility.asset.matrix_load import UMA_TRANSLATE

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
                    # if 'caoshangfei' in v['uma_name'] or 'caoshangfei' in v['bb']['uma_name'] or 'caoshangfei' in v['mm']['uma_name']:
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


UMA_ROLE_LIST: list[Template] = []
UMAMUSUME_UMA_ROLE_TEMPLATE_PATH = "resource/umamusume/uma_role"
_UMAMUSUME_UMA_ROLE_TEMPLATE_PATH = "/umamusume/uma_role"


def load_uma_head():
    # role
    image_files = [f for f in os.listdir(UMAMUSUME_UMA_ROLE_TEMPLATE_PATH) if os.path.isfile(os.path.join(UMAMUSUME_UMA_ROLE_TEMPLATE_PATH, f))]
    for i in image_files:
        temp_name = i[:-4]
        if temp_name.split('_')[0] not in UMA_TRANSLATE.values():
            log.warning(f"{temp_name} 不在相性名称表里面，请检查")
        temp_name = Template(temp_name, _UMAMUSUME_UMA_ROLE_TEMPLATE_PATH)
        UMA_ROLE_LIST.append(temp_name)


load_uma_list()
load_uma_head()
