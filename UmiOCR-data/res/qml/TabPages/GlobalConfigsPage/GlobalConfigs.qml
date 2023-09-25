// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
import GlobalConfigsConnector 1.0
import "../../Configs"
import "../../ApiManager"

Configs {
    category_: "Global"

    // ========================= 【全局配置项】 =========================
    configDict: {

        // 快捷方式
        "shortcut": {
            "title": qsTr("快捷方式"),
            "type": "group",

            "desktop": {
                "title": qsTr("桌面"),
                "default": false,
                "onChanged": (newFlag, oldFlag)=>{
                    if(oldFlag !== undefined)
                        return changeShortcut(newFlag, "desktop")
                },
            },
            "startMenu": {
                "title": qsTr("开始菜单"),
                "default": false,
                "onChanged": (newFlag, oldFlag)=>{
                    if(oldFlag !== undefined)
                        return changeShortcut(newFlag, "startMenu")
                },
            },
            "startup": {
                "title": qsTr("开机自启"),
                "default": false,
                "onChanged": (newFlag, oldFlag)=>{
                    if(oldFlag !== undefined)
                        return changeShortcut(newFlag, "startup")
                },
            },
        },

        // 界面和外观
        "ui": {
            "title": qsTr("界面和外观"),
            "type": "group",

            "i18n": getI18n,
            "theme": {
                "title": qsTr("主题"),
                "optionsList": qmlapp.themeManager.themeList, // 从全局主题管理器中取列表
                "onChanged": (val)=>{
                    qmlapp.themeManager.switchTheme(val)
                },
            },
            "opengl": {
                "title": qsTr("渲染器"),
                "save": false,
                "default": getOpengl(),
                "optionsList": [
                    ["AA_UseSoftwareOpenGL", qsTr("关闭硬件加速")],
                    ["AA_UseDesktopOpenGL", "Desktop OpenGL"],
                    ["AA_UseOpenGLES", "OpenGL ES"],
                ],
                "toolTip": qsTr("若出现界面闪烁、元素错位等界面异常，尝试切换渲染器或者关闭硬件加速"),
                "onChanged": (opt, old)=>{
                    old!==undefined && setOpengl(opt)
                },
            },
            "disableEffect": {
                "title": qsTr("禁用美化效果"),
                "default": false,
                "toolTip": qsTr("在低配置机器上，禁用动画、阴影等效果可减少部分资源占用"),
                "onChanged": (flag)=>{
                    qmlapp.enabledEffect = !flag
                },
            },
        },

        // 窗口
        "window": {
            "title": qsTr("窗口"),
            "type": "group",

            "startupInvisible": {
                "title": qsTr("启动时缩小到任务栏"),
                "default": false,
                "toolTip": qsTr("软件启动时，不弹出主窗口"),
            },
            "isMainWindowTop": {
                "title": qsTr("窗口置顶"),
                "default": false,
                "toolTip": qsTr("捷径：窗口左上角图钉"),
                "onChanged": (val)=>{
                    mainWindowRoot.isMainWindowTop = val
                },
            },
            "barIsLock": {
                "title": qsTr("锁定标签栏"),
                "default": false,
                "toolTip": qsTr("捷径：窗口右上角小锁"),
                "onChanged": (val)=>{
                    qmlapp.tab.barIsLock = val
                },
            },
            "closeWin2Hide": {
                "title": qsTr("关闭主窗口时"),
                "optionsList": [
                    [true, qsTr("最小化到系统托盘")],
                    [false, qsTr("退出应用")],
                ],
            },
            "simpleNotificationType": utilsDicts.getSimpleNotificationType(true),
        },

        // 服务
        "server": {
            "title": qsTr("服务"),
            "type": "group",
            "advanced": true,

            "port": {
                "title": qsTr("端口"),
                "isInt": true,
                "default": 1224,
                "max": 65535,
                "min": 1,
                // 保存数值，只是用于前端展示。实际端口号由pre_config保存。
                "toolTip": qsTr("用于本地进程通信、命令行指令传输、http接口"),
                "onChanged": (port, old)=>{
                    old!==undefined && setServerPort(port)
                },
            },
        },

        // OCR接口全局设定
        "ocr": ocrManager.globalOptions,
    }

    // ========================= 【全局单例，通过 qmlapp.globalConfigs.xxx 访问】 =========================

    OcrManager { id: ocrManager } // OCR管理器 qmlapp.globalConfigs.ocrManager
    UtilsConfigDicts { id: utilsDicts } // 通用配置项 qmlapp.globalConfigs.utilsDicts
    GlobalConfigsConnector { id: globalConfigConn } // 全局设置连接器

    property alias ocrManager: ocrManager
    property alias utilsDicts: utilsDicts
    property bool isPortInit: false // 标记端口号是否初始化完毕

    Component.onCompleted: {
        ocrManager.init()
        console.log("% GlobalConfig 初始化全局配置完毕！")
        // 延迟执行
        Qt.callLater(()=>{
            setQmlToCmd()  // 将qml模块字典传入cmd执行模块
            // 启动web服务
            globalConfigConn.runUmiWeb(this, "setRealPort")
        })
    }

    // 添加/删除快捷方式
    function changeShortcut(flag, position) {
        if(flag) {
            let res = globalConfigConn.createShortcut(position)
            if(res) {
                qmlapp.popup.simple(qsTr("成功添加快捷方式"), "")
            }
            else {
                qmlapp.popup.message(qsTr("添加快捷方式失败"), qsTr("请以管理员权限运行软件，重新操作。"), "error")
                return true // 阻止变化
            }
        }
        else {
            let res = globalConfigConn.deleteShortcut(position)
            if(res > 0) {
                qmlapp.popup.simple(qsTr("成功移除 %1 个快捷方式").arg(res), "")
            }
            else {
                qmlapp.popup.message(qsTr("提示"), qsTr("没有找到可移除的快捷方式。"), "warning")
            }
        }
    }

    // 询问重启软件
    function askRebootApp(msg) {
        const callback = (flag)=>{ flag&&Qt.quit() }
        const argd = {yesText: qsTr("立刻关闭软件"), noText: qsTr("稍后")}
        qmlapp.popup.dialog("", msg, callback, "", argd)
    }

    // 初始化i18n参数
    property var getI18n: _getI18n() // 转为静态
    function _getI18n() {
        const info = globalConfigConn.i18nGetInfos()
        const lang = info[0]
        const langDict = info[1]
        let optionsList = []
        for(let code in langDict) {
            const text = langDict[code][0]
            optionsList.push([code, text])
        }
        return {
            "title": "语言 / Language",
            "save": false,
            "default": lang,
            "optionsList": optionsList,
            "onChanged": changeI18n,
        }
    }
    // 改变i18n
    function changeI18n(lang, old) {
        if(old===undefined) return
        const flag = globalConfigConn.i18nSetLanguage(lang)
        if(flag) {
            const msg = "UI language has been modified. Please reload Umi-OCR to take effect.\n\n已修改界面语言，请重启软件生效。"
            askRebootApp(msg)
        }
    }

    // 获取渲染器
    function getOpengl() {
        return globalConfigConn.getOpengl()
    }
    // 设置渲染器
    function setOpengl(opt) {
        globalConfigConn.setOpengl(opt)
        const msg = qsTr("渲染器变更 将在重启软件后生效")
        askRebootApp(msg)
    }

    // 设置服务端口号
    function setServerPort(port) {
        if(port===null || port===undefined) {
            qmlapp.popup.simple(qsTr("端口号不合法"), "")
            return
        }
        if(isPortInit) { // 用户修改，忽略系统修改
            globalConfigConn.setServerPort(port)
            qmlapp.popup.simple(qsTr("端口号改为%1").arg(port), qsTr("将在重启软件后生效"))
        }
    }
    // py回调，设置当前实际的端口号
    function setRealPort(port1) {
        const port2 = getValue("server.port")
        if(port1 !== port2) {
            setValue("server.port", port1, true)
            if(advanced) {
                const msg = qsTr("原端口号%1被占用，\n切换为新端口号%2。\n\n若不想看到此通知，请在全局设置关闭高级模式。").arg(port2).arg(port1)
                qmlapp.popup.message("", msg, "")
            }
            else {
                console.log(`原端口号${port1}被占用，\n切换为新端口号${port2}。`)
            }
        }
        isPortInit = true
    }
    // 将qml模块字典传入cmd执行模块
    function setQmlToCmd() {
        const moduleDict = {
            "GlobalConfigs": this,
            "MainWindow": qmlapp.mainWin,
            "TabViewManager": qmlapp.tab,
        }
        globalConfigConn.setQmlToCmd(moduleDict)
    }
}