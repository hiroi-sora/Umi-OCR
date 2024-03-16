// ================================================
// =============== 导航页（新标签页） ===============
// ================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import ".."
import "../.."
import "../../Widgets"

TabPage {

    // =============== 逻辑 ===============

    id: naviPage
    
    ListModel { id: pageModel } // 页面信息存储

    // 初始化数据
    Component.onCompleted: initData()
    function initData() {
        pageModel.clear()
        const f = qmlapp.tab.infoList
        // 遍历所有文件信息（排除第一项自己）
        for(let i=1,c=f.length; i<c; i++){
            pageModel.append({
                "title": f[i].title,
                "intro": f[i].intro,
                "infoIndex": i,
            })
        }
    }
    // 动态变化的简介文本
    property string introText: `# ${qsTr("欢迎使用 Umi-OCR")}

## 👈 ${qsTr("请选择功能页")}
`


    // =============== 布局 ===============

    DoubleRowLayout {
        anchors.fill: parent
        initSplitterX: size_.line * 15
        
        // =============== 左侧，展示所有标签页名称 ===============
        leftItem: Panel{
            anchors.fill: parent

            ScrollView {
                id: scrollView
                anchors.fill: parent
                anchors.margins: size_.spacing
                clip: true

                Column {
                    anchors.fill: parent
                    spacing: size_.spacing * 0.5

                    Text {
                        text: qsTr("功能页")
                        width: scrollView.width
                        height: size_.line * 2.5
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        color: theme.subTextColor
                        font.pixelSize: size_.text
                        font.family: theme.fontFamily
                    }

                    Repeater {
                        model: pageModel
                        Button_ {
                            text_: title
                            width: scrollView.width
                            height: size_.line * 2.5

                            onHoveredChanged: {
                                naviPage.introText = intro
                            }
                            onClicked: {
                                let i = qmlapp.tab.getTabPageIndex(naviPage)
                                if(i < 0){
                                    console.error("【Error】导航页"+text+"未找到下标！")
                                }
                                qmlapp.tab.changeTabPage(i, infoIndex)
                            }
                        }
                    }
                }
            }
        }

        // =============== 右侧，展示功能简介 ===============
        rightItem: Panel{
            anchors.fill: parent
            
            MarkdownView {
                id: introView
                anchors.fill: parent
                anchors.margins: size_.spacing * 2
                text: introText
            }
        }
    }
}