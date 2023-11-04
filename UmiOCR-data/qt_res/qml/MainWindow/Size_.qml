// ===========================================
// =============== 组件尺寸相关 ===============
// ===========================================

import QtQuick 2.15

Item {
    // ========================= 【尺寸】 =========================

    // 全局缩放值，适配分辨率
    property real scale: 1

    // 行高
    // 主要文字
    property int line: 16 * scale
    // 较小的文字
    property int smallLine: 13 * scale
    // 较大的文字
    property int largeLine: 20 * scale

    // 文字缩放值
    property real textScale: 1 // 由下列 languageScale 控制
    // 主要文字大小
    property int text: line * textScale
    // 较小的文字大小
    property int smallText: smallLine * textScale
    // 较大的文字大小
    property int largeText: largeLine * textScale

    // 窗口圆角
    property real windowRadius: 0
    // 基础圆角
    property real baseRadius: 6 * scale
    // 按钮圆角
    property real btnRadius: baseRadius
    // 面板圆角
    property real panelRadius: baseRadius * 1.7

    // 水平标签栏高度
    property real hTabBarHeight: line * 1.8

    // 常用间距
    property real spacing: 7 * scale
    // 小间距
    property real smallSpacing: 4 * scale

    // 语言缩放系数
    // 在相同的行高内，有些语言经过缩放可以表现更好。如英文可以比汉字的字号更小。
    // 通过在翻译文件中定义 languageScale 可以单独修改这种语言的缩放。
    property string languageScale: qsTr("1.0")
    
    Component.onCompleted: {
        const s = parseFloat(languageScale)
        if(!isNaN(s)) {
            textScale = s
        }
        else {
            console.log("[Warning] 语言缩放系数无法应用：", languageScale)
        }
    }
}