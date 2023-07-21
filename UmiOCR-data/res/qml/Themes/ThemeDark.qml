// ===========================================
// =============== 基础深色样式 ===============
// ===========================================

import QtQuick 2.15

Theme {
    // 名称
    themeTitle: qsTr("深色")

    // 背景颜色
    bgColor: "#444"
    
    // 主题颜色，不透明，由浅到深
    themeColor1: "#005c99" // 背景
    themeColor2: "#009FFF" // 装饰性前景
    themeColor3: "#00BFFF" // 文字

    // 叠加层颜色，从浅到深
    coverColor1: "#22FFFFFF" // 大部分需要突出的背景
    coverColor2: "#33FFFFFF" // 按钮悬停
    coverColor3: "#44FFFFFF" // 阴影
    coverColor4: "#55FFFFFF" // 按钮按下

    // 标签栏颜色
    tabBarColor: "#444"
    // 标签颜色（选中）
    tabColor: bgColor

    // 主要文字颜色
    textColor: "#FFF"
    // 次要文字颜色
    subTextColor: "#AAA"

    // 表示允许、成功的颜色
    yesColor: "#6EFC39"
    // 表示禁止、失败的颜色
    noColor: "#FF2E2E"
}