import re
import time
import cv2
import hashlib
import json

from bot.recog.image_matcher import image_match, compare_color_equal
from bot.recog.ocr import ocr_line
from module.umamusume.context import UmamusumeContext
from module.umamusume.asset import *
from module.umamusume.define import *
import bot.base.log as logger
from config import CONFIG

log = logger.get_logger(__name__)


# 功能实现

def parser_uma_frist_page(ctx: UmamusumeContext, img):
    score_img = img[269:291, 85:200]
    score_img = cv2.copyMakeBorder(score_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    score = ocr_line(score_img)
    score = re.sub("\\D", "", score)
    log.info(f"评分为：{score}")

    speed_img = img[345:375, 75:150]
    speed_img = cv2.copyMakeBorder(speed_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    speed_text = ocr_line(speed_img)
    speed_text = re.sub("\\D", "", speed_text)

    stamina_img = img[345:375, 210:280]
    stamina_img = cv2.copyMakeBorder(stamina_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    stamina_text = ocr_line(stamina_img)
    stamina_text = re.sub("\\D", "", stamina_text)

    power_img = img[345:375, 345:420]
    power_img = cv2.copyMakeBorder(power_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    power_text = ocr_line(power_img)
    power_text = re.sub("\\D", "", power_text)

    will_img = img[345:375, 480:555]
    will_img = cv2.copyMakeBorder(will_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    will_text = ocr_line(will_img)
    will_text = re.sub("\\D", "", will_text)

    intelligence_img = img[345:375, 615:690]
    intelligence_img = cv2.copyMakeBorder(intelligence_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    intelligence_text = ocr_line(intelligence_img)
    intelligence_text = re.sub("\\D", "", intelligence_text)

    log.info(f"属性为：{speed_text},{stamina_text},{power_text},{will_text},{intelligence_text}")

    uma_name = parse_uma_role(ctx, img)
    log.info(uma_name)
    base_info = {"uma_name": uma_name, "score": score, "speed": speed_text, "stamina": stamina_text, "power": power_text, "will": will_text, "intelligence": intelligence_text}
    base_info_list = ['-' if x == '' else str(x) for x in base_info.values()]
    uuid_str = "_".join(base_info_list)
    log.info(uuid_str)
    if uuid_str in ctx.exist_uma:
        log.info(f"{uuid_str} 已经获取过，跳过")
        ctx.uma_result[uuid_str] = {}
        ctx.ctrl.click(719, 1, "返回列表")
        ctx.exist_count += 1
        if ctx.exist_count > 5:
            return '超过5次'
        return None

    ctx.exist_count = 0
    ctx.uma_result[uuid_str] = {"base_info": base_info, "relation": {}, "factor": {}, "data_version": CONFIG.dataversion, "account": CONFIG.role_name}
    ctx.exist_uma[uuid_str] = ""
    ctx.uma_now = uuid_str
    # TODO 适应性解析
    # TODO 技能解析
    ctx.ctrl.click(360, 554, "点击继承")
    time.sleep(1)
    return None


def parse_uma_role(ctx: UmamusumeContext, img):
    # TODO 未识别的马娘怎么编号下，同一个用一个unknown_1,unknown_2之类的，后面批量替换就行了。
    temp1 = img[108:290]
    start_time = time.time()
    img = cv2.cvtColor(temp1, cv2.COLOR_RGB2GRAY)
    for i in range(len(UMA_ROLE_LIST)):
        result = image_match(img, UMA_ROLE_LIST[i])
        if result.find_match:
            log.info(UraRoleList(i+1))
            end_time = time.time()
            log.debug("detect 头像 cost: " + str(end_time - start_time))
            return UraRoleList(i+1).name.lower().split('_')[0]
    log.warning("有未添加的头像，请人工处理")
    cv2.imwrite("resource/unknown_uma/uma_" + str(int(time.time())) + ".jpg", temp1)
    end_time = time.time()
    log.debug("detect 头像 cost: " + str(end_time - start_time))
    return UraRoleList(0).name.lower().split('_')[0]


def parser_uma_second_page(ctx: UmamusumeContext, img):
    log.info("开始解析自己因子")
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    bottom = image_match(img_gray, UI_UMA_DETAIL_2_JICHENG).center_point[1]
    i = 0
    res_factor = {}
    origin_img = ctx.ctrl.get_screen()
    while i < 20:
        row = i // 2
        column = i % 2
        if (352+row*60+60) > (bottom-10):
            log.debug("超过《继承对象》")
            break
        factor_img = origin_img[(655+row*59):(655+row*59+60), (137+column*280):(137+column*280+270)]
        factor_img_gray = cv2.cvtColor(factor_img, cv2.COLOR_BGR2GRAY)
        if i > 1:
            # 如果没横向就是没因子了，跳出，用gray图去做match
            if not image_match(factor_img_gray, UI_PARENT_FACTOR_STAR).find_match:
                log.debug("没有因子了")
                break
        factor_txt_img = factor_img[14:34, 36:230]
        factor_txt_img = cv2.copyMakeBorder(factor_txt_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
        factor_txt = ocr_line(factor_txt_img)
        factor_level = 0
        factor_level_check_point = [factor_img[45, 110], factor_img[45, 135], factor_img[45, 160]]
        for fi in range(len(factor_level_check_point)):
            if not compare_color_equal(factor_level_check_point[fi], [223, 227, 237]):
                factor_level += 1
            else:
                break
        if len(factor_txt) < 1:
            log.warning(f"{ctx.uma_now}  自己 有因子未解析，需要检查")
            cv2.imwrite("resource/unknown_factor/factor_" + str(int(time.time())) + ".jpg", origin_img)
            cv2.imwrite("resource/unknown_factor/factor_" + str(int(time.time())) + ".jpg", factor_txt_img)
            i += 1
            break
        res_factor[factor_txt] = factor_level
        i += 1
    time.sleep(0.3)
    log.info(f"有 {i} 个因子")
    ctx.uma_result[ctx.uma_now]["factor"] = res_factor
    time.sleep(0.2)
    ctx.ctrl.click(582, 554, "点击养成信息")


def parser_uma_third_page(ctx: UmamusumeContext, img):
    parser_support_card_list(ctx)
    log.info("开始解析父母因子")
    parents_location = {'bb': {"loc": [120, 930], "parent": {"bb": [285, 870], "mm": [285, 980]}},
                        'mm': {"loc": [450, 930], "parent": {"bb": [620, 870], "mm": [620, 980]}}}
    for k, v in parents_location.items():
        get_parent_factor(ctx, k, v)
    time.sleep(0.5)
    parser_race_list(ctx)
    ctx.ctrl.click(719, 1, "返回列表")


def parser_support_card_list(ctx: UmamusumeContext):
    # TODO 支援卡解析
    pass


def parser_race_list(ctx: UmamusumeContext):
    # TODO 胜场解析
    pass


def get_parent_factor(ctx: UmamusumeContext, relation: str, infos: dict):
    md5, uma_name, factor, is_borrow = parser_parent_factor(ctx, relation, infos['loc'])
    if md5 not in ctx.uma_data_info:
        log.info(f"{uma_name} {md5} 不存在，抓取祖辈*****")
        ctx.uma_data_info[md5] = {'uma_name': uma_name, 'factor': factor, 'is_borrow': is_borrow, 'md5': md5}
        for k, v in infos['parent'].items():
            uma_name, factor = parser_parent_factor(ctx, k, v, isparent=True)
            ctx.uma_data_info[md5][k] = {'uma_name': uma_name, 'factor': factor, 'is_borrow': is_borrow}
    ctx.uma_result[ctx.uma_now]['relation'][relation] = ctx.uma_data_info[md5]
    time.sleep(0.5)


def parser_parent_factor(ctx: UmamusumeContext, relation: str, location: list, isparent: bool = False):
    ctx.ctrl.click(location[0], location[1], '点击头像')
    origin_img = ctx.ctrl.get_screen()
    origin_img_gray = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)
    while not image_match(origin_img_gray, UI_YINZIYILAN).find_match:
        origin_img = ctx.ctrl.get_screen()
        origin_img_gray = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)
        time.sleep(0.5)
    origin_img = ctx.ctrl.get_screen()
    uma_name = parse_uma_role(ctx, origin_img)
    # left_top 35,352,单个高度为60，长度为320

    basic_heigt = 352
    is_borrow = False
    origin_img_gray = cv2.cvtColor(origin_img, cv2.COLOR_BGR2GRAY)
    if image_match(origin_img_gray, UI_UMA_BORROW).find_match:
        log.info("这个赛马娘是借用的")
        is_borrow = True
        basic_heigt = 538

    i = 0
    res_factor = {}
    while i < 20:
        row = i // 2
        column = i % 2
        factor_img = origin_img[(basic_heigt+row*59):(basic_heigt+row*59+59), (35+column*330):(35+column*330+320)]
        factor_img_gray = cv2.cvtColor(factor_img, cv2.COLOR_BGR2GRAY)
        if i > 1:
            if not image_match(factor_img_gray, UI_PARENT_FACTOR_STAR).find_match:
                log.debug("没有因子了")
                break
        factor_txt_img = factor_img[10:37, 30:230]
        factor_txt = ocr_line(factor_txt_img)
        factor_level = 0
        factor_level_check_point = [factor_img[45, 135], factor_img[45, 160], factor_img[45, 185]]
        for fi in range(len(factor_level_check_point)):
            if not compare_color_equal(factor_level_check_point[fi], [223, 227, 237]):
                factor_level += 1
            else:
                break
        if len(factor_txt) < 1:
            log.warning(f"{ctx.uma_now} {uma_name} 有因子未解析，需要检查")
            cv2.imwrite("resource/unknown_factor/factor_" + str(int(time.time())) + ".jpg", origin_img)
            cv2.imwrite("resource/unknown_factor/factor_" + str(int(time.time())) + ".jpg", factor_txt_img)
            i += 1
            break
        res_factor[factor_txt] = factor_level
        i += 1
    time.sleep(0.3)
    ctx.ctrl.click(719, 1, "返回")
    log.info(f"{relation} 有 {i} 个因子")
    if not isparent:
        md5 = cal_md5(factor=res_factor)
        return md5, uma_name, res_factor, is_borrow
    else:
        return uma_name, res_factor


def cal_md5(factor: dict) -> str:
    # log.debug(f"输入的因子dict 为：{factor}")
    # 似乎没必要排序，因子是排好的
    str_data = json.dumps(factor)
    md5 = hashlib.md5(str_data.encode('utf-8')).hexdigest()
    log.debug(f"输出的md5 为：{md5}")
    return md5
