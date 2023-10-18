// ==========================================================
// =============== 可显示OCR文本的增强Image组件 ===============
// ==========================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import ".."

Image_ {

    // 设置图片源，展示一张图片（覆盖父类方法）
    function setSource(source) {
        textBoxes = [] // 清空旧文本块
        if(source) {
            // 特殊字符#替换为%23
            if(source.startsWith("file:///") && source.includes("#"))
                source = source.replace(new RegExp("#", "g"), "%23");
            showImage.source = source // 设置源
        }
    }

    // 展示图片及 OCR文本块
    function setSourceResult(source, res) {
        setSource(source)
        // 提取文本框
        textBoxes = []
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
                }
                tbs.push(info)
            }
            textBoxes = tbs
        }
    }

    property var textBoxes: [] // 文本块列表

    // 文本块叠加层
    overlayLayer: Item {
        anchors.fill: parent

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
                    modelData.width = width // 记录修改后的组件大小
                    modelData.height = height
                }
            }
        }
    }
}