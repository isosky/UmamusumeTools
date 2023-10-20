from module.cal_compatibility.cal import get_recommand_uma_list
# from module.cal_compatibility.asset.uma_load import UMA_LIST
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)


target = {'uma_name': 'shenying', 'factor_list': ['中距离', '逆时针', 'URA剧本', '春季优俊少女', '天王奖（春）']}

temp = get_recommand_uma_list(target, '', False, True)
if temp:
    for i in temp:
        log.info(f"{i['father']['uma_uuid']}, {i['mother']['uma_uuid']},{ i['couple_count']}, {i['couple_sum_count']}, {i['couple_cap_score']}")
        log.info(f"{i['father']['blue_factor_result']} , {i['father']['red_factor_result']}")
        log.info(f"{i['mother']['blue_factor_result']} , {i['mother']['red_factor_result']}")
        log.info(f"{i['couple_factor_match']}")
