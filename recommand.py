from module.cal_compatibility.cal_cap import get_recommand_uma_list
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)


target = {'uma_name': 'dashukuaiche', 'factor_list': ['中距离', '逆时针', 'URA剧本', '春季优俊少女', '天王奖（春）']}
uma_borrow = 'wanshansiji'

temp = get_recommand_uma_list(target=target, borrow=uma_borrow, is_father=False, mua_min_factor=2, mua_min_blue=7, is_bigmatch=True, result_length=10)
if uma_borrow == '':
    if temp:
        s = 1
        for i in temp:
            log.info("*"*10)
            log.info(f" 开始输出第 {s} 个方案")
            log.info(f"{i['father']['uma_uuid']}, {i['mother']['uma_uuid']}, 总相性： {i['couple_cap_score']}")
            log.info(f" 总共指定 {len(target['factor_list'])} 个白因子，父母6个马娘总共可命中 {len(target['factor_list'])*6} 次， 当前命中 {i['couple_match_sum']} 次")
            log.info(f" 总计：{ sum(i['blue_factor_all'].values())} 蓝,详情：{','.join(f'{k}: {v}' for k, v in i['blue_factor_all'].items())}")
            log.info(f" 父因子详情{i['father']['uma_factor']}")
            log.info(f" 母因子详情{i['mother']['uma_factor']}")
            log.info(f" 总计：{ sum(i['red_factor_all'].values())} 红,详情：{','.join(f'{k}: {v}' for k, v in i['red_factor_all'].items())}")
            log.info(f" 指定各因子命中详情[父，爷，奶，母，公，婆]：{i['all_factor_match']}")
            log.info(f" 指定各因子命中详情[父，母]：{i['couple_factor_match']}")
            s += 1
    else:
        log.warning("一个组合也没有，放宽条件或者刷种马去吧")
else:
    if temp:
        s = 1
        log.info("借用马娘计算完毕")
        for i in temp:
            log.info("*"*10)
            log.info(f" 开始输出第 {s} 个方案")
            log.info(f"{i['father']['uma_uuid']}, {uma_borrow}, 总相性： {i['couple_cap_score']}")
            log.info(f" 总共指定 {len(target['factor_list'])} 个白因子，父母3个马娘总共可命中 {len(target['factor_list'])*3} 次， 当前命中 {i['couple_match_sum']} 次")
            log.info(f" 总计：{ sum(i['blue_factor_all'].values())} 蓝,详情：{','.join(f'{k}: {v}' for k, v in i['blue_factor_all'].items())}")
            log.info(f" 父因子详情{i['father']['uma_factor']}")
            log.info(f" 总计：{ sum(i['red_factor_all'].values())} 红,详情：{','.join(f'{k}: {v}' for k, v in i['red_factor_all'].items())}")
            log.info(f" 指定各因子命中详情[父，爷，奶]：{i['all_factor_match']}")
            log.info(f" 指定各因子命中详情[父]：{i['couple_factor_match']}")
            s += 1
    else:
        log.warning("一个组合也没有，放宽条件或者刷种马去吧")
