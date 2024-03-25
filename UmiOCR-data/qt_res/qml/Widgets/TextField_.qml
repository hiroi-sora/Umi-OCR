// =============================================
// =============== 单行输入框样式 ===============
// =============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

TextField {
    color: theme.subTextColor  // 默认颜色
    font.pixelSize: size_.text  // 默认大小
    font.family: theme.dataFontFamily  // 默认字体
    property color borderColor: theme.coverColor3
    // 外边距
    leftInset: 0
    rightInset: 0
    topInset: 0
    bottomInset: 0
    // 内边距
    leftPadding: 4
    rightPadding: 4
    topPadding: 0
    bottomPadding: 0

    verticalAlignment: Text.AlignVCenter // 垂直居中
    focus: true // 键盘聚焦
    selectByMouse: true // 允许鼠标选中

    background: Rectangle {
        color: theme.bgColor
        radius: size_.btnRadius

        border.width: 1
        border.color: borderColor
    }
}