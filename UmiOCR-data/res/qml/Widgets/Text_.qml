// ===========================================
// =============== 标准文字样式 ===============
// ===========================================

import QtQuick 2.15

Text {
    // 默认颜色
    color: theme.textColor
    // 默认大小
    font.pixelSize: size_.text
    // 默认字体
    font.family: theme.fontFamily
}