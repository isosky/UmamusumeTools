
import os.path
import json
import time
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)

UMA_DATA_DICT_LIST: dict[str, list] = {}
UMAMUSUME_RACE_TEMPLATE_PATH = "userdata/" + CONFIG.role_name
UMAMUSUME_RACE_TEMPLATE_PATH_REMOVE = "userdata/" + CONFIG.role_name + '_remove'

BLUR_FACTOR: dict = {'速度': "", '耐力': "", '力量': "", '毅力': "", '智力': ""}
RED_FACTOR: dict = {'草地': "", '泥地': "", '短距离': "", '英里': "", '中距离': "", '长距离': "", '领跑': "", '跟前': "", '居中': "", '后追': ""}
GREEN_FACTOR: dict = {}

# TODO 上下位因子合并，因子识别规范

UMA_DATA_DICT_LIST['uma_uuid'] = []
UMA_DATA_DICT_LIST['uma_score'] = []
UMA_DATA_DICT_LIST['status'] = []
UMA_DATA_DICT_LIST['blue_factor'] = []
UMA_DATA_DICT_LIST['red_factor'] = []
UMA_DATA_DICT_LIST['all_blue_factor'] = []
UMA_DATA_DICT_LIST['all_red_factor'] = []
UMA_DATA_DICT_LIST['white_factor'] = []
UMA_DATA_DICT_LIST['all_white_factor'] = []


def load_uma_data(filepath=UMAMUSUME_RACE_TEMPLATE_PATH):
    start_time = time.time()
    files = os.listdir(filepath)
    if '_remove' in filepath:
        status = 'remove'
    else:
        status = 'keep'

    for file in files:
        if 'unknown' in file:
            os.remove(os.path.join(filepath, file))
            log.info(f"{file} 中存在未识别的马娘，先移除")
            continue
        if 'json' in file:
            with open(os.path.join(filepath, file), 'r', encoding='utf-8') as f:
                temp = json.load(f)
            if 'unknown' in temp['base_info']['uma_name'] or 'unknown' in temp['relation']['bb']['uma_name'] or 'unknown' in temp['relation']['mm']['uma_name']:
                os.remove(os.path.join(filepath, file))
                log.info(f"{file} 中存在未识别的马娘，先移除")
                continue
            uma_uuid = file.split(".")[0]
            uma_factor = temp['factor']
            uma_score = temp['base_info']['score']
            uma_father_factor = temp["relation"]['bb']['factor']
            uma_mother_factor = temp["relation"]['mm']['factor']
            temp_factor_list = [uma_factor, uma_father_factor, uma_mother_factor]

            for k in uma_factor:
                if k in BLUR_FACTOR:
                    uma_blue_factor = k+str(uma_factor[k])
                if k in RED_FACTOR:
                    uma_red_factor = k+str(uma_factor[k])

            blue_factor = {x: 0 for x in BLUR_FACTOR}
            blue_factor_result = ''
            blue_factor_count = 0
            blue_factor_count_match = 0
            for k in BLUR_FACTOR:
                temp = 0
                for fl in temp_factor_list:
                    if k in fl:
                        temp += fl[k]
                        blue_factor[k] += fl[k]
                if temp != 0:
                    blue_factor_result = blue_factor_result + str(temp)+k
                if k not in ['毅力', '智力']:
                    blue_factor_count += temp
                blue_factor_count_match += temp
            # log.debug(f"{uma_uuid} {uma_name} blue factor:{blue_factor_result}")
            blue_factor = {k: v for k, v in blue_factor.items() if v != 0}

            red_factor = {x: 0 for x in RED_FACTOR}
            red_factor_result = ''
            for k in RED_FACTOR:
                temp = 0
                for fl in temp_factor_list:
                    if k in fl:
                        temp += fl[k]
                        red_factor[k] += fl[k]
                if temp != 0:
                    red_factor_result = red_factor_result + str(temp)+k
            # log.debug(f"{uma_uuid} {uma_name} red factor:{red_factor_result}")
            red_factor = {k: v for k, v in red_factor.items() if v != 0}

            factor_list = {}
            temp_factor = set(uma_factor.keys()) | set(uma_father_factor.keys()) | set(uma_mother_factor.keys())
            for k in temp_factor:
                if k in BLUR_FACTOR or k in RED_FACTOR:
                    continue
                _temp = []
                for fl in temp_factor_list:
                    if k in fl:
                        _temp.append(fl[k])
                    else:
                        _temp.append(0)
                factor_list[k] = sum(_temp)

            temp_str = ','.join([k+str(v) for k, v in factor_list.items()])
            UMA_DATA_DICT_LIST['uma_uuid'].append(uma_uuid)
            UMA_DATA_DICT_LIST['all_blue_factor'].append(blue_factor_result)
            UMA_DATA_DICT_LIST['uma_score'].append(uma_score)
            UMA_DATA_DICT_LIST['all_red_factor'].append(red_factor_result)
            UMA_DATA_DICT_LIST['all_white_factor'].append(temp_str)
            UMA_DATA_DICT_LIST['blue_factor'].append(uma_blue_factor)
            UMA_DATA_DICT_LIST['red_factor'].append(uma_red_factor)
            UMA_DATA_DICT_LIST['white_factor'].append(uma_factor)
            UMA_DATA_DICT_LIST['status'].append(status)

    log.info(f"加载马娘数据耗时:{time.time()-start_time}")


load_uma_data()
load_uma_data(UMAMUSUME_RACE_TEMPLATE_PATH_REMOVE)
