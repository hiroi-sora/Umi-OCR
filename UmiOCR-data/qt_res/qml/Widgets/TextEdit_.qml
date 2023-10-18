// ================================================
// =============== 标准文本编辑框样式 ===============
// ================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

TextEdit {
    wrapMode: TextEdit.Wrap // 尽量在单词边界处换行
    textFormat: TextEdit.PlainText // 纯文本格式
    readOnly: false // 可编辑
    selectByMouse: true // 允许鼠标选择文本
    selectByKeyboard: true // 允许键盘选择文本
    color: theme.textColor // 文本颜色
    selectedTextColor: theme.specialBgColor // 选区文字色
    selectionColor: theme.specialTextColor // 选区背景色
    font.pixelSize: size_.text
    font.family: theme.dataFontFamily
}