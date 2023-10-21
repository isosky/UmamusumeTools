
from module.cal_compatibility.asset.matrix_load import UMA_GRAND_COMPATIBILITY, UMA_PARENT_COMPATIBILITY
from module.cal_compatibility.asset.uma_load import UMA_DATA_ALL
from operator import itemgetter
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)


# TODO 春季优俊少女 可以在天王春和春季优俊少女中获得，怎么处理


def get_recommand_uma_list(target: dict, borrow: str = '', is_father: bool = True, mua_min_factor: int = 2, mua_min_blue: int = 4, is_bigmatch: bool = False, result_length: int = 10) -> list:
    """
    target = {'uma_name':'caoshangfei','factor_list':['逆时针','春季优俊少女','URA'],"constraints":['耐力>=3']}

    target.constraints只可以用蓝因子 # TODO

    borrow 表示借用的马的名称，拼音，计算相性的时候，会计算父母。如果为空，父母都用自己的。

    mua_min_factor 表示单个马和他的父辈，至少命中几个指定的因子才参与计算，min(mua_min_factor, len(temp_target_factor_list))

    is_father 表示target是目标马还是目标马的父辈，如果是父辈，那uma的父母不能是目标马

    第一个考虑指定因子在父母中是否存在，优先级为3个，2个，1个

    第二个考虑蓝因子

    第三个考虑相性

    返回结果：

    f：uuid

    m：uuid

    target_factor_list:

    ura:[0,1,2,0,1,2]  父，爷，奶，母，公，婆,0表示对应没这个因子

    """
    # TODO 参数校验
    _res = []
    # 计算每个马娘和目标因子的匹配程度
    temp_target_factor_list = target['factor_list']
    for uma in UMA_DATA_ALL:
        # log.debug(f" 开始计算 {UMA_LIST[uma]['uma_name']}")
        if is_bigmatch:
            # log.debug("大赛马考虑耐和智力")
            if UMA_DATA_ALL[uma]['blue_factor_count_match'] < mua_min_blue:
                # log.debug(f"计算大赛马： 当前计算马蓝因子数量为 {UMA_LIST[uma]['blue_factor_count_match']} < {mua_min_blue} 不满足要求")
                continue
        else:
            if UMA_DATA_ALL[uma]['blue_factor_count'] < mua_min_blue:
                # log.debug(f"计算普通马： 当前计算马蓝因子数量为 {UMA_LIST[uma]['blue_factor_count']} < {mua_min_blue} 不满足要求")
                continue
        if target['uma_name'] == UMA_DATA_ALL[uma]['uma_name']:
            # log.debug(f" 当前计算马与目标马重叠,target:{target['uma_name']},now:{UMA_LIST[uma]['uma_name']}")
            continue
        # 指定因子命中情况  [1,2,3] 表示 [当前马,父,母] 这个因子的等级
        _target_factor_match = {}
        _target_sum_count = 0
        _temp = UMA_DATA_ALL[uma]['factor_list']
        if not is_father:
            if target['uma_name'] == UMA_DATA_ALL[uma]['uma_father_name'] or target['uma_name'] == UMA_DATA_ALL[uma]['uma_mother_name']:
                # log.debug(f"当前计算父辈，祖辈出现目标马,target:{target['uma_name']},now:{UMA_LIST[uma]['uma_name']},father:{UMA_LIST[uma]['uma_father_name']},mathor:{UMA_LIST[uma]['uma_mother_name']}")
                continue

        for ttf in temp_target_factor_list:
            if ttf in _temp:
                _target_sum_count += len([num for num in _temp[ttf] if num != 0])
                _target_factor_match[ttf] = _temp[ttf]

        if _target_sum_count > min(mua_min_factor, len(temp_target_factor_list)):  # 减低计算量,如果只输入一个指定的白因子，那就按1算
            # log.debug("马娘满足最小因子要求")
            UMA_DATA_ALL[uma]['_target_factor_match'] = _target_factor_match

            # 有目标因子的才去计算相性
            _uma_cap_score = UMA_GRAND_COMPATIBILITY[target['uma_name']+'_'+UMA_DATA_ALL[uma]['uma_name']+'_'+UMA_DATA_ALL[uma]['uma_father_name']] + UMA_GRAND_COMPATIBILITY[target['uma_name']+'_'+UMA_DATA_ALL[uma]['uma_name']+'_'+UMA_DATA_ALL[uma]['uma_mother_name']]
            # _uma_cap_score = 0
            UMA_DATA_ALL[uma]['_uma_cap_score'] = _uma_cap_score
            _res.append(UMA_DATA_ALL[uma])

    log.info(f'满足要求的马娘总计: {len(_res)}')
    if len(_res) == 0:
        log.warn("一个组合也没有，放宽条件或者刷种马去吧")
        return []
    res = sorted(_res, key=itemgetter('uma_name'))
    return_res = cal_parents(target['uma_name'], temp_target_factor_list, res, borrow=borrow)
    return_res = sorted(return_res, key=itemgetter('couple_match_sum', 'couple_cap_score'), reverse=True)
    log.info(f"按couple_match_sum，couple_cap_score排序，返回前 {result_length} 个方案")
    return return_res[:result_length]


def cal_parents(target_name: str, temp_target_factor_list: list, uma_list: list, borrow: str) -> list:
    _temp_res = []
    ss = 0
    if borrow:
        for i in range(len(uma_list)):
            # 如果有借用，主要是算父母相性
            temp = uma_list[i]
            blue_factor_all = temp['blue_factor'].copy()
            red_factor_all = temp['red_factor'].copy()
            couple_factor_match = temp['_target_factor_match'].copy()
            couple_match_sum = sum(len([vv for vv in v if vv != 0]) for v in couple_factor_match.values())
            couple_cap_score = UMA_PARENT_COMPATIBILITY[target_name+'_'+temp['uma_name']+'_'+borrow] + temp['_uma_cap_score']
            _temp_res.append({'red_factor_all': red_factor_all, 'blue_factor_all': blue_factor_all, 'couple_match_sum': couple_match_sum, 'couple_factor_match': couple_factor_match, 'couple_cap_score': couple_cap_score, 'father': temp, 'mother': borrow})
            ss += 1
        if ss == 0:
            log.warn("一个组合也没有，放宽条件或者刷种马去吧")
            return []
        log.info(f"总计有：{ss} 种组合")
        return _temp_res
    for i in range(len(uma_list)):
        temp = uma_list[i]
        for j in uma_list[i+1:]:
            if temp['uma_name'] == j['uma_name']:
                continue
        ss += 1
        couple_factor_match = {}
        for ttf in temp_target_factor_list:
            temp_ss = [0, 0, 0]
            if ttf in temp['_target_factor_match']:
                temp_ss = temp['_target_factor_match'][ttf].copy()
            if ttf in j['_target_factor_match']:
                temp_ss.extend(j['_target_factor_match'][ttf])
            else:
                temp_ss.extend([0, 0, 0])
            couple_factor_match[ttf] = temp_ss
        # 计算相性
        couple_cap_score = UMA_PARENT_COMPATIBILITY[target_name+'_'+temp['uma_name']+'_'+j['uma_name']] + temp['_uma_cap_score'] + j['_uma_cap_score']
        # 蓝因子合并
        blue_factor_all = temp['blue_factor'].copy()
        blue_factor_all.update({k: blue_factor_all.get(k, 0) + v for k, v in j['blue_factor'].items()})

        # 红因子合并
        red_factor_all = temp['red_factor'].copy()
        red_factor_all.update({k: red_factor_all.get(k, 0) + v for k, v in j['red_factor'].items()})

        couple_match_sum = sum(len([vv for vv in v if vv != 0]) for v in couple_factor_match.values())

        _temp_res.append({'red_factor_all': red_factor_all, 'blue_factor_all': blue_factor_all, 'couple_match_sum': couple_match_sum, 'couple_factor_match': couple_factor_match, 'couple_cap_score': couple_cap_score, 'father': temp, 'mother': j})
    if ss == 0:
        log.warn("一个组合也没有，放宽条件或者刷种马去吧")
        return []
    log.info(f"总计有：{ss} 种组合")
    return _temp_res
