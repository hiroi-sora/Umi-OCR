// =============================================
// =============== 忽略区域编辑器 ===============
// =============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import ".."

Rectangle {
    id: iRoot
    visible: false
    color: theme.coverColor4
    property string previewPath: "" // 图片预览路径
    property string previewType: "" // 图片预览路径
    property var imageWithIgnore: undefined // 存放图片组件
    property bool running: false

    // 显示面板
    function show() {
        running = false
        iRoot.visible = true
    }
    function showPath(path) {
        show()
        imageWithIgnore.showPath(path)
        if(pathPreview) {
            pathPreview(path)
            running = true
        }
    }
    function showImgID(imgID) {
        show()
        imageWithIgnore.showImgID(imgID)
        if(imgIdPreview) {
            imgIdPreview(imgID)
            running = true
        }
    }
    // 关闭面板
    function close() {
        running = false
        iRoot.visible = false
    }
    // 调用预览函数
    property var pathPreview // (path)
    property var imgIdPreview // (imgID)
    // 获取预览
    function getPreview(res, path="", imgID="") {
        running = false
        if(path) imageWithIgnore.showPath(path)
        else if(imgID) imageWithIgnore.showImgID(imgID)
        imageWithIgnore.showTextBoxes(res)
    }

    MouseArea {
        anchors.fill: parent
        onWheel: {} // 拦截滚轮事件
        hoverEnabled: true // 拦截悬停事件
        onClicked: close() // 单击关闭面板
        cursorShape: Qt.PointingHandCursor
    }
    Loader {
        id: panelLoader
        asynchronous: false // 同步实例化
        sourceComponent: com
        active: iRoot.visible
    }

    Component {
        id: com
        Panel {
            parent: iRoot
            anchors.fill: parent
            anchors.margins: size_.line * 2
            color: theme.bgColor
            MouseArea {
                anchors.fill: parent
                onClicked: {}
            }
            // 左控制栏
            Item {
                id: lCtrl
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.margins: size_.spacing * 2
                width: size_.line * 10

                Column {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: size_.spacing
                    Button_ {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        bgColor_: theme.coverColor1
                        text_: qsTr("保存并返回")
                        onClicked: close()
                    }
                    Text_ {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        wrapMode: TextEdit.Wrap
                        color: theme.subTextColor
                        font.pixelSize: size_.smallText
                        text: qsTr("拖入本地图片：OCR预览\n滚轮：缩放\n左键：拖拽\n右键：绘制忽略区域\n\n可绘制一个或多个忽略区域矩形框。在执行批量OCR时，完全位于忽略区域内的文本块将被排除。\n比如批量处理影视截图时，可在右上角水印处添加忽略区域，避免输出水印文本。")
                    }
                }
                Column {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: size_.spacing
                    Button_ {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        bgColor_: theme.coverColor1
                        text_: qsTr("撤销")
                        onClicked: imageWithIgnore.revokeIg()
                    }
                    Button_ {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        bgColor_: theme.coverColor1
                        textColor_: theme.noColor
                        text_: qsTr("清空")
                        onClicked: imageWithIgnore.clearIg()
                    }
                }
            }
            // 右图片组件
            ImageWithIgnore {
                id: imageWithIgnore
                anchors.left: lCtrl.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.margins: size_.spacing
                anchors.leftMargin: size_.spacing * 2

                Component.onCompleted: {
                    iRoot.imageWithIgnore = this
                }

                // 加载图标
                Loading{
                    anchors.centerIn: parent
                    visible: running
                }
            }
            // 文件拖拽
            DropArea_ {
                anchors.fill: parent
                callback: (paths)=>{
                    paths = qmlapp.utilsConnector.findImages(paths, false)
                    if(paths && paths.length > 0) {
                        showPath(paths[0])
                    }
                }
            }
        }
    }
}