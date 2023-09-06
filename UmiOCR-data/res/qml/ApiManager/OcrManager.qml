// ==========================================
// =============== OCR接口管理 ===============
// ==========================================

// qml的 api key 与 python api.ocr 中的字典要一致

import QtQuick 2.15

QtObject {

    // ========================= 【配置】 =========================
    
    // 全局配置，如引擎路径、账号密钥等
    property var globalOptions: {
        "title": qsTr("文字识别"),
        "type": "group",

        "btns": {
            "title": qsTr("操作"),
            "btnsList": [
                {"text":qsTr("强制终止任务"), "onClicked": stopAllMissions, "textColor":theme.noColor},
                // {"text":qsTr("测试API"), "onClicked":()=>{}},
                {"text":qsTr("应用修改"), "onClicked": applyConfigs, "textColor":theme.yesColor},
            ],
        },
        "api": {
            "title": qsTr("当前接口"),
            "optionsList": [
                ["PaddleOCR", qsTr("PaddleOCR（本地）")],
                // ["RapidOCR", qsTr("RapidOCR（本地）")],
            ],
        },
        "PaddleOCR": {
            "title": qsTr("PaddleOCR（本地）"),
            "type": "group",

            "path": {
                "title": qsTr("引擎exe路径"),
                "type": "file",
                "default": "lib/PaddleOCR-json/PaddleOCR-json.exe",
                "selectExisting": true, // 选择现有
                "selectFolder": false, // 选择文件
                "dialogTitle": qsTr("PaddleOCR 引擎exe路径"),
            },
            "enable_mkldnn": {
                "title": qsTr("启用MKL-DNN加速"),
                "default": true,
                "toolTip": qsTr("使用MKL-DNN数学库提高神经网络的计算速度。能大幅加快OCR识别速度，但也会增加内存占用。"),
            },
            "ram_max": {
                "title": qsTr("内存占用限制"),
                "default": -1,
                "min": -1,
                "unit": "MB",
                "isInt": true,
                "advanced": true,
                "toolTip": qsTr("值>0时启用。引擎内存占用超过该值时，执行内存清理。"),
            },
            "ram_time": {
                "title": qsTr("内存闲时清理"),
                "default": 30,
                "min": -1,
                "unit": qsTr("秒"),
                "isInt": true,
                "advanced": true,
                "toolTip": qsTr("值>0时启用。引擎空闲时间超过该值时，执行内存清理。"),
            },
        },
        // "RapidOCR": {
        //     "title": qsTr("RapidOCR（本地）"),
        //     "type": "group",

        //     "path": {
        //         "title": qsTr("引擎exe路径"),
        //         "type": "file",
        //         "default": "lib/RapidOCR-json/RapidOCR-json.exe",
        //         "selectExisting": true, // 选择现有
        //         "selectFolder": false, // 选择文件
        //         "dialogTitle": qsTr("RapidOCR 引擎exe路径"),
        //     },
        // },
    }

    // 单独配置，每个页面的选项可以不同。都必须有 language 语言列表。
    property var pageOptions: {
        "PaddleOCR": {
            "title": qsTr("文字识别（PaddleOCR）"),
            "type": "group",

            "language": {
                "title": qsTr("语言/模型库"),
                "optionsList": [],
            },
            "cls": {
                "title": qsTr("纠正文本方向"),
                "default": false,
                "toolTip": qsTr("启用方向分类，识别倾斜或倒置的文本。可能降低识别速度。")
            },
            "limit_side_len": {
                "title": qsTr("限制图像边长"),
                "optionsList": [
                    [960, "960 "+qsTr("（默认）")],
                    [2880, "2880"],
                    [4320, "4320"],
                    [999999, qsTr("无限制")],
                ],
                "toolTip": qsTr("将边长大于该值的图片进行压缩，可以提高识别速度。可能降低识别精度。"),
                "advanced": true, // 高级选项
            },
        },
        "RapidOCR": {
            "title": qsTr("文字识别（RapidOCR）"),
            "type": "group",

            "language": {
                "title": qsTr("语言/模型库"),
                "optionsList": [
                    ["default", "默认"],
                ],
            },
        },
    }

    // ========================= 【外部接口】 =========================

    // 应用更改，showSuccess=false时不显示成功提示
    function applyConfigs(showSuccess=true) {

        // 成功应用修改之后的刷新函数
        function successUpdate() {
            // 从python获取额外信息，填入pageOptions。主要为了动态刷新[language][optionsList]
            const info = qmlapp.msnConnector.callPy("ocr", "getApiInfo", [])
            for(let k1 in info) {
                if(k1 in pageOptions[apiKey])
                    for(let k2 in info[k1])
                        pageOptions[apiKey][k1][k2] = info[k1][k2]
            }
            // 刷新qml各个页面的独立配置
            for (let key in deployDict) {
                const p = deployDict[key].page
                if(!p.configDict) { // 页面已经不存在了，则从记录字典中删除
                    delete deployDict[key]
                    continue
                }
                const k = deployDict[key].configKey
                p.configDict[k] = pageOptions[apiKey] // 刷新页面设置
                p.reload() // 刷新页面UI
            }
        }

        // 获取当前全局 apiKey ，验证在本字典中的存在性
        const nowKey = qmlapp.globalConfigs.getValue("ocr.api")
        if(!pageOptions.hasOwnProperty(nowKey)) {
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
        const allDict = qmlapp.globalConfigs.getConfigValueDict()
        const ocrk = "ocr."+nowKey
        const info = {"ocr.api": nowKey} // 汇聚为配置信息
        for(let k in allDict) { // 从全局配置中，提取以该api开头的键/值
            if(k.startsWith(ocrk))
                info[k] = allDict[k]
        }
        // 将配置信息发送给py，然后验证操作是否成功
        const msg = qmlapp.msnConnector.callPy("ocr", "setApi", [info])

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
            return pageOptions[apiKey]
        }
    }

    // 必须等全局配置初始化完毕后才能初始化OCR管理器
    function init() {
        applyConfigs(false)
        console.log("% OcrManager 初始化OCR管理器完毕！")
    }

    // ========================= 【内部】 =========================
    property string apiKey: "" // 当前选定的apiKey
    property var deployDict: {} // 存放 部署了配置的页面

    Component.onCompleted: {
        deployDict = {}
    }
}