import re
import time
import cv2

from bot.recog.image_matcher import image_match, compare_color_equal
from bot.recog.ocr import ocr_line
from module.umamusume.context import UmamusumeContext
from module.umamusume.asset import *
from module.umamusume.define import *
import bot.base.log as logger

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

    log.info(f"评分为：{speed_text} {stamina_text} {power_text} {will_text} {intelligence_text}")

    role_name = parse_uma_role(ctx, img)
    log.info(role_name)
    base_info = {"role_name": role_name, "score": score, "speed": speed_text, "stamina": stamina_text, "power": power_text, "will": will_text, "intelligence": intelligence_text}
    base_info_list = ['-' if x == '' else str(x) for x in base_info.values()]
    uuid_str = "_".join(base_info_list)
    log.info(uuid_str)
    if uuid_str in ctx.exsit_uma:
        # TODO 优化结束方式
        log.info(f"{uuid_str} 已经获取过，跳过")
        ctx.ctrl.click(719, 1, "返回列表")
        return
    ctx.uma_result[uuid_str] = {"base_info": base_info, "relation": {}, "factor": {}}
    ctx.uma_now = uuid_str
    # TODO 适应性解析
    # TODO 技能解析
    ctx.ctrl.click(360, 554, "点击继承")
    time.sleep(0.5)


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
    cv2.imwrite("resource/unknown_uma/npc_role" + str(int(time.time())) + ".jpg", temp1)
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
        if i > 2:
            # 如果没横向就是没因子了，跳出，用gray图去做match
            if not image_match(factor_img_gray, UI_PARENT_FACTOR_STAR).find_match:
                log.debug("没有因子了")
                break

        factor_txt_img = factor_img[14:34, 36:230]
        factor_txt = ocr_line(factor_txt_img)
        factor_level = 0
        factor_level_check_point = [factor_img[45, 110], factor_img[45, 135], factor_img[45, 160]]
        for fi in range(len(factor_level_check_point)):
            if not compare_color_equal(factor_level_check_point[fi], [223, 227, 237]):
                factor_level += 1
            else:
                break
        if len(factor_txt) < 1:
            log.warning(f"{ctx.uma_now} 有因子未解析，需要检查")
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
    parents_location = {'bb': [120, 930],
                        'yy': [285, 870],
                        'nn': [285, 980],
                        'mm': [450, 930],
                        'wg': [620, 870],
                        'wp': [620, 980]}
    for k, v in parents_location.items():
        parser_parent_factor(ctx, k, v)
    time.sleep(0.5)
    parser_race_list(ctx)
    ctx.ctrl.click(719, 1, "返回列表")


def parser_support_card_list(ctx: UmamusumeContext):
    # TODO 支援卡解析
    pass


def parser_race_list(ctx: UmamusumeContext):
    # TODO 胜场解析
    pass


def parser_parent_factor(ctx: UmamusumeContext, relation: str, location: list):
    ctx.ctrl.click(location[0], location[1], relation)
    time.sleep(0.5)
    origin_img = ctx.ctrl.get_screen()
    role_name = parse_uma_role(ctx, origin_img)
    # left_top 35,352,单个高度为60，长度为320

    is_borrow = False
    basic_heigt = 352
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
        factor_img = origin_img[(basic_heigt+row*60):(basic_heigt+row*60+60), (35+column*330):(35+column*330+320)]
        factor_img_gray = cv2.cvtColor(factor_img, cv2.COLOR_BGR2GRAY)
        if i > 2:
            if not image_match(factor_img_gray, UI_PARENT_FACTOR_STAR).find_match:
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
            log.warning(f"{ctx.uma_now} 有因子未解析，需要检查")
        res_factor[factor_txt] = factor_level
        i += 1
    time.sleep(0.3)
    log.info(f"{relation} 有 {i} 个因子")
    ctx.uma_result[ctx.uma_now]["relation"][relation] = {}
    ctx.uma_result[ctx.uma_now]["relation"][relation]['uma_name'] = role_name
    ctx.uma_result[ctx.uma_now]["relation"][relation]['factor'] = res_factor
    ctx.uma_result[ctx.uma_now]["relation"][relation]['factor'] = res_factor
    ctx.uma_result[ctx.uma_now]["relation"][relation]['is_borrow'] = is_borrow
    ctx.ctrl.click(719, 1, "返回")
