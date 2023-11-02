import re
import time
import cv2
import hashlib
import json
import random
import os
import numpy as np

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
    score = int(re.sub("\\D", "", score))
    log.info(f"评分为：{score}")

    speed_img = img[345:375, 75:150]
    speed_img = cv2.copyMakeBorder(speed_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    speed_text = ocr_line(speed_img)
    speed_text = int(re.sub("\\D", "", speed_text))

    stamina_img = img[345:375, 210:280]
    stamina_img = cv2.copyMakeBorder(stamina_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    stamina_text = ocr_line(stamina_img)
    stamina_text = int(re.sub("\\D", "", stamina_text))

    power_img = img[345:375, 345:420]
    power_img = cv2.copyMakeBorder(power_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    power_text = ocr_line(power_img)
    power_text = int(re.sub("\\D", "", power_text))

    will_img = img[345:375, 480:555]
    will_img = cv2.copyMakeBorder(will_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    will_text = ocr_line(will_img)
    will_text = int(re.sub("\\D", "", will_text))

    intelligence_img = img[345:375, 615:690]
    intelligence_img = cv2.copyMakeBorder(intelligence_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
    intelligence_text = ocr_line(intelligence_img)
    intelligence_text = int(re.sub("\\D", "", intelligence_text))

    log.info(f"属性为：{speed_text},{stamina_text},{power_text},{will_text},{intelligence_text}")

    uma_name = parse_uma_role(ctx, img)
    log.info(uma_name)
    base_info = {"uma_name": uma_name, "score": score, "speed": speed_text, "stamina": stamina_text, "power": power_text, "will": will_text, "intelligence": intelligence_text}
    base_info_list = ['-' if x == '' else str(x) for x in base_info.values()]
    uuid_str = "_".join(base_info_list)
    log.info(uuid_str)
    if uuid_str in ctx.uma_file_list:
        log.info(f"{uuid_str} 已经处理过，跳过")
        ctx.uma_result[uuid_str] = ''
        ctx.ctrl.click(719, 1, "返回列表")
        ctx.this_page_done += 1
        time.sleep(1)
        return None
    ctx.uma_result[uuid_str] = {"base_info": base_info, "relation": {}, "factor": {}, "data_version": CONFIG.dataversion, "account": CONFIG.role_name}
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
    log.debug(f"预计自己的因子行数为：{int(((bottom-10)-655)/60)+1}")
    expected_row = int(((bottom-10)-655)/60)+1
    i = 0
    res_factor = {}
    origin_img = ctx.ctrl.get_screen()
    while i < expected_row*2:
        row = i // 2
        column = i % 2
        if (655+row*60) > (bottom-10):
            log.debug("超过《继承对象》")
            break
        factor_img = origin_img[(655+row*59):(655+row*59+60), (137+column*280):(137+column*280+270)]
        factor_txt_img = factor_img[14:34, 36:230]
        factor_txt_img = cv2.copyMakeBorder(factor_txt_img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
        factor_txt = ocr_line(factor_txt_img)
        if factor_txt == '':
            log.debug("没有因子了")
            break
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
    ctx.this_page_done += 1
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
        factor_txt_img = factor_img[10:37, 30:230]
        factor_txt = ocr_line(factor_txt_img)
        if factor_txt == '':
            log.debug("没有因子了")
            break
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


def uma_list_match(target_image) -> dict:
    start_time = time.time()
    # 读取目标图像和原始图像
    # target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
    img_folder_path = 'resource/umamusume/uma_head'
    image_files = [f for f in os.listdir(img_folder_path) if os.path.isfile(os.path.join(img_folder_path, f))]

    # 定义一个变量来存储匹配到的位置
    matched_positions = []
    for file in image_files:
        image_path = os.path.join(img_folder_path, file)

        _image = cv2.imread(image_path)
        # 使用模板匹配方法来识别目标图像中的原始图像
        result = cv2.matchTemplate(target_image, _image, cv2.TM_CCOEFF_NORMED)

        # 设定一个阈值，用于确定匹配成功的程度
        threshold = 0.8
        target_image.shape[:2]
        # 在目标图像中查找匹配的位置
        loc = np.where(result >= threshold)

        for pt in zip(*loc[::-1]):
            match_score = result[pt[1], pt[0]]
            matched_positions.append([pt[0], pt[1], (file.split('.')[0]).split('_')[0], match_score])

    # 匹配的长度
    log.info(f'Matched positions length: {len(matched_positions)}')
    matched_positions = sorted(matched_positions, key=lambda point: (point[0], point[1]))
    # 去重
    temp_positions = {}
    if matched_positions:
        temp_positions[str(matched_positions[0][0])+'_'+str(matched_positions[0][1])] = matched_positions[0]
        for pt in matched_positions[1:]:
            if pt[1] > 855 or pt[1] < 120:
                continue
            is_closed = False
            _temp_positions = temp_positions.copy()
            # 10个像素内，选匹配度最高的
            for k, v in _temp_positions.items():
                if abs(pt[0]-v[0]) < 10 and abs(pt[1]-v[1]) < 10:
                    is_closed = True
                    if pt[3] < v[3]:
                        break
                    else:
                        temp_positions[k] = pt
                        break
            if not is_closed:
                temp_positions[str(pt[0])+'_'+str(pt[1])] = pt
    log.info(f"识别耗时：{time.time()-start_time}")
    log.info(f"去重后结果匹配的对象长度为： {len(temp_positions)}")
    log.info("开始识别评分")
    duplication_dict = {}
    _factor_dict = {}
    for v in temp_positions.values():
        ocr_txt_image = target_image[(v[1]+96):(v[1]+116), (v[0]):(v[0]+80)]
        ocr_txt_image = cv2.copyMakeBorder(ocr_txt_image, 20, 20, 20, 20, cv2.BORDER_CONSTANT, None, (255, 255, 255))
        uma_score = ocr_line(ocr_txt_image)
        if uma_score != '':
            uma_score = int(re.sub("\\D", "", uma_score))
        else:
            uma_score = 'None'
        _uma_score = v[2]+"_"+str(uma_score)
        v.append(_uma_score)  # shenying_11411
        if _uma_score not in _factor_dict:
            _factor_dict[_uma_score] = 1
        else:
            duplication_dict[_uma_score] = 1
            log.info(f"{_uma_score} 在本页有多个，需要都抓取判断一下")
    log.info("识别评分结束")
    if len(temp_positions) != 25:
        log.info("可能识别不全，图像先保存，待人工分析")
        color_dict = {}
        if len(temp_positions) > 0:
            # 画框
            for v in temp_positions.values():
                if v[2] not in color_dict:
                    color_dict[v[2]] = generate_random_color()
                cv2.rectangle(target_image, (v[0], v[1]), (v[0] + 78, v[1] + 96), color_dict[v[2]], 2)
            cv2.imwrite('resource/unknown_uma/'+'last' + str(int(time.time()))+'.jpg', target_image)
    return temp_positions, duplication_dict


def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)
