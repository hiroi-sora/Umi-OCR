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
    property real textScale: 1
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

    
    // Component.onCompleted: {
    //     for(let i in Qt.application.screens) {
    //         const screen = Qt.application.screens[i]
    //         console.log("== 屏幕", i, screen)
    //         for(let s in screen) {
    //             if (typeof screen[s] === 'function')
    //                 continue
    //             console.log(s,screen[s])
    //         }
    //     }
    // }
}