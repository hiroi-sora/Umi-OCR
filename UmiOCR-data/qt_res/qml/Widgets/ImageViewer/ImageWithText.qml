// ==========================================================
// =============== 可显示OCR文本的增强Image组件 ===============
// ==========================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import ".."

ImageScale {
    id: iRoot
    property bool showOverlay: true // 显示叠加层

    Component.onCompleted: {
        // 默认显示/关闭叠加层
        showOverlay = qmlapp.globalConfigs.getValue("ui.imgShowOverlay")
    }

    beforeShow: () => {
        mouseArea.initIndex() // 清空选字参数
        textBoxes = [] // 清空旧文本块
    }

    // 展示文本块
    function showTextBoxes(res) {
        beforeShow()
        // 提取文本框
        if(res.code == 100 && res.data.length > 0) {
            let tbs = []
            for(let i in res.data) {
                const d = res.data[i]
                const info = {
                    x: d.box[0][0],
                    y: d.box[0][1],
                    width: d.box[2][0] - d.box[0][0],
                    height: d.box[2][1] - d.box[0][1],
                    text: d.text,
                    end: d.end || "", // 行尾间隔符
                }
                tbs.push(info)
            }
            textBoxes = tbs
        }
    }

    // 弹出菜单
    function popupMenu() {
        selectMenu.popup()
    }
    // 显示/隐藏叠加层
    function switchOverlay() {
        showOverlay = !showOverlay
        if(!showOverlay)
            mouseArea.cursorShape = Qt.OpenHandCursor
    }

    property var textBoxes: [] // 文本块列表

    // 文本块叠加层
    overlayLayer: Item {
        id: oRoot
        anchors.fill: parent
        visible: showOverlay

        Repeater {
            id: textBoxRepeater
            model: textBoxes
            TextBox {
                text: modelData.text
                x: modelData.x
                y: modelData.y

                Component.onCompleted: {
                    width = modelData.width
                    height = modelData.height
                    resetSize() // 自适应字体和组件大小
                    textBoxes[index].width = width // 记录修改后的组件大小
                    textBoxes[index].height = height
                    textBoxes[index].obj = this
                }
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        property int startIndex: -1 // 拖拽开始时，文本框序号
        property int startTextIndex: -1 // 拖拽开始时，字符序号
        property int endIndex: -1 // 拖拽结束时，文本框序号
        property int endTextIndex: -1 // 拖拽结束时，字符序号
        property int selectUpdate: 0
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        // 清除index
        function initIndex() {
            startIndex = startTextIndex = endIndex = endTextIndex = -1
        }
        // 检测当前鼠标点，位于哪一个tb内
        function mouseInTextBox() {
            const localPoint = oRoot.mapFromItem(mouseArea, mouseX, mouseY)
            const x = localPoint.x, y = localPoint.y
            for (let i=0,l=textBoxes.length; i<l; i++) {
                const rect = textBoxes[i]
                if (x >= rect.x && x <= rect.x + rect.width &&
                    y >= rect.y && y <= rect.y + rect.height) {
                    return i
                }
            }
            return -1
        }
        // 检测当前鼠标点，在index tb内的哪一个字符处
        function mouseInTextIndex(index) {
            return textBoxes[index].obj.where(mouseArea, mouseX, mouseY)
        }
        // 获取Index正确顺序
        function getIndexes() {
            let li, lt, ri, rt
            if(startIndex < endIndex) {
                li=startIndex; lt=startTextIndex; ri=endIndex; rt=endTextIndex;
            }
            else if(startIndex > endIndex) {
                li=endIndex; lt=endTextIndex; ri=startIndex; rt=startTextIndex;
            }
            else {
                li=ri=startIndex
                if(startTextIndex < endTextIndex) {
                    lt=startTextIndex; rt=endTextIndex;
                }
                else if(startTextIndex > endTextIndex) {
                    lt=endTextIndex; rt=startTextIndex;
                }
                else { // 单击，未选中
                    li = ri = startIndex
                    lt = rt = -1
                }
            }
            return [li, lt, ri, rt]
        }
        // 根据 Index 的参数，选择对应文本。
        function selectIndex() {
            const [li, lt, ri, rt] = getIndexes()
            // 遍历每个文本框数据
            for (let i = 0, l=textBoxes.length; i < l; i++) {
                const tEdit = textBoxes[i].obj.textEdit
                if( li<0 || ri<0 || i<li || i>ri ) { // 未被选中
                    tEdit.deselect()
                }
                else if(i === li && i === ri) { // 单个块
                    if(lt === rt) // 无有效选中
                        tEdit.deselect()
                    else
                        tEdit.select(lt, rt)
                }
                else if(i === li) { // 多个块的起始
                    const len = textBoxes[i].text.length
                    tEdit.select(lt, len)
                }
                else if(i === ri) { // 多个块的结束
                    tEdit.select(0, rt)
                }
                else { // 多个块的中间
                    tEdit.selectAll(0, rt)
                }
            }
        }
        // 全选
        function selectAll() {
            const l = textBoxes.length
            if(l === 0) return
            startIndex = startTextIndex = 0
            endIndex = l-1
            endTextIndex = textBoxes[endIndex].text.length
            selectIndex()
        }
        // 复制已选中的内容
        function selectCopy() {
            // 没有有效选中，则复制全部
            if(startIndex<0 || endIndex<0 || 
                (startIndex==endIndex&&startTextIndex==endTextIndex)) {
                selectAllCopy()
                return
            }
            let [li, lt, ri, rt] = getIndexes()
            if(li >= 0 && ri >= 0) {
                let copyText = ""
                for(let i = li; i <= ri; i++) {
                    const text = textBoxes[i].text
                    const end = textBoxes[i].end
                    // 范围检查
                    const len = text.length
                    if (lt < 0) lt = 0
                    if (lt > len) lt = len
                    if (rt < lt) rt = lt
                    if (rt > len) rt = len
                    // 获取文本
                    if(i === li && i === ri) // 单个块
                        copyText = text.substring(lt, rt)
                    else if(i === li) // 多个块的起始
                        copyText = text.substring(lt)+end
                    else if(i === ri) // 多个块的结束
                        copyText += text.substring(0, rt)
                    else // 多个块的中间
                        copyText += text+end
                }
                if(copyText && copyText.length>0) {
                    qmlapp.utilsConnector.copyText(copyText)
                    qmlapp.popup.simple(qsTr("图片：复制%1字").arg(copyText.length), "")
                    return copyText
                }
            }
            qmlapp.popup.simple(qsTr("图片：无选中文字"), "")
            return ""
        }
        // 复制所有
        function selectAllCopy() {
            let copyText = ""
            for (let i = 0, l=textBoxes.length; i < l; i++) {
                copyText += textBoxes[i].text
                if(i < l-1) copyText += textBoxes[i].end
            }
            qmlapp.utilsConnector.copyText(copyText)
            qmlapp.popup.simple(qsTr("图片：复制全部%1字").arg(copyText.length), "")
            selectAll()
        }

        // 按下
        onPressed: {
            mouseArea.forceActiveFocus()
            if (mouse.button === Qt.RightButton) {
                selectMenu.popup()
                return
            }
            if(!showOverlay) {
                mouse.accepted = false
                return
            }
            initIndex()
            const tbi = mouseInTextBox()
            cursorShape = tbi < 0 ? Qt.ClosedHandCursor : Qt.IBeamCursor
            if(tbi >= 0) { // 选择文本
                startIndex = tbi
                startTextIndex = mouseInTextIndex(tbi)
            }
            else {
                mouse.accepted = false
            }
        }
        // 移动
        onPositionChanged: {
            if(!showOverlay) return
            const tbi = mouseInTextBox()
            if(pressed) { // 拖拽中
                if(tbi >= 0) { // 选择文本
                    endIndex = tbi
                    endTextIndex = mouseInTextIndex(tbi)
                    selectIndex()
                }
            }
            else { // 悬停中
                cursorShape = tbi < 0 ? Qt.OpenHandCursor : Qt.IBeamCursor
            }
        }
        // 抬起
        onReleased: {
            if(!showOverlay) return
            if (mouse.button === Qt.RightButton) return
            const tbi = mouseInTextBox()
            cursorShape = tbi < 0 ? Qt.OpenHandCursor : Qt.IBeamCursor
            if(startIndex === -1) return
            if(tbi >= 0) {
                endIndex = tbi
                endTextIndex = mouseInTextIndex(tbi)
            }
            selectIndex()
        }
        // 菜单
        Menu_ {
            id: selectMenu
            menuList: [
                [mouseArea.selectCopy, qsTr("复制　　（Ctrl+C）")],
                [mouseArea.selectAll, qsTr("全选　　（Ctrl+A）")],
                [iRoot.copyImage, qsTr("复制图片（Ctrl+X）")],
                [iRoot.saveImage, qsTr("保存图片（Ctrl+S）")],
                [iRoot.switchOverlay, qsTr("显示/隐藏文字（Tab）")],
            ]
        }
        // 按键事件
        Keys.onPressed: {
            if (event.modifiers & Qt.ControlModifier) {
                event.key===Qt.Key_A && selectAll()
                event.key===Qt.Key_C && selectCopy()
                event.key===Qt.Key_X && iRoot.copyImage()
                event.key===Qt.Key_S && iRoot.saveImage()
            }
            if (event.key === Qt.Key_Tab) {
                iRoot.switchOverlay()
                Qt.callLater(mouseArea.forceActiveFocus)
            }
        }
    }
}