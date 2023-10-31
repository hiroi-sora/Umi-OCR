// =========================================
// =============== 样式的基类 ===============
// =========================================

import QtQuick 2.15

Item {
    // 主题名称
    property string themeTitle: "Unknow theme"

    // ========================= 【颜色】 =========================

    property color tabBarColor // 标签栏
    property color bgColor // 背景
    property color textColor // 主要文字
    property color subTextColor // 次要文字
    property color yesColor // 允许、成功
    property color noColor // 禁止、失败
    property color specialBgColor // 特殊背景，弹窗确认按钮
    property color specialTextColor // 特殊前景，文字、图标
    // 叠加层颜色，半透明，从浅到深
    property color coverColor1 // 大部分需要突出的背景
    property color coverColor2 // 按钮悬停
    property color coverColor3 // 阴影
    property color coverColor4 // 按钮按下

    // 必要的键
    property var keys: [
        "themeTitle",
        "tabBarColor",
        "bgColor",
        "textColor",
        "subTextColor",
        "yesColor",
        "noColor",
        "specialBgColor",
        "specialTextColor",
        "coverColor1",
        "coverColor2",
        "coverColor3",
        "coverColor4",
    ]
    // 默认主题 / 当前读入的主题配置
    property var all: {
        // 默认主题
        "Default Light": {
            "themeTitle": qsTr("珍珠白"),
            "tabBarColor": "#F3F3F3",
            "bgColor": "#FFF",
            "textColor": "#000",
            "subTextColor": "#555",
            "yesColor": "#00CC00",
            "noColor": "#FF0000",
            "specialBgColor": "#FCF9BE",
            "specialTextColor": "#C58940",
            "coverColor1": "#11000000",
            "coverColor2": "#22000000",
            "coverColor3": "#33000000",
            "coverColor4": "#55000000",
        },
        "Default Dark": {
            "themeTitle": qsTr("云墨黑"),
            "tabBarColor": "#4A4A4A",
            "bgColor": "#444",
            "textColor": "#FFF",
            "subTextColor": "#AAA",
            "yesColor": "#6EFC39",
            "noColor": "#FF2E2E",
            "specialBgColor": "#005c99",
            "specialTextColor": "#00BFFF",
            "coverColor1": "#22FFFFFF",
            "coverColor2": "#33FFFFFF",
            "coverColor3": "#44FFFFFF",
            "coverColor4": "#55FFFFFF",
        },
        // 抄： https://github.com/altercation/solarized
        "Solarized Light": {
            "themeTitle": "Solarized Light",
            "tabBarColor": "#d9d2c2",
            "bgColor": "#fdf6e3",
            "textColor": "#586e75",
            "subTextColor": "#839496",
            "yesColor": "#48985d",
            "noColor": "#e51d09",
            "specialBgColor": "#FCF9BE",
            "specialTextColor": "#C58940",
            "coverColor1": "#11000000",
            "coverColor2": "#22000000",
            "coverColor3": "#33000000",
            "coverColor4": "#55000000"
        },
        "Solarized Dark": {
            "themeTitle": "Solarized Dark",
            "tabBarColor": "#004052",
            "bgColor": "#002b36",
            "textColor": "#93a1a1",
            "subTextColor": "#657b83",
            "yesColor": "#6EFC39",
            "noColor": "#f14c4c",
            "specialBgColor": "#00517D",
            "specialTextColor": "#00BFFF",
            "coverColor1": "#19FFFFFF",
            "coverColor2": "#29FFFFFF",
            "coverColor3": "#44FFFFFF",
            "coverColor4": "#55FFFFFF"
        },
        // 抄： https://github.com/Fndroid/clash_for_windows_pkg
        "Cyberpunk": {
            "themeTitle": qsTr("赛博朋克"),
            "tabBarColor": "#084A5A",
            "bgColor": "#136377",
            "textColor": "#FCEC0C",
            "subTextColor": "#CF9F0F",
            "yesColor": "#6EFC39",
            "noColor": "#FF5E5E",
            "specialBgColor": "#00517D",
            "specialTextColor": "#00BFFF",
            "coverColor1": "#33000000",
            "coverColor2": "#29FFFFFF",
            "coverColor3": "#44FFFFFF",
            "coverColor4": "#55FFFFFF"
        }
    }
    // 主题控制器
    property ThemeManager manager: ThemeManager{}

    // ========================= 【字体】 =========================

    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: "Microsoft YaHei"
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: "Microsoft YaHei"
}