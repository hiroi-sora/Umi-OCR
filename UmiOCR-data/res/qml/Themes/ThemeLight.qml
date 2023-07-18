// ===========================================
// =============== 基础浅色样式 ===============
// ===========================================

import QtQuick 2.15

Theme {
    // 名称
    themeTitle: qsTr("明亮")

    // 背景颜色
    bgColor: "#FFF"
    // 高亮颜色
    highlightColor: "#68b94d"

    // 叠加层颜色，从浅到深
    coverColor1: "#11000000" // 大部分需要突出的背景
    coverColor2: "#22000000" // 按钮悬停
    coverColor3: "#33000000" // 阴影
    coverColor4: "#55000000" // 按钮按下

    // 标签栏颜色
    tabBarColor: "#F3F3F3"
    // 标签颜色（选中）
    tabColor: bgColor

    // 主要文字颜色
    textColor: "#000"
    // 次要文字颜色
    subTextColor: "#555"
}