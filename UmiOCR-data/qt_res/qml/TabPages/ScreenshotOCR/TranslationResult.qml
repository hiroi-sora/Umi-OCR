import QtQuick 2.15
import QtQuick.Controls 2.15
import "../../Widgets"

Item {
    id: root
    property string original: ""
    property string translated: ""
    property string errorText: ""
    property bool busy: false
    property bool translationEnabled: false
    property string languageSummary: ""
    signal retry()
    property alias ctrlBar: controls

    Item {
        id: controls
        height: size_.line * 1.5
        anchors.left: parent.left
        anchors.right: parent.right
        Row {
            anchors.right: parent.right
            height: parent.height
            spacing: size_.smallSpacing
            Button_ {
                height: parent.height
                text_: qsTr("重新翻译")
                enabled: root.translationEnabled && root.original.length > 0 && !root.busy
                onClicked: root.retry()
            }
            Button_ {
                height: parent.height
                text_: qsTr("复制译文")
                enabled: root.translated.length > 0 && !root.busy
                onClicked: qmlapp.utilsConnector.copyText(root.translated)
            }
        }
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        contentWidth: availableWidth
        Column {
            width: parent.width
            spacing: size_.spacing
            Text_ {
                width: parent.width
                wrapMode: Text.Wrap
                text: root.languageSummary
                color: theme.subTextColor
            }
            Text_ {
                width: parent.width
                wrapMode: Text.Wrap
                color: root.errorText ? theme.noColor : theme.subTextColor
                text: !root.translationEnabled ? qsTr("点击图片上方的“翻译”启用，默认英文译为中文。")
                    : root.busy ? qsTr("正在翻译…")
                    : root.errorText ? root.errorText
                    : !root.original ? qsTr("截图、拖入或粘贴图片后显示译文。")
                    : qsTr("翻译完成")
            }
            Text_ { text: qsTr("译文"); visible: root.translated.length > 0 }
            TextEdit_ {
                width: parent.width
                readOnly: true
                text: root.translated
                visible: text.length > 0
            }
            Text_ { text: qsTr("原文"); visible: root.original.length > 0 }
            TextEdit_ {
                width: parent.width
                readOnly: true
                text: root.original
                visible: text.length > 0
            }
        }
    }
}
