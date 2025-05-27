import matplotlib.font_manager as fm
from fontTools.ttLib import TTFont


def font_has_char(font_path, char):
    """判断字体文件是否包含某字符"""
    try:
        font = TTFont(font_path, lazy=True, fontNumber=0)
        for table in font["cmap"].tables:
            if ord(char) in table.cmap:
                return True
        return False
    except Exception as e:
        # 有些字体可能损坏或不兼容，跳过
        print(f"⚠️ 不能读取字体: {font_path}，错误: {e}")
        return False


def find_chinese_fonts():
    char = "又"
    found_fonts: tuple[str, str] = []
    # 遍历 matplotlib 收录的所有字体
    for font_entry in fm.fontManager.ttflist:
        font_path = font_entry.fname
        font_name = font_entry.name
        if font_has_char(font_path, char):
            found_fonts.append((font_name, font_path))
    return found_fonts


def print_chinese_fonts():
    fonts = find_chinese_fonts()
    print("以下是系统中所有支持中文的字体的名称：")
    """打印所有包含特定中文字符的字体"""
    for font_name, _ in fonts:
        print(font_name)
