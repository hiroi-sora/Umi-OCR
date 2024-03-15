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
    "数字 number （输入框）": {
        "title": ,
        "isInt": true 整数 / false 浮点数,
        "default": 233,
        "max": 可选，上限,
        "min": 可选，下限,
        "unit": 可选，单位。qsTr("秒"),
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
    "热键 hotkey": {
        "title": ,
        "type": "hotkey",
        "default": "win+alt+c", // 默认热键
        "eventTitle": "<<screenshot>>", // 触发事件标题
    },
    "按钮组 buttons": {
        "title": ,
        "btnsList": [
            {"text":"名称1", "onClicked":函数1, "textColorKey": 字体颜色名}},
            {"text":"名称2", "onClicked":函数2, "bgColorKey": 背景颜色名}},
        ],
        // 颜色名 ColorKey 为 theme.keys 的值
    },
    "任意变量 var": { // 程序缓存任意变量
        "type": "var",
        "save": false,
    }

    通用配置元素：
    "title": 显示名称。不填（或undefined）时不生成组件。填写（包括空字符串""）时自动生成控件。
    "type": 控件类型,
    "save": 可选，填false时不保存（每次初始化为默认值）,
    "toolTip": 可选，字符串，鼠标悬停时的提示,
    "advanced": 可选，填true时为高级选项，平时隐藏
    "onChanged": 可选，值变化时的回调函数，  (newVal, oldVal)=>{console.log(`值从 ${oldVal} 变为 ${newVal}`)}
        onChanged可以有返回值。默认返回 undefined 表示允许变动，返回 true 表示阻止这次变动。
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
    property bool autoLoad: true // 自动加载设置项

    // 重置所有设置为默认值
    function reset() {
        for (let key in originDict) {
            setValue(key, originDict[key].default, true) // 刷新值
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
    function getValueDict() {
        return valueDict
    }
    // 获取原始值字典
    function getOriginDict() {
        return originDict
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
        if(autoLoad) reload() // 自动加载设置项
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
                else if(config.type === "var") { // 缓存任意类型
                    if(!config.hasOwnProperty("default"))
                        config.default = undefined
                }
            }
            // 类型判断：省略type
            else{
                if (typeof config.default === "boolean") { // 布尔
                    config.type = "boolean"
                }
                else if (config.hasOwnProperty("optionsList")) { // 枚举
                    if(config.optionsList.length==0) {
                        qmlapp.popup.message("", qsTr("%1 处理配置项异常：\n%2枚举列表为空。").arg(category_).arg(key), "error")
                        return
                    }
                    config.type = "enum"
                    if(config.default == undefined)
                        config.default = config.optionsList[0][0]
                }
                else if (typeof config.default === "string") { // 文本
                    config.type = "text"
                }
                else if (typeof config.default === "number") { // 数字
                    config.type = "number"
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
                    case "number": // 数字，字符串转数字
                        if(typeof val === "string") {
                            if(config.isInt)
                                val = parseInt(val)
                            else
                                val = parseFloat(val)
                        }
                        flag = !(val==null || isNaN(val)) // 若非数字，则设为默认数值
                        break
                    case "enum": // 枚举，检查记录参数是否在列表内
                        val = str2var(val) // 尝试转为合适类型
                        for(let i in config.optionsList) {
                            if(config.optionsList[i][0] == val) {
                                flag = true
                                break
                            }
                        }
                        break
                    // 无需检查
                    case "var": // 任意
                    case "file": // 文件
                    case "text": // 文本
                    case "hotkey": // 热键
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
                if(config.type==="group") { // 若是配置项组，递归遍历
                    handleConfigGroup(config, fullKey+".") // 前缀加深一层
                    originDict[fullKey] = config
                }
                else { // 若是配置项
                    originDict[fullKey] = config
                    handleConfigItem(config, fullKey)
                }
            }
        }
        handleConfigGroup(configDict)
    }
    // 尝试将字符串类型的变量转为合适的类型
    function str2var(str) {
        // 非字符串
        if(typeof str !== "string") return str
        // 尝试转数字
        const num = Number(str)
        if(!isNaN(num)) return num
        // 尝试转布尔
        if(str === "true") return true
        if(str === "false") return false
        // 都不符合，保持为字符串
        return str
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
    // 设置值  键, 值, 是否刷新UI, 是否立刻写入本地（还是缓存写入）
    function setValue(key, val, isupdateUI=false, saveNow=false) {
        if(typeof val !== "object" && valueDict[key] === val) // 如果val不是数组或字典，排除相同值
            return
        let res = onChangedFunc(key, val, valueDict[key]) // 触发函数，传入新值和旧值
        if(res !== undefined) { // 阻止这次变动
            compDict[key].updateUI()
            return
        }
        valueDict[key] = val
        if(originDict[key].save) { // 需要保存值
            if(saveNow) // 立刻保存
                settings.setValue(key, val)
            else // 缓存保存
                saveValue(key)
        }
        if(isupdateUI && compDict.hasOwnProperty(key)) { // 刷新UI
            compDict[key].updateUI()
        }
    }
    // 初始化期间。不执行触发函数
    property bool isChangedInit: false
    // 触发函数
    function onChangedFunc(key, newVal, oldVal) {
        if(!isChangedInit) // 初始化期间。不执行触发函数
            return undefined
        // 配置项存在触发函数，则执行
        if(originDict[key].hasOwnProperty("onChanged")) 
            return originDict[key].onChanged(newVal, oldVal)
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
        category: category_
        property alias configs_advanced: configs.advanced
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
        property alias advanced: configs.advanced // 高级标志的引用
        // 获取所有外层配置组的信息
        function getGroupList() {
            const c = panelContainer.children
            let itemList = []
            for(let i in c) {
                if(c[i].title===undefined)
                    return
                itemList.push({
                    title: c[i].title,
                    advanced: c[i].advanced
                })
            }
            return itemList
        }
        // 滚到一个外层配置组的位置
        function scrollToGroup(index) {
            const children = panelContainer.children
            if(index < 0 || index >= children.length) {
                console.log(`[Error] 无法滚动到${index}，超出范围！`)
                return
            }
            const c = children[index]
            let y = c.y - size_.line
            let max = panelContainer.height - panelComponent.height
            if(y < 0) y = 0
            if(y > max) y = max
            y = y / panelContainer.height
            ScrollBar.vertical.position = y
            c.kirakira && c.kirakira() // 闪烁
        }

        Column {
            id: panelContainer
            anchors.fill: parent
            anchors.rightMargin: size_.spacing
            spacing: size_.spacing

            // 顶部控制栏
            Item {
                id: ctrlBar
                height: size_.line*1.5
                anchors.left: parent ? parent.left : undefined
                anchors.right: parent ? parent.right : undefined

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
                    toolTip: qsTr("显示更多高级选项。它们标有 * 号。\n请谨慎修改高级选项。")
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
            property bool advanced: false // true时是高级选项
            anchors.left: parent.left
            anchors.right: parent.right
            // 高级模式，整组隐藏
            height: (advanced&&!configs.advanced) ? 0 : groupText.height+groupRectangle.height
            visible: !(advanced&&!configs.advanced)
            // 边框闪烁
            function kirakira() {
                if(qmlapp.enabledEffect)
                    blinkAnimation.start()
            }

            Component.onCompleted: {
                origin = configs.originDict[key]
                title = origin.title
                if(origin.advanced) {
                    advanced = origin.advanced
                    title = "* "+title
                }
            }
            // 标题
            Text_ {
                id: groupText
                text: title
                anchors.left: parent.left
                anchors.leftMargin: size_.spacing
                // 显示标题时，自动高度；否则高度为0
                height: (title) ? undefined:0
                
            }
            // 内容
            Rectangle {
                id: groupRectangle
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: groupText.bottom
                anchors.topMargin: size_.smallSpacing
                color: theme.bgColor
                radius: size_.panelRadius
                height: childrenRect.height + size_.smallSpacing

                Column {
                    id: panelContainer
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: size_.smallSpacing
                    spacing: size_.smallSpacing
                }

                Item { // 底部占位
                    anchors.top: panelContainer.bottom
                    height: size_.smallSpacing
                }
            }
            // 闪烁边框
            Panel {
                id: groupBorder
                anchors.fill: parent
                color: "#00000000"
                border.width: 2
                border.color: theme.specialTextColor
                visible: false
                opacity: 0
                // 颜色闪烁动画
                SequentialAnimation {
                    id: blinkAnimation
                    running: false
                    loops: 3
                    onStarted: groupBorder.visible = true
                    NumberAnimation {
                        target: groupBorder; property: "opacity"
                        from: 0; to: 1; duration: 200
                    }
                    NumberAnimation {
                        target: groupBorder; property: "opacity"
                        from: 1; to: 0; duration: 200
                    }
                    onStopped: {
                        groupBorder.visible = false
                    }
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
                // 如果设定了提示，则加载提示组件
                if(origin.toolTip) {
                    toolTipLoader.sourceComponent = toolTip
                }
            }

            // 提示
            Component {
                id: toolTip
                ToolTip_ {
                    visible: mouseAreaBackgroud.hovered
                    text: origin.toolTip
                }
            }
            Loader { id: toolTipLoader }
            // 背景
            MouseAreaBackgroud { id: mouseAreaBackgroud }
            // 标题
            Text_ {
                id: groupText
                text: title+"："
                anchors.left: parent.left
                anchors.leftMargin: size_.smallSpacing
                height: size_.line+size_.smallSpacing*2
                verticalAlignment: Text.AlignVCenter
            }
            // 折叠按钮
            Button_ {
                id: foldBtn
                visible: enabledFold
                anchors.right: parent.right
                anchors.rightMargin: size_.smallSpacing
                anchors.verticalCenter: groupText.verticalCenter
                height: groupText.height
                textSize: size_.smallLine
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
                anchors.leftMargin: size_.smallSpacing*0.5 // 子项右偏移
            }
            // 内容左边的边框
            Rectangle {
                id: panelLeftBorder
                anchors.left: parent.left
                anchors.top: panelContainer.top
                anchors.bottom: panelContainer.bottom
                anchors.leftMargin: size_.smallSpacing*2
                width: size_.smallSpacing*0.5
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
        "number": compNumber,
        "hotkey": compHotkey,
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
                anchors.rightMargin: size_.smallSpacing
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
                radius: size_.btnRadius

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
    // 配置项：数字
    Component {
        id: compNumber

        ConfigItemComp {
            id: rootNumber
            property string errTips: ""
            // 更新UI
            updateUI: ()=>{
                textInput.text = value()
            }
            // 修改值
            function set(t) {
                let n = check(t)
                value(n) // 设置值
            }
            // 检查值
            function check(val) {
                let n = Number(val);
                if (!isNaN(n)) { // 是数字
                    if(origin.isInt && !Number.isInteger(n)) {
                        errTips = qsTr("必须为整数")
                    }
                    else {
                        if(origin.max !== undefined && n > origin.max) {
                            errTips = qsTr("不能超过")+origin.max
                        }
                        else if(origin.min !== undefined && n < origin.min) {
                            errTips = qsTr("不能低于")+origin.min
                        }
                        else
                            errTips = ""
                    }
                }
                else {
                    errTips = qsTr("必须为数字")
                }
                if(errTips==="")
                    return n
                return null
            }
            // 提示信息
            Rectangle {
                visible: errTips!==""
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: textInputContainer.left
                anchors.margins: 3
                color: theme.noColor
                radius: size_.btnRadius
                width: errTipsText.width+size_.smallSpacing*2
                Text_ {
                    id: errTipsText
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.leftMargin: size_.smallSpacing
                    color: theme.bgColor
                    text: errTips
                }
            }
            // 输入框
            Rectangle {
                id: textInputContainer
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.margins: 1
                width: parent.width*0.25
                color: "#00000000"
                border.width: 2
                border.color: theme.coverColor2
                radius: size_.btnRadius

                TextInput_ {
                    id: textInput
                    clip: true
                    anchors.left: parent.left
                    anchors.right: unitText.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: parent.border.width
                    // anchors.rightMargin: parent.border.width
                    onTextChanged: { // 对话框文本改变时设置值
                        rootNumber.set(text)
                    }
                }
                // 单位
                Text_ {
                    id: unitText
                    visible: origin.unit!==undefined
                    text: origin.unit===undefined ? "" : origin.unit
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: size_.smallSpacing
                    verticalAlignment: Text.AlignVCenter // 垂直居中
                    color: theme.subTextColor
                    font.pixelSize: size_.smallText
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
                    anchors.leftMargin: size_.smallSpacing
                    verticalAlignment: Text.AlignVCenter
                    font.pixelSize: size_.text
                    font.family: theme.fontFamily
                    color: theme.subTextColor
                }
                // 前景箭头
                indicator: Icon_ {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.margins: size_.smallSpacing
                    height: size_.smallLine
                    width: size_.smallLine
                    icon: "down"
                    color: theme.subTextColor
                }
                // 背景
                background: Rectangle {
                    anchors.fill: parent
                    color: "#00000000"
                    border.width: 2
                    border.color: theme.coverColor2
                    radius: size_.btnRadius
                    
                    // 背景
                    MouseAreaBackgroud {
                        cursorShape: Qt.PointingHandCursor
                    }
                }
                // 选项
                delegate: ItemDelegate {
                    width: comboBox.width
                    height: size_.line + size_.spacing
                    Text {
                        text: modelData + (comboBox.currentIndex===index? " √":"")
                        anchors.left: parent.left
                        anchors.leftMargin: size_.smallSpacing
                        font.pixelSize: size_.text
                        font.family: theme.fontFamily
                        font.bold: comboBox.currentIndex===index
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
                    radius: size_.btnRadius

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

            Row {
                anchors.right: parent.right
                anchors.rightMargin: size_.smallSpacing
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                spacing: size_.smallSpacing

                Repeater {
                    model: origin.btnsList
                    Button_ {
                        property var info: origin.btnsList[index]
                        text_: info.text
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        bgColor_: info.bgColorKey?theme[info.bgColorKey]:theme.coverColor1
                        textColor_: info.textColorKey?theme[info.textColorKey]:theme.textColor

                        onClicked: {
                            info.onClicked()
                        }
                    }
                }
            }
        }
    }
    // 配置项：热键
    Component {
        id: compHotkey

        ConfigItemComp {
            id: rootHotkey
            property string eventTitle: origin.eventTitle
            property string keysName: ""
            property int readNum: 0 // 记录更新了几次

            // 初始化，更新UI
            updateUI: ()=>{
                const kn = value()
                changeHotkey(kn, false)
            }
            // 改变快捷键
            function changeHotkey(kn, showMsg=true) {
                // 移除相同事件的快捷键
                qmlapp.keyMouse.delHotkey("", eventTitle, 0)
                // 取消快捷键
                if(kn === "") {
                    keysName = ""
                    value("")
                    if(showMsg)
                        qmlapp.popup.simple(qsTr("已取消%1的快捷键。").arg(title), "")
                }
                // 注册新按键
                else {
                    const res = qmlapp.keyMouse.addHotkey(kn, eventTitle, 0)
                    // 成功
                    if(res.startsWith("[Success]")) {
                        keysName = kn
                        value(kn)
                        if(showMsg)
                            qmlapp.popup.simple(qsTr("更新热键成功"), qsTr("%1的快捷键为 %2").arg(title).arg(kn))
                    }
                    // 失败
                    else {
                        keysName = ""
                        value("")
                        // 重复注册
                        if(res.startsWith("[Warning] Registering same hotkey.")) {
                            qmlapp.popup.message("", qsTr("%1 快捷键%2已被注册，请尝试另外的按键组合。").arg(title).arg(kn), "warning")
                        }
                        else { // 未知原因
                            qmlapp.popup.message("", qsTr("%1 快捷键%2无法注册，请尝试另外的按键组合。").arg(title).arg(kn), "error")
                        }
                    }
                }
            }
            // 录制开始
            function readHotkey() {
                // 展开遮罩
                readNum = 1
                qmlapp.popup.showMask(qsTr("请按下快捷键组合。按【Esc】退出。"), "<<readHotkey>>")
                // 订阅事件
                qmlapp.pubSub.subscribe("<<readHotkeyRunning>>", rootHotkey, "readRunning")
                qmlapp.pubSub.subscribe("<<readHotkeyFinish>>", rootHotkey, "readFinish")
                // 开始录制
                let res = qmlapp.keyMouse.readHotkey("<<readHotkeyRunning>>", "<<readHotkeyFinish>>")
                if(res !== "[Success]") { // 开始录制失败
                    // 隐藏遮罩
                    qmlapp.popup.hideMask("<<readHotkey>>")
                    // 取消订阅事件
                    qmlapp.pubSub.unsubscribe("<<readHotkeyRunning>>", rootHotkey, "readRunning")
                    qmlapp.pubSub.unsubscribe("<<readHotkeyFinish>>", rootHotkey, "readFinish")
                    if(res.startsWith("[Warning] Recording is running.")) // 报错
                        qmlapp.popup.message("", qsTr("当前快捷键录制已在进行，不能同时录制！"), "warning")
                    else
                        qmlapp.popup.message(qsTr("无法录制快捷键"), res, "error")
                }
            }
            // 录制中的回调
            function readRunning(kn){
                readNum++  // 更新遮罩
                qmlapp.popup.showMask(kn, "<<readHotkey>>")
            }
            // 录制完毕的回调
            function readFinish(kn) {
                // 隐藏遮罩
                for(let i=0; i<readNum; i++)
                    qmlapp.popup.hideMask("<<readHotkey>>")
                // 取消订阅事件
                qmlapp.pubSub.unsubscribe("<<readHotkeyRunning>>", rootHotkey, "readRunning")
                qmlapp.pubSub.unsubscribe("<<readHotkeyFinish>>", rootHotkey, "readFinish")
                // 改变快捷键
                changeHotkey(kn)
            }

            Item {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.margins: 1
                width: parent.width*0.5

                IconButton {
                    id: clearBtn
                    icon_: "clear"
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    anchors.margins: 1
                    width: height
                    onClicked: changeHotkey("")
                }
                Button_ {
                    id: hotkeyBtn
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: clearBtn.left
                    textColor_: theme.subTextColor
                    borderWidth: 2
                    borderColor: theme.coverColor2
                    text_: keysName
                    onClicked: readHotkey()
                }
            }
        }
    }
}