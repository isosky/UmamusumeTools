import json
import time
import shutil


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
    log.info("开始处理马娘页面")
    if len(ctx.this_page_todo) > 0:
        log.info(f"还剩 {len(ctx.this_page_todo)} 个马娘待处理")
        temp = ctx.this_page_todo.pop()
        ctx.ctrl.click(temp[0]+10, temp[1]+10, "点击马娘")
        ctx.this_page_is_work = True
        time.sleep(1)
    else:
        if check_finish(ctx=ctx):
            time.sleep(1)
            return
        if ctx.this_page_done >= ctx.this_page_count and ctx.this_page_done != 0:
            log.info(">>>>>>> 翻页")
            ctx.ctrl.swipe(x1=350, y1=900, x2=350, y2=500, duration=1000, name="上滑")
            time.sleep(1)
            ctx.this_page_is_work = False
            ctx.this_page_done = 0
        screen = ctx.ctrl.get_screen()
        uma_result, duplication_dict = uma_list_match(screen)
        ctx.this_page_count = len(uma_result)
        for uma in uma_result:
            _temp = uma_result[uma]
            if _temp[-1] in duplication_dict:
                log.info(f'{_temp[-1]} 本页有同名同评分的，需要进行抓取')
            else:
                if _temp[-1] in ctx.uma_name_score:
                    if len(ctx.uma_name_score[_temp[-1]]) == 1:
                        # 将已经存在的添加进来
                        ctx.this_page_done += 1
                        ctx.uma_result[ctx.uma_name_score[_temp[-1]][0]] = ""
                        log.debug(f'{_temp[-1]} 已经抓取过，跳过')
                        continue
                    else:
                        log.info(f"{_temp[-1]} 有多个同名马娘同评分，再次处理")
            ctx.this_page_todo.append(_temp)
        log.info(f" 本页需要处理的马娘数量为 { len(ctx.this_page_todo)}")
        time.sleep(1)


def script_uma_frist_page(ctx: UmamusumeContext):
    img = ctx.current_screen
    parser_uma_frist_page(ctx, img)


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
    if check_finish(ctx=ctx):
        time.sleep(1)
        return


def check_finish(ctx: UmamusumeContext):
    log.info(f"ctx.this_page_count : {ctx.this_page_count}")
    log.info(f"ctx.this_page_done  : {ctx.this_page_done}")
    if ctx.this_page_done == 25 or ctx.this_page_count == ctx.this_page_done:
        log.info("需要判断是否到底了")
        img = ctx.ctrl.get_screen(to_gray=True)
        if image_match(img, UI_UMA_LIST_FINAL).find_match:
            log.info("到底了")
            for uma in ctx.uma_file_list:
                if uma not in ctx.uma_result:
                    log.info(f"{uma} 已经不存在了，移走")
                    shutil.move('userdata/'+CONFIG.role_name+'/'+uma+'.json', 'userdata/'+CONFIG.role_name+'_remove/'+uma+'.json')
            ctx.task.end_task(TaskStatus.TASK_STATUS_SUCCESS, EndTaskReason.COMPLETE)
            return True
    else:
        return False
