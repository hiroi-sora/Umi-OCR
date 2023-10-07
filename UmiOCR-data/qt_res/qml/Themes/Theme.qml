// =========================================
// =============== 样式的基类 ===============
// =========================================

import QtQuick 2.15

Item {
    // 主题名称
    property string themeTitle

    // ========================= 【颜色】 =========================

    // 背景颜色
    property color bgColor

    // 主题颜色，不透明，由浅到深
    property color themeColor1 // 背景
    property color themeColor2 // 装饰性前景
    property color themeColor3 // 文字

    // 叠加层颜色，半透明，从浅到深
    property color coverColor1 // 大部分需要突出的背景
    property color coverColor2 // 按钮悬停
    property color coverColor3 // 阴影
    property color coverColor4 // 按钮按下

    // 标签栏颜色
    property color tabBarColor

    // 主要文字颜色
    property color textColor
    // 次要文字颜色
    property color subTextColor

    // 以下三种警告色，不同主题都应该为红绿，但饱和度可以根据主题背景来微调
    // 表示允许、成功的颜色
    property color yesColor: "green"
    // 表示禁止、失败的颜色
    property color noColor: "red"

    // ========================= 【字体】 =========================

    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: "Microsoft YaHei"
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: "Microsoft YaHei"

}