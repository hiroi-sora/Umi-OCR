// ===========================================
// =============== 文档预览面板 ===============
// ===========================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import DocPreviewConnector 1.0

import "../../Widgets"
import "../../Widgets/ImageViewer"

ModalLayer {
    id: pRoot
    property var updateInfo // 更新信息函数
    property bool running: false
    property string previewPath: ""
    property string password: ""
    property bool isEncrypted: false // 已加密
    property bool isAuthenticate: false // 密码正确
    property int previewPage: -1
    property int pageCount: -1
    property int rangeStart: -1
    property int rangeEnd: -1

    // 展示文档
    // info: path, page_count, range_start, range_end, is_encrypted, password, is_authenticate
    function show(info) {
        visible = true
        previewPath = info.path
        pageCount = info.page_count
        previewPage = info.range_start
        rangeStart = info.range_start
        rangeEnd = info.range_end
        password = info.password
        isEncrypted = info.is_encrypted
        isAuthenticate = info.is_authenticate
        toPreview()
    }

    // 返回，更新信息
    onVisibleChanged: {
        if(visible) return
        if(rangeStart < 1) rangeStart = 1
        if(rangeStart > pageCount) rangeStart = pageCount
        if(rangeEnd < rangeStart) rangeEnd = rangeStart
        if(rangeEnd > pageCount) rangeEnd = pageCount
        if(updateInfo) {
            updateInfo(previewPath, {
                pages: `${rangeStart}-${rangeEnd}`,
                state: isAuthenticate ? "" : qsTr("密码错误"),
                range_start: rangeStart,
                range_end: rangeEnd,
                password: password,
                is_authenticate: isAuthenticate,
            })
        }
        qmlapp.popup.simple(qsTr("文档信息已更新"), previewPath)
    }

    // 翻页。to直接翻页，flag加减页。
    function changePage(to, flag=0) {
        if (typeof to === "string") {
            to = parseInt(to, 10)
        }
        if(flag != 0) {
            to = previewPage + flag
        }
        if(previewPage != to && to > 0 && to <= pageCount) {
            previewPage = to
            toPreview()
        }
    }

    // 预览一页文档
    function toPreview() {
        running = true
        if(previewPage < 1) previewPage = 1
        if(previewPage > pageCount) previewPage = pageCount
        prevConn.preview(previewPath, previewPage, password)
    }
    // 预览连接器
    DocPreviewConnector {
        id: prevConn
        // 图片渲染的回调
        onPreviewImg: function(imgID) {
            const title = qsTr("打开文档失败")
            if(imgID === "[Warning] isEncrypted") {
                qmlapp.popup.simple(title, qsTr("请填写正确的密码"))
                isAuthenticate = false
            }
            else if(imgID.startsWith("[Error]")) {
                qmlapp.popup.message(title, imgID, "error")
            }
            else {
                imgViewer.showImgID(imgID)
                if(!isAuthenticate) {
                    qmlapp.popup.simple(qsTr("密码正确"), password)
                    isAuthenticate = true
                }
            }
        }
    }

    // 左：控制面板
    Item {
        id: fileInfoItem
        anchors.fill: parent
        Column {
            anchors.fill: parent
            spacing: size_.spacing
            // ===== 文件名 =====
            Text_ {
                text: previewPath
                anchors.left: parent.left
                anchors.right: parent.right
                wrapMode: TextEdit.WrapAnywhere // 任意换行
                maximumLineCount: 4 // 限制行数
                color: theme.subTextColor
                font.pixelSize: size_.smallText
            }
            // ===== 密码 =====
            Row {
                visible: isEncrypted && !isAuthenticate // 已加密，未填密码，才显示
                spacing: size_.spacing
                height: size_.line + size_.spacing * 2
                Text_ {
                    color: theme.noColor
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("密码：")
                }
                Rectangle {
                    width: size_.line * 6
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    color: theme.bgColor
                    TextInput_ {
                        clip: true
                        anchors.fill: parent
                        bgColor: "#00000000"
                        text: password
                        onTextChanged: password = text
                    }
                }
                IconButton {
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: height
                    icon_: "yes"
                    onClicked: toPreview()
                }
            }
            // 控制项
            Column {
                visible: !isEncrypted || isAuthenticate
                // ===== 页数 =====
                Text_ {
                    text: qsTr("预览页面")
                }
                Row {
                    spacing: size_.spacing
                    height: size_.line + size_.spacing * 2
                    Button_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        text_: "<"
                        onClicked: changePage(0, -1)
                    }
                    Button_ {
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        text_: ">"
                        onClicked: changePage(0, 1)
                    }
                    Rectangle {
                        width: size_.line * 3
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        color: theme.bgColor
                        TextInput_ {
                            clip: true
                            anchors.fill: parent
                            bgColor: "#00000000"
                            text: previewPage
                            onTextChanged: changePage(text)
                        }
                    }
                    Text_ {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "/ "+pageCount
                    }
                }
                // ===== OCR范围 =====
                Text_ {
                    text: qsTr("OCR范围")
                }
                Row {
                    height: size_.line + size_.spacing * 2
                    Rectangle {
                        width: size_.line * 3
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        color: theme.bgColor
                        TextInput_ {
                            clip: true
                            anchors.fill: parent
                            bgColor: "#00000000"
                            text: rangeStart
                            onTextChanged: rangeStart = text
                        }
                    }
                    Text_ {
                        anchors.verticalCenter: parent.verticalCenter
                        text: " - "
                    }
                    Rectangle {
                        width: size_.line * 3
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        color: theme.bgColor
                        TextInput_ {
                            clip: true
                            anchors.fill: parent
                            bgColor: "#00000000"
                            text: rangeEnd
                            onTextChanged: rangeEnd = text
                        }
                    }
                }
            }
        }
    }

    // 右：忽略区域
    Item {
        id: ignoreAreaItem
    }

    contentItem: DoubleRowLayout {
        anchors.fill: parent
        initSplitterX: size_.line * 13
        // 左：控制面板
        leftItem: Panel {
            anchors.fill: parent
            TabPanel {
                id: tabPanel
                anchors.fill: parent
                anchors.margins: size_.spacing
                tabsModel: [
                    {
                        "key": "fileInfo",
                        "title": qsTr("文档属性"),
                        "component": fileInfoItem,
                    },
                    {
                        "key": "ignoreArea",
                        "title": qsTr("忽略区域"),
                        "component": ignoreAreaItem,
                    },
                ]
            }
        }
        // 右：图片查看面板
        rightItem: ImageScale {
            id: imgViewer
            anchors.fill: parent
        }
    }
}
