// ======================================================
// =============== 复选框按钮，提供点击事件 ===============
// ======================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

Button_ {
    id: btn
    property bool enabledAnime: false
    property real margins_: size_.smallSpacing
    checkable: true
    checked: false
    width: checkBox.width + textComp.width + btn.margins_ * 3

    contentItem: Row {
        anchors.fill: parent
        anchors.leftMargin: btn.margins_
        spacing: btn.margins_

        // 复选框
        CheckBox_ {
            id: checkBox
            anchors.verticalCenter: parent.verticalCenter
            width: size_.line
            checked: btn.checked
            enabledAnime: btn.enabledAnime
        }
        
        // 文字
        Text_ {
            id: textComp
            anchors.verticalCenter: parent.verticalCenter
            text: btn.text_
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: btn.textSize
            color: btn.textColor_
            font.bold: btn.bold_
        }
    }
}