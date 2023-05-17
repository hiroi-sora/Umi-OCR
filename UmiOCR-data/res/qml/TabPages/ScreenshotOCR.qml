// ==============================================
// =============== 功能页：截屏OCR ===============
// ==============================================

import QtQuick 2.15
import QtQuick.Controls 2.15

import "../Widgets"

Item {
    anchors.fill: parent

    DoubleColumnLayout {
        anchors.fill: parent
        initSplitterX: 0.5
        hideWidth: 50

        leftItem: Item{
            anchors.fill: parent

            Panel{
            anchors.fill: parent
        }
        }
        rightItem: Panel{
            anchors.fill: parent
        }
    }
}