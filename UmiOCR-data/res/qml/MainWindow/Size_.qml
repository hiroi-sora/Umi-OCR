// ===========================================
// =============== 组件尺寸相关 ===============
// ===========================================

import QtQuick 2.15

Item {
    // ========================= 【尺寸】 =========================

    // 全局缩放值，适配分辨率
    property real scale: 1

    // 主要文字大小
    property int text: 16 *scale
    // 较小的文字大小
    property int smallText: 13 *scale
    // 较大的文字大小
    property int largeText: 20 *scale

    // 窗口圆角
    property real windowRadius: 0
    // 基础圆角
    property real baseRadius: 6 *scale
    // 按钮圆角
    property real btnRadius: baseRadius
    // 面板圆角
    property real panelRadius: baseRadius * 1.7
    
    // 水平标签栏高度
    property real hTabBarHeight: text * 1.8
    // 水平标签栏下方阴影分割线高度
    property real hTabBarShadowHeight: hTabBarHeight * 0.5
    // 水平标签最大宽度
    property real hTabMaxWidth: text * 8

    // 元素之间的常用间距
    property real spacing: 10
    // 小间距
    property real smallSpacing: spacing * 0.6
}