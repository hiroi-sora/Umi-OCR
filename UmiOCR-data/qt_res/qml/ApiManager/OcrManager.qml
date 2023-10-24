// ==========================================
// =============== OCR接口管理 ===============
// ==========================================

// qml的 api key 与 python api.ocr 中的字典要一致

import QtQuick 2.15

Item {

    // 配置在python那边编写
    // 缓存全局配置，如引擎路径、账号密钥等
    property var globalOptions: {
        "title": qsTr("文字识别"),
        "type": "group",

        "btns": {
            "title": qsTr("操作"),
            "btnsList": [
                {"text":qsTr("强制终止任务"), "onClicked": stopAllMissions, "textColorKey":"noColor"},
                // {"text":qsTr("测试API"), "onClicked":()=>{}},
                {"text":qsTr("应用修改"), "onClicked": applyConfigs, "textColorKey":"yesColor"},
            ],
        },
        "api": {
            "title": qsTr("当前接口"),
            "optionsList": [],
        },
    }

    // ========================= 【外部接口】 =========================

    // 应用更改，showSuccess=false时不显示成功提示
    function applyConfigs(showSuccess=true) {

        // 成功应用修改之后的刷新函数
        function successUpdate() {
            // 刷新qml各个页面的独立配置
            for (let key in deployDict) {
                const p = deployDict[key].page
                if(!p.configDict) { // 页面已经不存在了，则从记录字典中删除
                    delete deployDict[key]
                    continue
                }
                const k = deployDict[key].configKey
                p.configDict[k] = localOptions[apiKey] // 刷新页面设置
                p.reload() // 刷新页面UI
            }
        }

        // 获取当前全局 apiKey ，验证在本字典中的存在性
        const nowKey = qmlapp.globalConfigs.getValue("ocr.api")
        if(!localOptions.hasOwnProperty(nowKey)) {
            const s = qsTr("OCR API 列表中不存在%1").arg(nowKey)
            qmlapp.popup.message("", s, "error")
            return
        }
        // 验证 py 是否有执行中的任务
        const pyStatus = qmlapp.msnConnector.callPy("ocr", "getStatus", [])
        const msnLen = Object.keys(pyStatus.missionListsLength).length
        if(msnLen > 0) { // 当前执行中的任务队列数量 > 0
            let n = 0
            for(let k in pyStatus.missionListsLength)
                n += pyStatus.missionListsLength[k]
            const s = qsTr("当前已有%1组任务队列、共%2个任务正在执行。您可【强制终止任务】后修改API。").arg(msnLen).arg(n)
            qmlapp.popup.message(qsTr("无法修改 文字识别接口设置"), s, "warning")
            return
        }
        // 从全局配置中，提取出目前apiKey对应的配置项
        const allDict = qmlapp.globalConfigs.getValueDict()
        const ocrk = "ocr."+nowKey
        const info = {} // 汇聚为配置信息
        for(let k in allDict) { // 从全局配置中，提取以该api开头的键/值
            if(k.startsWith(ocrk)) {
                info[k] = allDict[k]
            }
        }
        // 将配置信息发送给py，然后验证操作是否成功
        const msg = qmlapp.msnConnector.callPy("ocr", "setApi", [nowKey, info])

        // 成功，写入记录
        if(msg.startsWith("[Success]")) {
            apiKey = nowKey
            successUpdate()
            if(showSuccess) { // 显示弹窗
                qmlapp.popup.simple(qsTr("文字识别接口应用成功"), qsTr("当前API为【%1】").arg(nowKey))
            }
        }
        else {
            qmlapp.popup.message(qsTr("文字识别接口应用失败"), msg, "error")
        }
    }

    // 终止所有任务
    function stopAllMissions() {
        const pyStatus = qmlapp.msnConnector.callPy("ocr", "getStatus", [])
        const msnLen = Object.keys(pyStatus.missionListsLength).length
        if(msnLen == 0) { // 无任务
            qmlapp.popup.simple(qsTr("当前没有运行中的任务"), "")
            return
        }

        let n = 0
        for(let k in pyStatus.missionListsLength)
            n += pyStatus.missionListsLength[k]
        const s = qsTr("当前已有%1组任务队列、共%2个任务正在执行。\n要强制终止全部任务吗？").arg(msnLen).arg(n)

        const argd = {yesText: qsTr("强制终止任务")}
        const callback = (flag)=>{ if(flag) qmlapp.msnConnector.callPy("ocr", "stopAllMissions", []) }
        qmlapp.popup.dialog("", s, callback, "warning", argd)
    }

    // 部署进一个Configs的配置项里，可动态改变配置页。
    // 传入configs页引用和所在字典键（只能在最外层）
    function deploy(page, configKey) {
        // 记录已部署页面
        const pageId = page.toString()
        deployDict[pageId] = { 
            "page": page,
            "configKey": configKey,
        }
        // 返回初始配置字典
        if(apiKey === ""){
            return { // apiKey未初始化，先返回空的占位
                "title": "",
                "type": "group",
            }
        }
        else{ // apiKey已初始化，返回对应配置
            return localOptions[apiKey]
        }
    }

    // 初始化1：传入python ocr信息，整理信息，返回全局配置字典
    function init1(options) {
        localOptions = {}
        for (var key in options) {
            const gOpt = options[key].global_options
            const lOpt = options[key].local_options
            if(gOpt) { // 有全局配置
                globalOptions.api.optionsList.push([key, gOpt.title])
                globalOptions[key] = gOpt
            }
            else { // 无全局配置
                globalOptions.api.optionsList.push([key, key])
                globalOptions[key] = {"title":key, "type":"group"}
            }
            if(lOpt) // 有局部配置
                localOptions[key] = lOpt
            else // 无局部配置
                localOptions[key] = {"title":key, "type":"group"}
        }
        qmlapp.globalConfigs.configDict.ocr = globalOptions // 写入全局预配置
    }
    // 初始化2：应用更改
    function init2() {
        applyConfigs(false)
        console.log("% OcrManager 初始化OCR管理器完毕！")
    }

    // ========================= 【内部】 =========================
    property string apiKey: "" // 当前选定的apiKey
    property var deployDict: {} // 存放 部署了配置的页面
    property var localOptions: {} // 缓存局部配置
    property var pyOptions: undefined // 由py定义的配置参数的原始内容

    Component.onCompleted: {
        deployDict = {}
    }
}