// ============================================
// =============== 参数配置 逻辑 ===============
// ============================================

/*
定义规则：

configDict: {

    "配置项组": {
        "title": 显示名称，可选，填写时自动生成控件,
        "type": "group",
        "配置项或配置项组"
    },

    "布尔 boolean （开关）": {
        "title": ,
        "default": true / false,
    },
    "枚举 enum （下拉框）": {
        "title": ,
        "optionsList": [
            ["键1", "名称1"],
            ["键2", "名称2"],
        ],
    },
    "文件路径 file （文件选择框）": {
        "title": ,
        "type": "file",
        "selectExisting": true 选择现有文件 / false 新创建文件(夹),
        "selectFolder": true 选择文件夹 / false 选择文件,
        "dialogTitle": 对话框标题,
        "nameFilters": ["图片 (*.jpg *.jpeg)", "类型2..."] 文件夹类型可不需要
    },

}

configDict为嵌套形式，而originDict与valueDict为展开形式的单层字典。例：
    configDict["aaa"]["bbb"]["ccc"] === originDict["aaa.bbb.ccc"]
    configDict["aaa"]["bbb"]["ccc"]的当前取值 === valueDict["aaa.bbb.ccc"]
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3 // 文件对话框
import "../Widgets"

Item {
    id: configs
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
            // 类型判断
            if (typeof config.default === "boolean") { // 布尔
                config.type = "boolean"
            }
            else if (config.hasOwnProperty("optionsList")) { // 枚举
                config.type = "enum"
                config.default = config.optionsList[0][0]
            }
            else if (config.hasOwnProperty("type")) {
                if(config.type === "file") { // 文件选择
                    config.default = ""
                    if(! config.hasOwnProperty("nameFilters")) {
                        config.nameFilters = []
                    }
                }
            }
            else {
                console.error("【Error】未知类型的配置项："+key)
                return
            }
            let flag = false
            // 从配置文件中取值
            let val = settings.value(key, undefined)
            // 检查和格式化存储值类型
            if(val !== undefined) { 
                switch(config.type) {
                    case "boolean": // 布尔，记录参数字符串转布尔值
                        val = val=="true"
                        flag = true
                        break
                    case "enum": // 枚举，检查记录参数是否在列表内
                        for(let i in config.optionsList) {
                            if(config.optionsList[i][0] == val) {
                                flag = true
                                break
                            }
                        }
                        break
                    case "file": // 文件
                        // 无需检查
                        flag = true
                        break
                }
            }
            if(!flag) { // 未有存储项或类型检查不合格，则取默认值
                val = config.default
                setValue(key, val) // 存储
                console.log(`${key}  取默认值 ${val}`)
            }
            originDict[key] = config // configDict项的引用绑定到originDict
            config.fullKey = key // 记录完整key
            valueDict[key] = val // 设当前值
        }
        function handleConfigGroup(group, prefix="") { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object"){
                    continue
                }
                // 补充空白参数
                if(!config.hasOwnProperty("title")) // 标题
                    config.title = ""
                if(!config.hasOwnProperty("type")) // 类型
                    config.type = ""
                // 若是配置项组，递归遍历
                if(config.type==="group") { 
                    config.fullKey = prefix+key // 记录完整key
                    handleConfigGroup(config, prefix+key+".") // 前缀加深一层
                }
                else { // 若是配置项
                    handleConfigItem(config, prefix+key)
                }
            }
        }
        handleConfigGroup(configDict)
        // console.log(`配置${category_}: `,JSON.stringify(originDict, null, 4))
        console.log(`配置${category_}: `,JSON.stringify(valueDict, null, 4))
    }

    // 获取值，设置值
    function getValue(key) {
        return valueDict[key]
    }
    function setValue(key, value) {
        if(valueDict[key] === value) // 排除相同值
            return
        valueDict[key] = value
        saveValue(key)
    }
    // 带缓存的存储值
    property var cacheDict: {} // 缓存
    property int cacheInterval: 500 // 缓存写入本地时间
    function saveValue(key) {
        cacheDict[key] = valueDict[key]
        cacheTimer.restart()
    }
    // 保存计时器
    Timer {
        id: "cacheTimer"
        running: false
        interval: cacheInterval
        onTriggered: {
            for(let k in cacheDict) {
                settings.setValue(k, cacheDict[k]) // 缓存写入本地
            }
            cacheDict = {} // 清空缓存
        }
    }

    // 存储
    Settings_ {
        id: settings
        category: category_ // 自定义类别名称
    }
    // 初始化
    Component.onCompleted: { 
        cacheDict = {}
        initConfigDict() 
        getCinfigsComponent()
    }
    
    // ========================= 【自动生成组件】 =========================

    // 初始化 自动生成组件
    function getCinfigsComponent() {

        function handleConfigItem(config, parent) { // 处理一个配置项
            if(componentDict.hasOwnProperty(config.type)) {
                const comp = componentDict[config.type]
                comp.createObject(parent, {"key":config.fullKey, "configs": configs})
            }
        }
        function handleConfigGroup(group, parent=panelContainer) { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object")
                    continue
                if(!config.title) // 无标题，则表示不生成组件
                    continue
                if(config.type === "group") { // 若是配置项组，递归遍历
                    // 若是外层，则生成外层group组件；若是内层则生成内层组件。
                    const c = parent===panelContainer ? compGroup : compGroupInner
                    const p = c.createObject(parent, {"title":config.title})
                    const par = p.container // 下一层的父级
                    handleConfigGroup(config, par) // 递归下一层
                }
                else { // 若是配置项
                    handleConfigItem(config, parent)
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
                height: childrenRect.height + theme.smallSpacing
                
                Column {
                    id: panelContainer
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: theme.smallSpacing
                    spacing: theme.smallSpacing
                }

                Item { // 底部占位
                    anchors.top: panelContainer.bottom
                    height: theme.smallSpacing
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
                anchors.leftMargin: theme.smallSpacing
            }
            // 背景
            MouseAreaBackgroud { }
            // 内容
            Column {
                id: panelContainer
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: groupText.bottom
                anchors.leftMargin: theme.textSize*1.5 // 子项右偏移
            }
        }
    }
    // ========== 生成组件字典 ========== 
    property var componentDict: {
        "boolean": compBoolean,
        "enum": compEnum,
        "file": compFile,
    }
    // 配置项：布尔值
    Component {
        id: compBoolean

        ConfigItemComp {
            property bool checked: true
            property bool isInit: false

            // 初始化
            Component.onCompleted: {
                checked = value()
                isInit = true // 初始化完毕，允许启用动画
            }

            // 按下
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    checked = !checked
                    value(checked)
                }
            }

            // 开关图标
            Rectangle {
                id: switchBtn
                anchors.right: parent.right
                anchors.rightMargin: theme.smallSpacing
                anchors.verticalCenter: parent.verticalCenter
                height: theme.textSize
                width: theme.textSize*2
                clip: true
                color: theme.bgColor
                radius: theme.btnRadius
                border.width: 2
                border.color: theme.coverColor4

                // 关闭：×
                Icon_ {
                    anchors.fill: parent
                    anchors.margins: 3
                    icon: "close"
                    color: theme.noColor
                }

                // 启用：√
                Rectangle {
                    id: enableIcon
                    x: checked ? 0 : width*-1.1
                    height: parent.height
                    width: parent.width
                    color: theme.yesColor
                    radius: theme.btnRadius
                    Icon_ {
                        anchors.fill: parent
                        icon: "check"
                        color: theme.bgColor
                    }
                    Behavior on x { // 位移动画
                        enabled: theme.enabledEffect && isInit
                        NumberAnimation {
                            duration: 200
                            easing.type: Easing.OutCirc
                        }
                    }
                }

            }
        }
    }
    // 配置项：枚举
    Component {
        id: compEnum

        ConfigItemComp {

            property var optionsList: [] // 候选列表原型
            // 初始化
            Component.onCompleted: {
                optionsList = origin.optionsList
                let model = []
                let index = 0
                const v = value()
                for(let i=0, l=optionsList.length; i<l; i++) {
                    const opt = optionsList[i]
                    model.push(opt[1]) // 显示标题
                    if(v==opt[0]) {
                        index = i
                    }
                }
                comboBox.model = model
                comboBox.currentIndex = index
            }
            // 更新数值
            function set() {
                const curr = optionsList[comboBox.currentIndex][0]
                value(curr)
            }

            ComboBox {
                id: comboBox
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.margins: 1
                width: parent.width*0.5
                model: []
                onCurrentIndexChanged: set() // 数值刷新

                // 前景文字
                contentItem: Text {
                    text: parent.currentText
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: theme.smallSpacing
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: theme.textSize
                    font.family: theme.fontFamily
                    color: theme.subTextColor
                }
                // 前景箭头
                indicator: Icon_ {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.margins: theme.smallSpacing
                    height: theme.smallTextSize
                    icon: "down"
                    color: theme.subTextColor
                }
                // 背景
                background: Rectangle {
                    anchors.fill: parent
                    color: "#00000000"
                    border.width: 2
                    border.color: theme.coverColor2
                    radius: theme.btnRadius
                    
                    // 背景
                    MouseAreaBackgroud {
                        cursorShape: Qt.PointingHandCursor
                    }
                }
                // 选项
                delegate: ItemDelegate {
                    width: parent.width
                    height: theme.textSize + theme.smallSpacing
                    Text {
                        text: modelData
                        anchors.left: parent.left
                        anchors.leftMargin: theme.smallSpacing
                        font.pixelSize: theme.textSize
                        font.family: theme.fontFamily
                        color: theme.subTextColor
                    }
                    MouseAreaBackgroud {
                        radius_: 0
                        onClicked: parent.clicked()
                    }
                }
            }
        }
    }
    // 配置项：文件选择
    Component {
        id: compFile

        ConfigItemComp {
            id: rootFile
            // 初始化
            Component.onCompleted: {
                textInput.text = value()
            }
            // 导入路径
            function set(path) {
                value(path) // 设置值
            }

            Item {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.margins: 1
                width: parent.width*0.5

                // 选择按钮
                IconButton {
                    id: iconButton
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: height
                    icon_: "folder"
                    onClicked: fileDialog.open()

                    FileDialog_ {
                        id: fileDialog
                        title: origin.dialogTitle
                        selectExisting: origin.selectExisting
                        selectFolder: origin.selectFolder
                        selectMultiple: false  // 始终禁止多选
                        nameFilters: origin.nameFilters
                        folder: shortcuts.desktop
                        onAccepted: {
                            if(fileDialog.fileUrls_.length > 0) {
                                // rootFile.set(fileDialog.fileUrls_[0])
                                textInput.text = fileDialog.fileUrls_[0] // 设置对话框文本
                            }
                        }
                    }
                }
                

                // 文本输入框
                Rectangle {
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: iconButton.left
                    anchors.rightMargin: 2
                    color: "#00000000"
                    border.width: 2
                    border.color: theme.coverColor2
                    radius: theme.btnRadius

                    TextInput_ {
                        id: textInput
                        clip: true
                        anchors.fill: parent
                        anchors.leftMargin: parent.border.width
                        anchors.rightMargin: parent.border.width
                        onTextChanged: { // 对话框文本改变时设置值
                            rootFile.set(text)
                        }
                    }
                }
            }
        }
    }
}