

import pandas as pd
import time
import bot.base.log as logger

log = logger.get_logger(__name__)

# 读取Excel文件中的所有sheet页
excel_file = 'resource/umamusume/data/compatibility_matrix.xlsx'
df_list = []

# ums_father_mother : compatibility
UMA_PARENT_COMPATIBILITY: dict[str:int] = {}
# ums_parent_grand : compatibility
UMA_GRAND_COMPATIBILITY: dict[str:int] = {}

UMA_TRANSLATE: dict[str:str] = {"特别周": "tebiezhou",
                                "无声铃鹿": "wushenglinglu",
                                "东海帝皇": "donghaidiwang",  # 国服不一样
                                "丸善斯基": "wanshansiji",
                                "富士奇石": "fushiqishi",
                                "小栗帽": "xiaolimao",
                                "黄金船": "huangjinchuan",
                                "伏特加": "futejia",
                                "大和赤骥": "dahechiji",
                                "大树快车": "dashukuaiche",
                                "草上飞": "caoshangfei",
                                "菱亚马逊": "lingyamaxun",
                                "目白麦昆": "mubaimaikun",
                                "神鹰": "shenying",
                                "好歌剧": "haogeju",
                                "成田白仁": "chengtianbairen",
                                "皇帝": "huangdi",
                                "气槽": "qicao",
                                "星云天空": "xingyuntiankong",
                                "琵琶晨光": "pipachenguang",
                                "重炮": "zhongpao",
                                "美保波旁": "meibaobopang",
                                "目白赖恩": "mubailaien",
                                "米浴": "miyu",
                                "爱丽速子": "ailisuzi",
                                "胜利彩券": "shenglijiangquan",  # 国服不一样
                                "真机伶": "zhenjiling",
                                "黄金城市": "huangjinchengshi",
                                "樱花进王": "yinghuajinwang",
                                "超级小海湾": "chaojixiliu",  # 国服不一样
                                "醒目飞鹰": "xingmufeiying",
                                "成田大进": "chengtiandajin",
                                "春乌拉拉": "chunwulala",
                                "待兼福来": "daijianfulai",
                                "优秀素质": "youxiusuzhi",
                                "帝王光辉": "diwangguanghui"}


def compatibility_matrix_load():
    start_time = time.time()

    for sheet_name in pd.read_excel(excel_file, sheet_name=None):
        if '换算版' in sheet_name or '双人' in sheet_name:
            continue
        if '祖辈相性' in sheet_name:
            # print(f"祖辈相性 : {sheet_name[:-4]}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df.fillna(0, inplace=True)
            for index, row in df.iterrows():
                for column_index, value in enumerate(row):
                    if column_index != 0:
                        row_name = UMA_TRANSLATE[row[0]]
                        column_name = UMA_TRANSLATE[df.columns[column_index]]
                        k = UMA_TRANSLATE[sheet_name[:-4]] + '_' + row_name+"_"+column_name
                        UMA_GRAND_COMPATIBILITY[k] = value

        if '父母相性' in sheet_name:
            # print(f"父母相性 : {sheet_name[:-4]}")
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df.fillna(0, inplace=True)
            for index, row in df.iterrows():
                for column_index, value in enumerate(row):
                    if column_index != 0:
                        row_name = UMA_TRANSLATE[row[0]]
                        column_name = UMA_TRANSLATE[df.columns[column_index]]
                        k = UMA_TRANSLATE[sheet_name[:-4]] + '_' + row_name+"_"+column_name
                        UMA_PARENT_COMPATIBILITY[k] = value

    log.info(f"加载相性表耗时:{time.time()-start_time}")


compatibility_matrix_load()
