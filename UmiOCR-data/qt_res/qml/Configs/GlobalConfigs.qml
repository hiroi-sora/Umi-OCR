// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
import GlobalConfigsConnector 1.0
import PluginsConnector 1.0
import "../Configs"
import "../ApiManager"

Configs {
    id: gRoot
    category_: "Global"
    autoLoad: false
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
                "optionsList": theme.manager.getOptionsList(), // 从全局主题管理器中取列表
                "onChanged": (val, old)=>{
                    theme.manager.switchTheme(val)
                    if(old)
                        qmlapp.popup.simple(qsTr("切换主题"), val)
                },
            },
            "fontBtn": {
                "title": qsTr("字体"),
                "btnsList": [
                    {
                        "text":qsTr("修改字体"),
                        "onClicked": openFontPanel,
                        "textColorKey":"specialTextColor",
                    },
                ],
            },
            "fontFamily": {
                "default": "Microsoft YaHei",
                "onChanged": (val)=>{ theme.fontFamily = val },
            },
            "dataFontFamily": {
                "default": "Microsoft YaHei",
                "onChanged": (val)=>{ theme.dataFontFamily = val },
            },
            "scale": {
                "title": qsTr("界面与文字大小"),
                "default": 1,
                "optionsList": [
                    [0.5, "50%"],
                    [0.75, "75%"],
                    [0.9, "90%"],
                    [1, "100%"],
                    [1.1, "110%"],
                    [1.25, "125%"],
                    [1.5, "150%"],
                ],
                "onChanged": (val)=>{
                    size_.scale = val
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
            "imgShowOverlay": {
                "title": qsTr("图片预览默认显示叠加层"),
                "default": true,
                "toolTip": qsTr("默认开启/关闭叠加层显示\n对所有图片预览组件生效"),
            }
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
            "hideTrayIcon": {
                "title": qsTr("隐藏托盘图标"),
                "toolTip": qsTr("若要弹出位于后台的软件窗口，请在文件管理器中重复启动软件。\n若要彻底退出软件，请从任务管理器中结束进程。"),
                "default": false,
                "advanced": true,
                "onChanged": changeHideTrayIcon,
            },
            "simpleNotificationType": utilsDicts.getSimpleNotificationType(true),
            "geometry": { // 存放主窗位置大小，字符串格式 "x,y,w,h"
                "type": "var",
                "default": "", // 如： 300,20,500,300
            },
            "messageMemory": { // 存放“不再弹出”的消息弹窗的mid
                "type": "var",
                "default": [], // 如： ["aaa", "bbb"]
            },
            "doubleLayout": { // 存放 Double__Layout 的 hide 信息
                "type": "var",
                "default": {}, // 如： {"ScreenshotOCR1": 0, }
            },
        },

        // 截图
        "screenshot": {
            "title": qsTr("截图"),
            "type": "group",

            "hideWindow": {
                "title": qsTr("截图前隐藏主窗口"),
                "toolTip": qsTr("截图前，如果主窗口处于前台，则隐藏主窗口\n将会延时等待主窗口关闭"),
                "default": true,
            },
            "hideWindowTime": {
                "title": qsTr("隐藏等待时间"),
                "default": 0.2,
                "min": 0,
                "unit": qsTr("秒"),
                "isInt": false,
                "advanced": true,
            },
        },

        // 服务
        "server": {
            "title": qsTr("服务"),
            "type": "group",
            "advanced": true,

            "enable": {
                "title": qsTr("允许HTTP服务"),
                "toolTip": qsTr("Umi-OCR依赖HTTP接口进行本机跨进程通信。如果禁用，将无法使用命令行模式、多开检测等功能。"),
                "default": true,
                "onChanged": (val, old)=>{
                    old!==undefined && qmlapp.popup.simple(qsTr("重启软件后生效"), "")
                },
            },
            "host": {
                "title": qsTr("主机"),
                "optionsList": [
                    ["127.0.0.1", qsTr("仅本地")+" (127.0.0.1)"],
                    ["0.0.0.0", qsTr("任何可用地址")],
                ],
                "onChanged": (val, old)=>{
                    if(old!==undefined) {
                        let msg = val==="0.0.0.0"?qsTr("将允许局域网访问。请开启对应防火墙权限！"):qsTr("将禁止局域网访问。")
                        qmlapp.popup.simple(qsTr("重启软件后生效"), msg)
                    }
                },
            },
            "port": {
                "title": qsTr("端口"),
                "isInt": true,
                "default": 1224,
                "max": 65535,
                "min": 1,
                // 保存数值，只是用于前端展示。实际端口号由pre_config保存。
                "onChanged": (port, old)=>{
                    old!==undefined && setServerPort(port)
                },
            },
        },

        // OCR接口全局设定
        "ocr": undefined,

        // 开发者工具
        "developer": {
            "title": "developer tools",
            "type": "group",
            "advanced": true,

            "textScale": {
                "title": "languageScale (textScale)",
                "isInt": false,
                "default": 1,
                "max": 10,
                "min": 0.1,
                "save": false,
                "onChanged": (val, old)=>{
                    if(old!==undefined)
                        size_.textScale = val
                },
            },
        },
    }

    // ========================= 【全局单例，通过 qmlapp.globalConfigs.xxx 访问】 =========================

    OcrManager { id: ocrManager } // OCR管理器 qmlapp.globalConfigs.ocrManager
    UtilsConfigDicts { id: utilsDicts } // 通用配置项 qmlapp.globalConfigs.utilsDicts
    GlobalConfigsConnector { id: globalConfigConn } // 全局设置连接器
    PluginsConnector { id: pluginsConnector } // 插件全局设置连接器

    property alias ocrManager: ocrManager
    property alias utilsDicts: utilsDicts
    property bool isPortInit: false // 标记端口号是否初始化完毕
    property var fontPanel: undefined // 缓存字体控制面板组件引用

    Component.onCompleted: {
        // 初始化主题
        theme.manager.init()
        // 加载插件
        initPlugins()
        // 初始化配置项
        reload()
        // 检查权限和异常情况
        checkAccess()
        // 应用OCR信息
        if(configDict.ocr)
            ocrManager.init2()
        console.log("% GlobalConfig 初始化全局配置完毕！")
        // 延迟执行
        Qt.callLater(()=>{
            setQmlToCmd()  // 将qml模块字典传入cmd执行模块
            // 启动web服务
            const enab = getValue("server.enable")
            if(enab) {
                const host = getValue("server.host")
                globalConfigConn.runUmiWeb(gRoot, "setRealPort", host)
            }
        })
    }

    // 检查权限和异常情况
    function checkAccess() {
        let msg = globalConfigConn.checkAccess()
        if(msg.length > 0) {
            msg += "\n" + qsTr("请尝试更换软件路径！")
            qmlapp.popup.message(qsTr("配置文件读写异常"), msg, "error")
        }
    }

    // 初始化插件
    function initPlugins() {
        // 初始化插件
        let pluginInfos = pluginsConnector.init()
        if(!pluginInfos) return false // 没有加载插件
        // 记录失败信息
        if(pluginInfos.errors && Object.keys(pluginInfos.errors).length > 0) {
            const errs = pluginInfos.errors
            let msg = ""
            for (let key in errs) {
                msg += `${key}: ${errs[key]}\n`
            }
            qmlapp.popup.message(qsTr("插件加载失败"), msg, "error")
        }
        // 成功的插件
        if(pluginInfos.options) {
            // 初始化OCR管理器
            if(pluginInfos.options.ocr)
                ocrManager.init1(pluginInfos.options.ocr)
        }
    }

    // 添加/删除快捷方式
    function changeShortcut(flag, position) {
        if(flag) {
            const res = globalConfigConn.createShortcut(position)
            if(res === "[Success]") {
                qmlapp.popup.simple(qsTr("成功添加快捷方式"), "")
            }
            else {
                qmlapp.popup.message(qsTr("添加快捷方式失败"), res, "error")
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
            qmlapp.popup.simple(qsTr("重启软件后生效"), qsTr("端口号改为%1").arg(port))
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

    // 打开字体控制板
    function openFontPanel() {
        if(fontPanel) {
            fontPanel.visible = true
        }
    }

    // 改变托盘图标显示
    function changeHideTrayIcon(flag, old) {
        if(flag && old===false) {
            qmlapp.popup.messageMemory("changeHideTrayIcon", "", configDict.window.hideTrayIcon.toolTip)
        }
        qmlapp.systemTray.visible = !flag
    }
}