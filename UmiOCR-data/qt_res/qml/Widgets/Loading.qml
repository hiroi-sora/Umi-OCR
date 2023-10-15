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

    // 主体
    Panel {
        anchors.fill: parent
        
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
                property real p1w
                property real p1h
                property real p2x
                property real p2y
                property real p2w
                property real p2h
                property real pt: lRoot.time * 0.5
                property bool running: false
                Component.onCompleted: {
                    // 父组件大小
                    let pw=parent.width, ph=parent.height
                    // 图片原始大小
                    let sw=sourceSize.width, sh=sourceSize.height
                    if(qmlapp.enabledEffect) {
                        // 最高点
                        p1h=ph*0.9
                        p1w=p1h*(sw/sh)*0.9
                        p1y=0, p1x=(pw-p1w)*0.5
                        // 最低点
                        p2h=p1h*0.9
                        p2w=p1h*(sw/sh)*1.1
                        p2x=(pw-p2w)*0.5, p2y=ph-p2h
                        x=p2x
                        y=p2y
                        width=p2w
                        height=p2h
                        image.running = true
                    }
                    else {
                        height = ph
                        width = ph*(sw/sh)
                        y=0
                        x=(pw-width)*0.5
                    }
                }
                SequentialAnimation{ // 串行动画
                    id: animation
                    running: image.running && qmlapp.enabledEffect
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
                textTimer.running = true
            }
            Timer {
                id: textTimer
                property int now: 0
                property int max: 0
                interval: cRoot.time
                running: false
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
                        color: theme.textColor
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: size_.smallSpacing
                        height: size_.smallText
                        property real scaleMax: 1.4
                        property real opacityMin: 0.4
                        opacity: opacityMin
                        
                        onCharShowChanged: {
                            if(qmlapp.enabledEffect) {
                                if(charShow) caShow.running = true
                                else caHide.running = true
                            }
                            else {
                                color = charShow ? theme.textColor:theme.coverColor4
                                scale = charShow ? scaleMax : 1
                            }
                        }
                        ParallelAnimation {
                            id: caShow
                            running: false
                            OpacityAnimator { target:charT; from:opacityMin; to:1; easing.type:Easing.InQuart; duration:cRoot.time }
                            ScaleAnimator { target:charT; from:1; to:scaleMax; easing.type:Easing.InQuart; duration:cRoot.time}
                        }
                        ParallelAnimation {
                            id: caHide
                            running: false
                            OpacityAnimator { target:charT; from:1; to:opacityMin; easing.type:Easing.InQuart; duration:cRoot.time }
                            ScaleAnimator { target:charT; from:scaleMax; to:1; easing.type:Easing.InQuart; duration:cRoot.time}
                        }
                    }
                }
            }
        }
    }
}