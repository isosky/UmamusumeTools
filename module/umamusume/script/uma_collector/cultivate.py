import json
import time
import cv2


from bot.base.task import TaskStatus, EndTaskReason
from bot.recog.image_matcher import image_match
from module.umamusume.asset.point import *
from module.umamusume.context import UmamusumeContext
from module.umamusume.script.uma_collector.parse import *
from config import CONFIG
import bot.base.log as logger

log = logger.get_logger(__name__)


def script_to_first_btn(ctx: UmamusumeContext):
    ctx.ctrl.click_by_point(TO_FIRST_BTN)
    time.sleep(0.5)


def script_to_mrt(ctx: UmamusumeContext):
    ctx.ctrl.click_by_point(TO_MRT_BTN)
    time.sleep(0.5)


def script_to_umas(ctx: UmamusumeContext):
    ctx.ctrl.click_by_point(TO_YILAN_BTN)
    # TODO 关闭筛选并且按登记日降序排列
    time.sleep(0.5)


def script_to_uma(ctx: UmamusumeContext):
    # 一行5个，默认5行，单个头像应该是130*160 第一个 90，180
    # TODO 从列表抓，判断哪些抓过，哪些需要处理
    # uma_selector = 0
    if ctx.uma_selector > 24:
        ctx.ctrl.swipe(x1=350, y1=900, x2=350, y2=450, duration=1000, name="上滑")
        ctx.uma_selector = 0
        time.sleep(1)
        # ctx.task.end_task(TaskStatus.TASK_STATUS_INTERRUPT, EndTaskReason.MANUAL_ABORTED)
        return
    log.info(ctx.uma_selector)
    log.debug(f"下一个点击的位置为：{90+ctx.uma_selector % 5*130} , {180+ctx.uma_selector // 5*160}")
    ctx.ctrl.click(90+ctx.uma_selector % 5*130, 180+ctx.uma_selector // 5*160, "")
    ctx.uma_selector += 1
    time.sleep(1)
    check_finish(ctx=ctx)


def script_uma_frist_page(ctx: UmamusumeContext):
    img = ctx.current_screen
    result_str = parser_uma_frist_page(ctx, img)
    if result_str == '超过5次':
        log.info("连续存在的马娘超过5次")
        ctx.ctrl.click(719, 1, "")
        ctx.task.end_task(TaskStatus.TASK_STATUS_SUCCESS, EndTaskReason.COMPLETE)


def script_not_found_ui(ctx: UmamusumeContext):
    temp = ctx.ctrl.get_screen()
    # cv2.imwrite("not_found_ui.jpg", temp)
    # ctx.task.end_task(TaskStatus.TASK_STATUS_INTERRUPT, EndTaskReason.MANUAL_ABORTED)
    ctx.ctrl.click(719, 1, "")


def script_uma_second_page(ctx: UmamusumeContext):
    img = ctx.current_screen
    parser_uma_second_page(ctx, img)


def script_uma_third_page(ctx: UmamusumeContext):
    img = ctx.current_screen
    parser_uma_third_page(ctx, img)
    log.info(f"存储数据文件:{ctx.uma_now}")
    with open('userdata/'+CONFIG.role_name+'/'+ctx.uma_now+'.json', 'w', encoding="utf-8") as f:
        f.write(json.dumps(ctx.uma_result[ctx.uma_now], ensure_ascii=False))
    check_finish(ctx=ctx)


def check_finish(ctx: UmamusumeContext):
    if ctx.uma_selector == 25:
        log.info("需要判断是否到底了")
        img = ctx.ctrl.get_screen(to_gray=True)
        if image_match(img, UI_UMA_LIST_FINAL).find_match:
            log.info("到底了")
            ctx.task.end_task(TaskStatus.TASK_STATUS_SUCCESS, EndTaskReason.COMPLETE)
            return
