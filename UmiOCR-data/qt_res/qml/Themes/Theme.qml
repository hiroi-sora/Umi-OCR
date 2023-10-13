// =========================================
// =============== 样式的基类 ===============
// =========================================

import QtQuick 2.15

Item {
    // 主题名称
    property string themeTitle: "Unknow theme"

    // ========================= 【颜色】 =========================

    // 主题颜色，不透明，由浅到深
    property color themeColor1 // 背景
    property color themeColor2 // 装饰性前景
    property color themeColor3 // 文字
    // 叠加层颜色，半透明，从浅到深
    property color coverColor1 // 大部分需要突出的背景
    property color coverColor2 // 按钮悬停
    property color coverColor3 // 阴影
    property color coverColor4 // 按钮按下

    property color bgColor // 背景
    property color tabBarColor // 标签栏
    property color textColor // 主要文字
    property color subTextColor // 次要文字
    property color yesColor // 允许、成功
    property color noColor // 禁止、失败

    // 必要的键
    property var keys: [
        "themeTitle",
        "themeColor1",
        "themeColor2",
        "themeColor3",
        "coverColor1",
        "coverColor2",
        "coverColor3",
        "coverColor4",
        "bgColor",
        "tabBarColor",
        "textColor",
        "subTextColor",
        "yesColor",
        "noColor",
    ]
    // 默认主题 / 当前读入的主题配置
    property var all: {
        "Light": {
            "themeTitle": "明亮",
            "bgColor": "#FFF",
            "themeColor1": "#FCF9BE",
            "themeColor2": "#FFDCA9",
            "themeColor3": "#C58940",
            "coverColor1": "#11000000",
            "coverColor2": "#22000000",
            "coverColor3": "#33000000",
            "coverColor4": "#55000000",
            "tabBarColor": "#F3F3F3",
            "textColor": "#000",
            "subTextColor": "#555",
            "yesColor": "#00CC00",
            "noColor": "#FF0000",
        },
        "Dark": {
            "themeTitle": "黑暗",
            "bgColor": "#444",
            "themeColor1": "#005c99",
            "themeColor2": "#009FFF",
            "themeColor3": "#00BFFF",
            "coverColor1": "#22FFFFFF",
            "coverColor2": "#33FFFFFF",
            "coverColor3": "#44FFFFFF",
            "coverColor4": "#55FFFFFF",
            "tabBarColor": "#4A4A4A",
            "textColor": "#FFF",
            "subTextColor": "#AAA",
            "yesColor": "#6EFC39",
            "noColor": "#FF2E2E",
        },
    }
    // 主题控制器
    property ThemeManager manager: ThemeManager{}

    // ========================= 【字体】 =========================

    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: "Microsoft YaHei"
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: "Microsoft YaHei"
}