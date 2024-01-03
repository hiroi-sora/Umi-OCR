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
    property bool running: false
    property string previewPath: ""
    property int previewPage: 1

    // 展示文档
    // info: path, range_start, range_end
    function show(info) {
        visible = true
        previewPage = info.range_start
        previewPath = info.path
        toPreview()
    }

    // 预览一页文档
    function toPreview() {
        running = true
        prevConn.preview(previewPath, previewPage)
    }
    // 预览连接器
    DocPreviewConnector {
        id: prevConn
        // 图片渲染的回调
        onPreviewImg: function(imgID) {
            console.log("==", imgID)
            imgViewer.showImgID(imgID)
        }
    }

    contentItem: DoubleRowLayout {
        anchors.fill: parent
        initSplitterX: size_.line * 13
        // 左：控制面板
        leftItem: Panel {
            anchors.fill: parent
            // TabPanel {
            //     id: tabPanel
            //     anchors.fill: parent
            //     anchors.margins: size_.spacing
            //     tabsModel: [
            //         {
            //             "key": "configs",
            //             "title": qsTr("文档属性"),
            //             "component": undefined,
            //         },
            //         {
            //             "key": "ignoreArea",
            //             "title": qsTr("忽略区域"),
            //             "component": undefined,
            //         },
            //     ]
            // }
        }
        // 右：图片查看面板
        rightItem: Panel {
            anchors.fill: parent
            ImageScale {
                id: imgViewer
                anchors.fill: parent
            }
        }
    }
}
