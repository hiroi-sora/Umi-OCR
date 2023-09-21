// =========================================
// =============== 全局配置项 ===============
// =========================================

import QtQuick 2.15
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

        // OCR接口全局设定
        "ocr": ocrManager.globalOptions,
    }

    // ========================= 【全局单例，通过 qmlapp.globalConfigs.xxx 访问】 =========================

    OcrManager { id: ocrManager } // OCR管理器 qmlapp.globalConfigs.ocrManager
    UtilsConfigDicts { id: utilsDicts } // 通用配置项 qmlapp.globalConfigs.utilsDicts

    property alias ocrManager: ocrManager
    property alias utilsDicts: utilsDicts

    Component.onCompleted: {
        ocrManager.init()
        console.log("% GlobalConfig 初始化全局配置完毕！")
    }

    // 添加/删除快捷方式
    function changeShortcut(flag, position) {
        if(flag) {
            let res = qmlapp.utilsConnector.createShortcut(position)
            if(res) {
                qmlapp.popup.simple(qsTr("成功添加快捷方式"), "")
            }
            else {
                qmlapp.popup.message(qsTr("添加快捷方式失败"), qsTr("请以管理员权限运行软件，重新操作。"), "error")
                return true // 阻止变化
            }
        }
        else {
            let res = qmlapp.utilsConnector.deleteShortcut(position)
            if(res > 0) {
                qmlapp.popup.simple(qsTr("成功移除 %1 个快捷方式").arg(res), "")
            }
            else {
                qmlapp.popup.message(qsTr("提示"), qsTr("没有找到可移除的快捷方式。"), "warning")
            }
        }
    }
    // 初始化i18n参数
    property var getI18n: _getI18n() // 转为静态
    function _getI18n() {
        const info = qmlapp.utilsConnector.i18nGetInfos()
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
        const flag = qmlapp.utilsConnector.i18nSetLanguage(lang)
        if(flag) {
            const callback = (flag)=>{ flag&&Qt.quit() }
            const msg = "UI language has been modified. Please reload Umi-OCR to take effect.\n\n已修改界面语言，请重启软件生效。"
            const argd = {yesText: "Exit Now", noText:"Later"}
            qmlapp.popup.dialog("Success", msg, callback, "", argd)
        }
    }
    // 获取渲染器
    function getOpengl() {
        return qmlapp.utilsConnector.getOpengl()
    }
    // 设置渲染器
    function setOpengl(opt) {
        qmlapp.utilsConnector.setOpengl(opt)
        const callback = (flag)=>{ flag&&Qt.quit() }
        const msg = qsTr("渲染器选项将在重启软件后生效")
        const argd = {yesText: qsTr("立刻关闭软件")}
        qmlapp.popup.dialog("", msg, callback, "", argd)
    }
}