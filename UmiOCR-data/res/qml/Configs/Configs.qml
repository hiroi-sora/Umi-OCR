// ============================================
// =============== 参数配置 逻辑 ===============
// ============================================

/*
定义规则：

configDict: {

    "配置项组": {
        "title": 显示名称，可选，填写时自动生成控件,
        "group": true,
        "配置项或配置项组": ……
    },

    "常规配置项": {
        "title": 显示名称，可选，填写时自动生成控件,
        "default": 默认值，支持string，number，bool,
    },

}

configDict为嵌套形式，而originDict与valueDict为展开形式的单层字典。例：
    configDict["aaa"]["bbb"]["ccc"] === originDict["aaa.bbb.ccc"]
    configDict["aaa"]["bbb"]["ccc"]的当前取值 === valueDict["aaa.bbb.ccc"]
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import "../Widgets"

Item {
    property string category_: "" // 配置名
    property var configDict: { } // 定义字典，静态参数
    property alias panelComponent: panelComponent // 自动生成的组件

    property var originDict: { } // 键字典，键为展开形式，值指向configDict的项
    property var valueDict: { } // 值字典，动态变化

    // 初始化数值
    function initConfigDict() {
        if(originDict!==undefined){
            console.error("【Error】重复初始化配置"+category_+"！")
            return
        }
        originDict = {}
        valueDict = {}
        function handleConfigItem(config, key) { // 处理一个配置项
            originDict[key] = config // configDict项的引用绑定到originDict
            // 从配置文件中取值
            let val = settings.value(key, undefined)
            if(val === undefined) {
                val = config.default // 取默认值
                settings.setValue(key, val) // 存储
            }
            config.fullKey = key // 记录完整key
            valueDict[key] = val // 设当前值
        }
        function handleConfigGroup(group, prefix="") { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object"){
                    continue
                }
                if(!config.hasOwnProperty("title")) { // 补充空白标题
                    config.title = ""
                }
                if(config.hasOwnProperty("group")) { // 若是配置项组，递归遍历
                    handleConfigGroup(config, prefix+key+".") // 前缀加深一层
                }
                else { // 若是配置项
                    config.group = false
                    handleConfigItem(config, prefix+key)
                }
            }
        }
        handleConfigGroup(configDict)
        // console.log(`配置${category_}: `,JSON.stringify(originDict, null, 4))
        console.log(`配置${category_}: `,JSON.stringify(valueDict, null, 4))
    }

    // 存储
    Settings_ {
        id: settings
        category: category_ // 自定义类别名称
    }
    // 初始化
    Component.onCompleted: { 
        initConfigDict() 
        getCinfigsComponent()
    }
    
    // ========================= 【自动生成组件】 =========================

    // 初始化 自动生成组件
    function getCinfigsComponent() {

        function handleConfigItem(config) { // 处理一个配置项
            console.log("生成项", config.fullKey)
        }
        function handleConfigGroup(group, parent=panelContainer) { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object"){
                    continue
                }
                if(config.group) { // 若是配置项组，递归遍历
                    console.log("生成配置项组", key)
                    // 若是外层，则生成外层group组件；若是内层则生成内层组件。
                    const c = parent===panelContainer ? compGroup : compGroupInner
                    const p = c.createObject(parent, {"title":config.title})
                    const par = p.container // 下一层的父级
                    handleConfigGroup(config, parent=par) // 递归下一层
                    console.log("结束配置项组", key)
                }
                else { // 若是配置项
                    handleConfigItem(config)
                }
            }
        }
        handleConfigGroup(configDict)
    }

    // 总体 滚动视图
    ScrollView {
        id: panelComponent
        anchors.fill: parent
        contentWidth: width // 内容宽度
        clip: true // 溢出隐藏

        Column {
            id: panelContainer
            anchors.fill: parent
            spacing: theme.spacing
        }
    }
    // 配置项组（外层）
    Component {
        id: compGroup

        Item {
            property string title: "" // 标题
            property alias container: panelContainer // 容器
            anchors.left: parent.left
            anchors.right: parent.right
            height: childrenRect.height

            Text_ {
                id: groupText
                text: title
                anchors.left: parent.left
            }
            
            Rectangle {
                id: groupRectangle
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: groupText.bottom
                anchors.topMargin: theme.smallSpacing
                color: theme.bgColor
                radius: theme.panelRadius
                height: childrenRect.height
                
                Column {
                    id: panelContainer
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: theme.smallSpacing
                    spacing: theme.smallSpacing
                }
            }
        }
    }
    // 配置项组（内层）
    Component {
        id: compGroupInner

        Item {
            property string title: "" // 标题
            property alias container: panelContainer // 容器
            anchors.left: parent.left
            anchors.right: parent.right
            height: childrenRect.height

            Text_ {
                id: groupText
                text: title
                anchors.left: parent.left
            }
            
            Column {
                id: panelContainer
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: groupText.bottom
                anchors.topMargin: theme.smallSpacing
                anchors.leftMargin: theme.textSize // 子项右偏移
                spacing: theme.smallSpacing
            }
        }
    }

}