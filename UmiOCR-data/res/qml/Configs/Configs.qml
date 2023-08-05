// ============================================
// =============== 参数配置 逻辑 ===============
// ============================================

/*
定义规则：

configDict: {

    "配置项组": {
        "title": 若填单个空格“ ”，则不显示标题栏
        "type": "group",
        "配置项或配置项组"
        // 折叠属性，仅内层组生效
        "enabledFold": 填true时显示折叠标签
        "fold": 填true时初始折叠
    },

    "布尔 boolean （开关）": {
        "title": ,
        "default": true / false,
    },
    "文本 text （文本框）": {
        "title": ,
        "default": "文本",
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
        "default": "默认路径",
        "selectExisting": true 选择现有文件 / false 新创建文件(夹),
        "selectFolder": true 选择文件夹 / false 选择文件,
        "dialogTitle": 对话框标题,
        "nameFilters": ["图片 (*.jpg *.jpeg)", "类型2..."] 文件夹类型可不需要
    },
    "按钮组 buttons": {
        "title": ,
        "btnsList": [
            {"text":"名称1", "onClicked":函数1, "textColor": 字体颜色}},
            {"text":"名称2", "onClicked":函数2, "bgColor": 背景颜色}},
        ],
    },

    通用配置元素：
    "title": 显示名称。不填（或undefined）时不生成组件。填写（包括空字符串""）时自动生成控件。
    "type": 控件类型,
    "save": 可选，填false时不保存（每次初始化为默认值）,
    "toolTip": 可选，字符串，鼠标悬停时的提示,
    "advanced": 可选，填true时为高级选项，平时隐藏
    "onChanged": 可选，值变化时的回调函数，  (newVal, oldVal)=>{console.log(`值从 ${oldVal} 变为 ${newVal}`)}
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

    // ========================= 【对外接口】 =========================

    property string category_: "" // 配置名
    property var configDict: { } // 定义字典，静态参数，key为嵌套
    property alias panelComponent: panelComponent // 自动生成的组件

    // 重置所有设置为默认值
    function reset() {
        for (let key in originDict) {
            setValue(key, originDict[key].default) // 刷新值
            if(compDict.hasOwnProperty(key)) { // 刷新UI
                compDict[key].updateUI()
            }
        }
    }
    // 重新从 configDict 加载设置项和UI
    function reload() {
        isChangedInit = false
        initConfigDict() 
        initPanelComponent()
        initChangedFuncs()
        console.log(`% 加载配置 ${category_} ！`)
        // console.log(`% 加载配置 ${category_} ！: ${JSON.stringify(valueDict, null, 2)}`)
    }
    // 获取配置值字典
    function getConfigValueDict() {
        return valueDict
    }
    
    // ========================= 【内部变量】 =========================

    // 配置存储字典，key为展开形式，三个字典key对应
    property var originDict: { } // 键字典，键为展开形式，值指向configDict的项
    property var valueDict: { } // 值字典，动态变化
    property var compDict: { } // 组件字典（不包括组）。可能不是所有配置项都有组件
    property var compList: [] // 保存所有组件（包括组）的列表，便于删除

    property var cacheDict: {} // 缓存
    property int cacheInterval: 500 // 缓存写入本地时间

    property bool enabledAdvanced: false // true时显示高级模式的按钮。只有任意设置项设了高级模式，此项才会被置true
    property bool advanced: false // true时进入高级模式

    // ========================= 【数值逻辑（内部调用）】 =========================

    // 初始化
    Component.onCompleted: { 
        reload()
    }
    // 初始化数值
    function initConfigDict() {
        originDict = {}
        valueDict = {}
        cacheDict = {}
        function handleConfigItem(config, key) { // 处理一个配置项
            // 类型：指定type
            if (config.type !== "") {
                if(config.type === "file") { // 文件选择
                    if(! config.hasOwnProperty("default"))
                        config.default = ""
                    if(! config.hasOwnProperty("nameFilters")) {
                        config.nameFilters = []
                    }
                }
            }
            // 类型判断：省略type
            else{
                if (typeof config.default === "boolean") { // 布尔
                    config.type = "boolean"
                }
                else if (typeof config.default === "string") { // 文本
                    config.type = "text"
                }
                else if (config.hasOwnProperty("optionsList")) { // 枚举
                    config.type = "enum"
                    config.default = config.optionsList[0][0]
                }
                else if (config.hasOwnProperty("btnsList")) { // 按钮组
                    config.type = "buttons"
                    config.fullKey = key // 记录完整key
                    return
                }
                else {
                    console.error("【Error】未知类型的配置项："+key)
                    return
                }
            }
            let flag = false
            // 从配置文件中取值
            let val = settings.value(key, undefined)
            // 检查和格式化存储值类型
            if(val !== undefined) { 
                switch(config.type) {
                    case "boolean": // 布尔，记录参数字符串转布尔值
                        if(typeof val === "string")
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
                    // 无需检查
                    case "file": // 文件
                    case "text": // 文本
                        flag = true
                        break
                }
            }
            if(!flag) { // 未有存储项或类型检查不合格，则取默认值
                val = config.default
                setValue(key, val) // 存储
                console.log(`${key} 取默认值 ${val}`)
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
                // 补充空白参数
                supplyDefaultParams(config)
                // 记录完整key
                const fullKey = prefix+key
                config.fullKey = fullKey
                originDict[fullKey] = config
                if(config.type==="group") { // 若是配置项组，递归遍历
                    handleConfigGroup(config, fullKey+".") // 前缀加深一层
                }
                else { // 若是配置项
                    handleConfigItem(config, fullKey)
                }
            }
        }
        handleConfigGroup(configDict)
    }
    // 补充空白参数
    function supplyDefaultParams(config) {
        if(!config.hasOwnProperty("type")) // 类型
            config.type = ""
        if(!config.hasOwnProperty("save")) // 保存
            config.save = true
    }
    // 获取值
    function getValue(key) {
        return valueDict[key]
    }
    // 设置值
    function setValue(key, val) {
        if(valueDict[key] === val) // 排除相同值
            return
        onChangedFunc(key, val, valueDict[key]) // 触发函数，传入新值和旧值
        valueDict[key] = val
        if(originDict[key].save) { // 需要保存值
            saveValue(key)
        }
    }
    // 初始化期间。不执行触发函数
    property bool isChangedInit: false
    // 触发函数
    function onChangedFunc(key, newVal, oldVal) {
        if(!isChangedInit) // 初始化期间。不执行触发函数
            return
        // 配置项存在触发函数，则执行
        if(originDict[key].hasOwnProperty("onChanged")) 
            originDict[key].onChanged(newVal, oldVal)
    }
    // 初始化，执行全部触发函数
    function initChangedFuncs() {
        isChangedInit = true
        for(let k in originDict) {
            onChangedFunc(k, valueDict[k], undefined) // 传入空旧值
        }
    }
    // 带缓存的存储值
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

    // 存储配置项
    Settings_ {
        id: settings
        category: category_ // 自定义类别名称
    }
    // 存储UI项
    Settings_ {
        id: uiSettings
        category: category_+"-UI" // 类别名称-ui
        property alias advanced: configs.advanced
    }

    // ========================= 【自动生成组件】 =========================

    // 初始化 自动生成组件
    function initPanelComponent() {
        enabledAdvanced = false
        const compListLength = compList.length
        if(compListLength !== 0) { // 外层组件列表非空，先删除旧的组件
            for(let i = compListLength-1; i>=0; i--) { // 倒序遍历，从内层往外层删
                compList[i].destroy()
            }
            compList = []
        }
        compDict = {}

        function handleConfigGroup(group, parent=panelContainer) { // 处理一个配置组
            for(let key in group) {
                const config = group[key]
                if(typeof config !== "object")
                    continue
                if(! (typeof config.title === "string")) // 无标题，则表示不生成组件
                    continue
                if(config.advanced) // 任意一个选项是高级选项，则总体开启高级模式
                    enabledAdvanced = true
                // 若是配置项组，递归遍历
                if(config.type === "group") { 
                    // 若是外层，则生成外层group组件；若是内层则生成内层组件。
                    const comp = parent===panelContainer ? compGroup : compGroupInner
                    const fold = config.fold?true:false // 是否折叠，转布尔值
                    const obj = comp.createObject(parent, {"key":config.fullKey, "configs":configs})
                    compList.push(obj) // 保存组件引用
                    handleConfigGroup(config, obj.container) // 递归下一层，父级变成本层
                }
                // 若是配置项
                else {
                    if(componentDict.hasOwnProperty(config.type)) {
                        const comp = componentDict[config.type]
                        const obj = comp.createObject(parent, {"key":config.fullKey, "configs":configs})
                        compList.push(obj) // 保存组件引用
                        compDict[config.fullKey] = obj
                    }
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
        property alias ctrlBar: ctrlBar // 控制栏的引用

        Column {
            id: panelContainer
            anchors.fill: parent
            spacing: theme.spacing

            // 顶部控制栏
            Item {
                id: ctrlBar
                height: theme.textSize*1.5
                anchors.left: parent.left
                anchors.right: parent.right

                Button_ {
                    id: ctrlBtn1
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    text_: qsTr("重置")
                    toolTip: qsTr("重置本页上的设定")
                    textColor_: theme.noColor
                    onClicked: {
                        const argd = {yesText: qsTr("重置设定")}
                        const callback = (flag)=>{ if(flag) reset() }
                        qmlapp.popup.dialog("", qsTr("要重置本页的设定吗？"), callback, "warning", argd)
                    }
                }
                CheckButton {
                    visible: enabledAdvanced
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: ctrlBtn1.left
                    text_: qsTr("高级")
                    toolTip: qsTr("显示更多高级选项")
                    textColor_: configs.advanced ? theme.textColor : theme.subTextColor
                    checked: configs.advanced
                    enabledAnime: true
                    onCheckedChanged: configs.advanced = checked
                }
            }
        }
    }
    // 配置项组（外层）
    Component {
        id: compGroup

        Item {
            id: groupRoot
            property string key: "" // 键
            property var configs: undefined // 保存对Configs组件的引用
            property var origin: undefined // 起源参数（静态）
            property string title: "" // 标题
            property alias container: panelContainer // 容器
            anchors.left: parent.left
            anchors.right: parent.right
            height: childrenRect.height

            Component.onCompleted: {
                origin = configs.originDict[key]
                title = origin.title
            }


            Text_ {
                id: groupText
                text: title
                anchors.left: parent.left
                // 显示标题时，自动高度；否则高度为0
                height: (title) ? undefined:0
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
            property string key: "" // 键
            property var configs: undefined // 保存对Configs组件的引用
            property var origin: undefined // 起源参数（静态）
            property string title: "" // 标题
            property alias container: panelContainer // 容器
            property bool enabledFold: false // 启用折叠机制
            property bool fold: false // 折叠状态
            property string foldKey: key+".fold" // 折叠键
            property alias isFold: foldBtn.checked // 折叠
            anchors.left: parent.left
            anchors.right: parent.right
            clip: true
            // 折叠时高度=标题+0，展开时高度=标题+内容
            height: groupText.height + (fold ? 0:panelContainer.height)

            Component.onCompleted: {
                origin = configs.originDict[key]
                title = origin.title
                // 折叠属性。origin值转布尔，undefined当成false
                enabledFold = origin.enabledFold?true:false
                const f = origin.fold?true:false
                if(enabledFold) { // 若启用折叠按钮，则取记录值，无记录则使用设定值
                    const readf = uiSettings.value(foldKey, undefined)
                    // 字符串转bool
                    if(readf===undefined) fold = f
                    else if(readf===true || readf==="true") fold = true
                    else if(readf===false || readf==="false") fold = false
                }
                else { // 未启用折叠按钮，则使用设定值
                    fold = f
                }
            }

            // 背景
            MouseAreaBackgroud { }
            // 标题
            Text_ {
                id: groupText
                text: title+"："
                anchors.left: parent.left
                anchors.leftMargin: theme.smallSpacing
                height: theme.textSize+theme.smallSpacing*2
                verticalAlignment: Text.AlignVCenter
            }
            // 折叠按钮
            Button_ {
                id: foldBtn
                visible: enabledFold
                anchors.right: parent.right
                anchors.rightMargin: theme.smallSpacing
                anchors.verticalCenter: groupText.verticalCenter
                height: groupText.height
                textSize: theme.smallTextSize
                textColor_: theme.subTextColor
                text_: fold ? qsTr("展开")+" 🔽" : qsTr("折叠")+" 🔼"
                onClicked: {
                    fold=!fold
                    uiSettings.setValue(foldKey, fold) // 折叠状态写入本地
                }
            }
            // 内容
            Column {
                id: panelContainer
                anchors.left: panelLeftBorder.right
                anchors.right: parent.right
                anchors.top: groupText.bottom
                anchors.leftMargin: theme.smallSpacing*0.5 // 子项右偏移
            }
            // 内容左边的边框
            Rectangle {
                id: panelLeftBorder
                anchors.left: parent.left
                anchors.top: panelContainer.top
                anchors.bottom: panelContainer.bottom
                anchors.leftMargin: theme.smallSpacing*2
                width: theme.smallSpacing*0.5
                color: theme.coverColor1
            }
        }
    }
    // ========== 生成组件字典 ========== 
    property var componentDict: {
        "boolean": compBoolean,
        "enum": compEnum,
        "file": compFile,
        "text": compText,
        "buttons": compBtns,
    }
    // 配置项：布尔值
    Component {
        id: compBoolean

        ConfigItemComp {
            id: boolRoot
            property bool checked: true
            property bool isInit: false

            // 初始化
            Component.onCompleted: {
                isInit = true // 初始化完毕，允许启用动画
            }

            // 更新UI
            updateUI: ()=>{
                checked = value()
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
            CheckBox_ {
                id: switchBtn
                anchors.right: parent.right
                anchors.rightMargin: theme.smallSpacing
                anchors.verticalCenter: parent.verticalCenter
                checked: boolRoot.checked
                enabledAnime: boolRoot.isInit
            }
        }
    }
    // 配置项：文本
    Component {
        id: compText

        ConfigItemComp {
            id: rootText
            // 更新UI
            updateUI: ()=>{
                textInput.text = value()
            }
            // 修改值
            function set(t) {
                value(t) // 设置值
            }
            // 输入框
            Rectangle {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.margins: 1
                width: parent.width*0.5
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
                        rootText.set(text)
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
            // 更新UI
            updateUI: ()=>{
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
                    width: theme.smallTextSize
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
                        color: comboBox.currentIndex===index? theme.textColor:theme.subTextColor
                    }
                    background: Rectangle {
                        color: theme.bgColor
                        MouseAreaBackgroud {
                            radius_: 0
                            onClicked: parent.clicked()
                        }
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
            // 更新UI
            updateUI: ()=>{
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
    // 配置项：按钮组
    Component {
        id: compBtns

        ConfigItemComp {
            id: rootFile

            Row {
                anchors.right: parent.right
                anchors.rightMargin: theme.smallSpacing
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                spacing: theme.smallSpacing

                Repeater {
                    model: origin.btnsList
                    Button_ {
                        property var info: origin.btnsList[index]
                        text_: info.text
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        bgColor_: info.bgColor?info.bgColor:theme.coverColor1
                        textColor_: info.textColor?info.textColor:theme.textColor

                        onClicked: {
                            info.onClicked()
                        }
                    }
                }
            }
        }
    }
}