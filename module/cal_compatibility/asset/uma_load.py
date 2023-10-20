
import os.path
import json
import time
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)

UMA_LIST: dict[str, dict] = {}
UMAMUSUME_RACE_TEMPLATE_PATH = "userdata/" + CONFIG.role_name

BLUR_FACTOR: dict = {'速度': "", '耐力': "", '力量': "", '毅力': "", '智力': ""}
RED_FACTOR: dict = {'草地': "", '泥地': "", '短距离': "", '英里': "", '中距离': "", '长距离': "", '领跑': "", '跟前': "", '居中': "", '后追': ""}
GREEN_FACTOR: dict = {}

# TODO 上下位因子合并，因子识别规范


def load_uma_data():
    start_time = time.time()
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
            uma_uuid = file.split(".")[0]
            uma_name = temp["base_info"]['role_name']
            uma_factor = temp['factor']
            uma_father_name = temp["relation"]['bb']['uma_name']
            uma_father_factor = temp["relation"]['bb']['factor']
            uma_mother_name = temp["relation"]['mm']['uma_name']
            uma_mother_factor = temp["relation"]['mm']['factor']
            temp_factor_list = [uma_factor, uma_father_factor, uma_mother_factor]

            blue_factor_result = ''
            blue_factor_count = 0
            blue_factor_count_match = 0
            for k in BLUR_FACTOR:
                temp = 0
                for fl in temp_factor_list:
                    if k in fl:
                        temp += fl[k]
                if temp != 0:
                    blue_factor_result = blue_factor_result + str(temp)+k
                if k not in ['毅力', '智力']:
                    blue_factor_count += temp
                blue_factor_count_match += temp
            # log.debug(f"{uma_uuid} {uma_name} blue factor:{blue_factor_result}")

            red_factor_result = ''
            for k in RED_FACTOR:
                temp = 0
                for fl in temp_factor_list:
                    if k in fl:
                        temp += fl[k]
                if temp != 0:
                    red_factor_result = red_factor_result + str(temp)+k
            # log.debug(f"{uma_uuid} {uma_name} red factor:{red_factor_result}")
            factor_list = {}
            temp_factor = set(uma_factor.keys()) | set(uma_father_factor.keys()) | set(uma_mother_factor.keys())
            for k in temp_factor:
                _temp = []
                for fl in temp_factor_list:
                    if k in fl:
                        _temp.append(fl[k])
                    else:
                        _temp.append(0)
                factor_list[k] = _temp

            UMA_LIST[uma_uuid] = {'uma_uuid': uma_uuid, 'uma_name': uma_name, 'uma_factor': uma_factor, 'uma_father_name': uma_father_name, 'uma_father_factor': uma_father_factor, 'uma_mother_name': uma_mother_name, 'uma_mother_factor': uma_mother_factor,
                                  'cap_sum': 0, "score": 0, "blue_factor_result": blue_factor_result, "red_factor_result": red_factor_result, "factor_list": factor_list,
                                  "blue_factor_count": blue_factor_count, "blue_factor_count_match": blue_factor_count_match}
            # log.debug(UMA_LIST[uma_uuid])

    log.info(f"加载马娘数据耗时:{time.time()-start_time}")


load_uma_data()
