from typing import Dict

from bot.base.manifest import AppManifest
from bot.base.resource import NOT_FOUND_UI
from module.umamusume.asset.ui import *
from module.umamusume.context import build_context
from module.umamusume.hook import after_hook, before_hook
from module.umamusume.script.uma_collector.cultivate import *
from module.umamusume.task import UmamusumeTaskType, build_task
from module.umamusume.context import UmamusumeContext


# 事件列表
script_dicts: Dict[UmamusumeTaskType, dict] = {
    UmamusumeTaskType.UMAMUSUME_TASK_TYPE_TOOL: {
        MAIN_MENU: script_to_first_btn,
        MRT_MENU: script_to_mrt,
        UMAS_MENU: script_to_umas,
        MRT_LIST: script_to_uma,
        UMA_DETAIL_1: script_uma_frist_page,
        UMA_DETAIL_2: script_uma_second_page,
        UMA_DETAIL_3: script_uma_third_page,
        NOT_FOUND_UI: script_not_found_ui
    }
}

default_script_dict: Dict[UI, callable] = {

}


def exec_script(ctx: UmamusumeContext):
    if ctx.task.task_type in script_dicts:
        # for k in script_dicts[ctx.task.task_type]:
        log.info(ctx.current_ui)
        if ctx.current_ui in script_dicts[ctx.task.task_type]:
            script_dicts[ctx.task.task_type][ctx.current_ui](ctx)
            return
    if ctx.current_ui in default_script_dict:
        default_script_dict[ctx.current_ui](ctx)
    else:
        print("未找到此界面对应的默认脚本")


UmamusumeManifest = AppManifest(
    app_name="umamusume",
    app_package_name="com.bilibili.umamusu",
    app_activity_name="com.uo.sdk.SplashActivity",
    build_context=build_context,
    build_task=build_task,
    ui_list=scan_ui_list,
    script=exec_script,
    before_hook=before_hook,
    after_hook=after_hook
)
