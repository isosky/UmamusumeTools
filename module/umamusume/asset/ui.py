from bot.base.resource import UI
import module.umamusume.asset.template as template

MAIN_MENU = UI("MAIN_MENU", [template.UI_MAIN_MENU], [])
MRT_MENU = UI("MRT_MENU", [template.UI_MRT_MENU], [])
UMAS_MENU = UI("UMAS_MENU", [template.UI_UMAS_MENU], [])
MRT_LIST = UI("MRT_LIST", [template.UI_MRT_LIST], [])
UMA_DETAIL_1 = UI("UMA_DETAIL_1", [template.UI_UMA_DETAIL_1], [])
UMA_DETAIL_2 = UI("UMA_DETAIL_2", [template.UI_UMA_DETAIL_2], [])
UMA_DETAIL_3 = UI("UMA_DETAIL_3", [template.UI_UMA_DETAIL_3], [])


scan_ui_list = [MAIN_MENU, MRT_MENU, UMAS_MENU, MRT_LIST, UMA_DETAIL_1, UMA_DETAIL_2, UMA_DETAIL_3]
