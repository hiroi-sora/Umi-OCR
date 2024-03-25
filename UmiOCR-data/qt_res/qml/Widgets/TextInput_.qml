// ================================================
// =============== 标准文字编辑框样式 ===============
// ================================================

import QtQuick 2.15

TextInput {
    color: theme.subTextColor  // 默认颜色
    font.pixelSize: size_.text  // 默认大小
    font.family: theme.dataFontFamily  // 默认字体
    leftPadding: 4
    rightPadding: 4
    verticalAlignment: Text.AlignVCenter // 垂直居中
    focus: true // 键盘聚焦
    selectByMouse: true // 允许鼠标选中
    property alias hoverColor: mouseAreaBackgroud.color_ // 鼠标悬浮时的颜色

    MouseAreaBackgroud {
        id: mouseAreaBackgroud
        cursorShape: Qt.IBeamCursor
    }
}