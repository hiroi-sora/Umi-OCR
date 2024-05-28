// =========================================
// =============== 图标按钮栏 ===============
// =========================================

import QtQuick 2.15


Row {
    id: bRoot
    /* btnList 每一项: {
        // 必填
        "icon": "screenshot", // 图标
        // 选填
        "onClicked": func, // 回调函数
        "toolTip": "提示，支持",
        "text": "显示文本",
        "color": theme.subTextColor,
        "bgColor": theme.subTextColor,
    } */
    property var btnList: []

    // 常用按钮的翻译
    function tr(text) {
        return trTable[text]
    }
    property var trTable: {
        "右键菜单": qsTr("右键菜单"),
        "保存图片": qsTr("保存图片"),
        "图片大小：适应窗口": qsTr("图片大小：适应窗口"),
        "图片大小：实际": qsTr("图片大小：实际"),

        "截图": qsTr("截图"),
        "粘贴": qsTr("粘贴"),
        "屏幕截图": qsTr("屏幕截图"),
        "粘贴图片": qsTr("粘贴图片"),
    }


    spacing: size_.smallSpacing
    Repeater {
        model: bRoot.btnList

        IconTextButton {
            anchors.top: bRoot.top
            anchors.bottom: bRoot.bottom
            // width: height
            icon_: modelData.icon
            color: modelData.color || theme.subTextColor
            bgColor_: modelData.bgColor || "#00000000"
            text_: modelData.text || ""
            toolTip: modelData.toolTip || ""
            // 函数类型onClicked只能用 [index] 访问
            onClicked: btnList[index].onClicked ? btnList[index].onClicked() : undefined
        }
    }
}