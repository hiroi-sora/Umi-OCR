// =========================================
// =============== 样式的基类 ===============
// =========================================

import QtQuick 2.15

QtObject {

    // ========================= 【颜色】 =========================

    // 背景颜色
    property color bgColor
    // 高亮颜色
    property color highlightColor
    // 标题栏颜色
    // property color titleBarColor

    // 叠加层颜色，从浅到深
    property color coverColor0
    property color coverColor1
    property color coverColor2
    property color coverColor3
    property color coverColor4

    // 标签栏颜色
    property color tabBarColor
    // 标签颜色（选中）
    property color tabColor

    // 主要文字颜色
    property color textColor
    // 次要文字颜色
    property color subTextColor

    // 表示允许、成功的颜色
    property color yesColor: "green"
    // 表示禁止、失败的颜色
    property color noColor: "red"

    // ========================= 【字体】 =========================

    // 主要UI文字字体，内容可控，可以用裁切的ttf
    property string fontFamily: "Microsoft YaHei"
    // 数据显示文字字体，内容不可控，用兼容性好的系统字体
    property string dataFontFamily: "Microsoft YaHei"

    // ========================= 【尺寸】 =========================

    // 全局缩放值，适配分辨率
    property real scale: 1

    // 主要文字大小
    property int textSize: 16 *scale
    // 较小的文字大小
    property int smallTextSize: 13 *scale

    // 窗口圆角
    property real windowRadius: 0
    // 基础圆角
    property real baseRadius: 6 *scale
    // 按钮圆角
    property real btnRadius: baseRadius
    // 面板圆角
    property real panelRadius: baseRadius * 1.7
    
    // 水平标签栏高度
    property real hTabBarHeight: textSize * 1.8
    // 水平标签栏下方阴影分割线高度
    property real hTabBarShadowHeight: hTabBarHeight * 0.5
    // 水平标签最大宽度
    property real hTabMaxWidth: textSize * 8

    // 元素之间的常用间距
    property real spacing: 10
    // 小间距
    property real smallSpacing: spacing * 0.6


    // ========================= 【特效】 =========================

    // 是否全局启用美化特效
    property bool enabledEffect: true
    // 关闭美化则取消圆角
    Component.onCompleted: {
        if(!enabledEffect){
            windowRadius = baseRadius = panelRadius = btnRadius = 0
        }
    }
    
}