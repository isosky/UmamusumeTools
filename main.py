import sys
import bot.base.foldercheck

from bot.base.manifest import register_app, APP_MANIFEST_LIST
from module.umamusume.manifest import UmamusumeManifest
import bot.engine.executor as executor
import bot.base.log as logger

log = logger.get_logger(__name__)

if __name__ == '__main__':
    if sys.version_info.minor != 10 or sys.version_info.micro != 9:
        print("\033[33m{}\033[0m".format("注意：python 版本号不正确，可能无法正常运行"))
        print("建议python版本：3.10.9 当前：" + sys.version)
    register_app(UmamusumeManifest)
    task_executor = executor.Executor()
    app_name = 'umamusume'
    task_execute_mode = 1
    task_type = 2
    task_desc = '育成'
    cron_job_config = None
    # 从网页生成 TODO 改成读配置文件 TODO 改成命令行 TODO
    attachment_data = {'expect_attribute': [1000, 700, 700, 250, 400], 'follow_support_card_name': '一颗安心糖', 'follow_support_card_level': 50, 'extra_race_list': [1701, 2303, 2703, 2905, 3103, 3303, 3403, 4408, 4506, 4608, 4804, 5407, 5605, 6006, 6701, 6807, 7008, 7204], 'learn_skill_list': [
        '圆弧艺术家', '弧线大师', '最后冲刺', '春季优俊少女', '逆时针', '标准距离'], 'tactic_list': [4, 4, 4], 'clock_use_limit': 3, 'learn_skill_threshold': 500, 'allow_recover_tp': False, 'learn_skill_only_user_provided': False, 'extra_weight': [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]}
    app_config = APP_MANIFEST_LIST[app_name]
    # TODO 优化build_task的方式
    task = app_config.build_task(
        task_execute_mode, task_type, task_desc, cron_job_config, attachment_data)

    task_executor.start(task)
