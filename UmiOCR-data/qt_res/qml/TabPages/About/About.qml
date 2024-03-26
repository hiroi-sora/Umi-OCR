// ===================================================
// =============== 功能页：关于/检查更新 ===============
// ===================================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import ".."
import "../../Widgets"

TabPage {
    id: tabPage

    Panel{
        anchors.fill: parent
        anchors.margins: size_.line

        ScrollView {
            anchors.fill: parent
            anchors.margins: size_.spacing
            anchors.leftMargin: size_.line * 2
            anchors.rightMargin: size_.line * 2
            contentWidth: width
            clip: true

            Column {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: size_.spacing

                // ==================== 标题 ====================

                Image {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: size_.line * 10
                    fillMode: Image.PreserveAspectFit
                    source: "../../../images/Umi-OCR_logo_full.png"
                }
                Text_ {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: qsTr("开源、免费的离线OCR软件")
                }
                SplitLine {}

                // ==================== 软件 / 项目信息 ====================

                Text_ {text: qsTr("当前版本") + "   •   " + UmiAbout.version.string}
                UrlList {
                    title: qsTr("项目链接")
                    urlList: [
                        {text:qsTr("官方网站"), url:UmiAbout.url.home},
                        {text:qsTr("插件拓展"), url:UmiAbout.url.plugins},
                        {text:qsTr("问题反馈"), url:UmiAbout.url.issue},
                    ]
                }
                UrlList {
                    title: qsTr("发布地址")
                    urlList: [
                        {text:"Github", url:"https://github.com/hiroi-sora/Umi-OCR/releases/latest"},
                        {text:"Source Forge", url:"https://sourceforge.net/projects/umi-ocr"},
                        {text:"Lanzou (蓝奏云)", url:"https://hiroi-sora.lanzoul.com/s/umi-ocr"},
                    ]
                }
                UrlList {
                    title: qsTr("许可协议")
                    urlList: [
                        {text:UmiAbout.license.type, url:UmiAbout.license.url},
                    ]
                }
                SplitLine {}

                // ==================== 开发者 ====================

                UrlList {
                    title: qsTr("作者")
                    urlList: (() => {
                        let as = UmiAbout.authors, t = []
                        for(const i in as)
                            t.push({ text: as[i].name, url: as[i].url, })
                        return t
                    })()
                }
                Text_ {text: qsTr("译者")}
                Repeater {
                    model: UmiAbout.localization

                    UrlList {
                        anchors.leftMargin: size_.line * 2
                        textSize: size_.smallText
                        title: UmiAbout.localization[index].language
                        urlList: (() => {
                            let as = UmiAbout.localization[index].translators, t = []
                            for(const i in as)
                                t.push({ text: as[i].name, url: as[i].url, })
                            return t
                        })()
                    }
                }
                SplitLine {}

                // ==================== 系统 / Debug信息 ====================

                Row {
                    anchors.left: parent.left
                    Text_ {
                        font.pixelSize: size_.smallText
                        height: size_.smallLine + size_.spacing*2
                        verticalAlignment: Text.AlignVCenter
                        text: qsTr("运行环境信息（如需请求协助，请提供给开发者）")
                    }
                    Button_ {
                        height: size_.smallLine + size_.spacing*2
                        textSize: size_.smallText
                        text_: qsTr("复制")
                        textColor_: theme.yesColor
                        onClicked: {
                            const info = JSON.stringify(UmiAbout.app, null, 2)
                            qmlapp.utilsConnector.copyText(info)
                        }
                    }
                }
                Text_ {
                    anchors.left: parent.left
                    anchors.leftMargin: size_.line * 2
                    wrapMode: Text.WordWrap
                    font.pixelSize: size_.smallText
                    text: JSON.stringify(UmiAbout.app, null, 2)
                }

                Item {width: 1; height: size_.line}
            }
        }
    }
}