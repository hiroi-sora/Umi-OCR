// ==============================================
// =============== 加载中 动态图标 ===============
// ==============================================

import QtQuick 2.15
import QtGraphicalEffects 1.15 // 阴影

Item {
    id: lRoot
    property string text: "OCR..."
    property real time: 700 // 动画间隔时间，毫秒
    width: size_.smallText * 6
    height: width
    clip: true
    property bool running: false // 是否运行动画

    onVisibleChanged: {
        if(visible) {
            image.init()
            cRoot.init()
            running = qmlapp.enabledEffect // 启动动画
        }
        else {
            running = false // 停止动画
        }
    }

    // 主体
    Panel {
        anchors.fill: parent
        color: theme.bgColor
        
        // 图标
        Item {
            anchors.fill: parent
            anchors.margins: size_.spacing * 2
            anchors.topMargin: size_.spacing
            Image {
                id: image
                source: "../../images/icons/dango_right.png"
                mipmap: true // 启用高质量缩放
                fillMode: Image.Stretch
                property real p1x
                property real p1y
                property real pw
                property real ph
                property real sw
                property real sh
                property real p1w
                property real p1h
                property real p2x
                property real p2y
                property real p2w
                property real p2h
                property real pt: lRoot.time * 0.5
                // 预计算变形动画参数
                Component.onCompleted: {
                    // 父组件大小
                    pw=parent.width, ph=parent.height
                    // 图片原始大小
                    sw=sourceSize.width, sh=sourceSize.height
                    // 最高点
                    p1h=ph*0.9, p1w=p1h*(sw/sh)*0.9, p1y=0, p1x=(pw-p1w)*0.5
                    // 最低点
                    p2h=p1h*0.9, p2w=p1h*(sw/sh)*1.1, p2x=(pw-p2w)*0.5, p2y=ph-p2h
                }
                // 恢复初始状态
                function init() {
                    if(qmlapp.enabledEffect) {
                        x=p2x, y=p2y
                        width=p2w, height=p2h
                    }
                    else {
                        height=ph, width=ph*(sw/sh)
                        y=0, x=(pw-width)*0.5
                    }
                }
                // 串行动画
                SequentialAnimation{
                    id: animation
                    running: lRoot.running
                    loops: Animation.Infinite
                    ParallelAnimation {
                        NumberAnimation{ target:image; property:"x"; to:image.p1x; duration:image.pt; easing.type:Easing.OutCubic}
                        NumberAnimation{ target:image; property:"y"; to:image.p1y; duration:image.pt; easing.type:Easing.OutCubic}
                        NumberAnimation{ target:image; property:"width"; to:image.p1w; duration:image.pt; easing.type:Easing.OutCubic}
                        NumberAnimation{ target:image; property:"height"; to:image.p1h; duration:image.pt; easing.type:Easing.OutCubic}
                    }
                    ParallelAnimation {
                        NumberAnimation{ target:image; property:"x"; to:image.p2x; duration:image.pt; easing.type:Easing.InCubic}
                        NumberAnimation{ target:image; property:"y"; to:image.p2y; duration:image.pt; easing.type:Easing.InCubic}
                        NumberAnimation{ target:image; property:"width"; to:image.p2w; duration:image.pt; easing.type:Easing.InCubic}
                        NumberAnimation{ target:image; property:"height"; to:image.p2h; duration:image.pt; easing.type:Easing.InCubic}
                    }
                }
            }
        }

        // 下方文字动画
        Item {
            id: cRoot
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            // anchors.margins: size_.smallSpacing
            height: size_.smallText
            property var chars: []
            property int time: lRoot.time
            
            Component.onCompleted: {
                let l = []
                for(let i in lRoot.text)
                    l.push(lRoot.text[i])
                chars = l
                textTimer.max = l.length
            }
            // 恢复初始状态
            function init() {
                textTimer.now = 0
            }
            Timer {
                id: textTimer
                property int now: 0
                property int max: 0
                interval: cRoot.time
                running: lRoot.visible
                repeat: true
                onTriggered: {
                    if(now===max-1)
                        now = 0
                    else
                        now++
                }
            }

            Row {
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: size_.smallText * 0.1
                
                Repeater {
                    model: cRoot.chars
                    Text_ {
                        id: charT
                        property bool charShow: textTimer.now===index
                        font.pixelSize: size_.smallText
                        text: modelData
                        color: theme.specialTextColor
                        property real minOpa: 0.5
                        opacity: minOpa
                        property real sp: size_.smallSpacing
                        property real spMax: size_.smallSpacing * 1.5
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: sp
                        height: size_.smallText

                        onCharShowChanged: {
                            if(lRoot.running) {
                                if(charShow) caShow.running = true
                                else caHide.running = true
                            }
                            else {
                                anchors.bottomMargin = charShow ? spMax : sp
                                opacity = charShow ? 1 : minOpa
                            }
                        }
                        ParallelAnimation {
                            id: caShow
                            running: false
                            NumberAnimation {
                                target:charT; properties: "anchors.bottomMargin";
                                from: charT.sp; to: charT.spMax; duration:cRoot.time * 0.5;
                                easing.type:Easing.OutCubic;
                            }
                            NumberAnimation {
                                target:charT; properties: "opacity";
                                from: minOpa; to: 1; duration:cRoot.time * 0.5;
                                easing.type:Easing.OutCubic;
                            }
                        }
                        ParallelAnimation {
                            id: caHide
                            running: false
                            NumberAnimation {
                                target:charT; properties: "anchors.bottomMargin";
                                from: charT.spMax; to: charT.sp;
                                easing.type:Easing.InQuart; duration:cRoot.time;
                            }
                            NumberAnimation {
                                target:charT; properties: "opacity";
                                from: 1; to: minOpa; duration:cRoot.time;
                                easing.type:Easing.InQuart;
                            }
                        }
                    }
                }
            }
        }
    }
}