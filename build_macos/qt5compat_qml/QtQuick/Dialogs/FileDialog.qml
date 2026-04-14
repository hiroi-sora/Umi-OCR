// Qt5 FileDialog compatibility wrapper for Qt6
// Maps Qt5 properties (folder, selectExisting, selectFolder, selectMultiple, fileUrls, nameFilters)
// to their Qt6 equivalents (currentFolder, fileMode, selectedFiles, nameFilters)

import QtQuick
import QtQuick.Dialogs as Dialogs6

Dialogs6.FileDialog {
    id: root

    // Qt5 property: folder (URL) → Qt6: currentFolder
    property url folder: ""
    onFolderChanged: {
        if (folder.toString() !== "") {
            currentFolder = folder
        }
    }

    // Qt5 property: shortcuts.desktop etc.
    // In Qt6, StandardPaths is used instead. Provide a basic "shortcuts" object.
    readonly property QtObject shortcuts: QtObject {
        readonly property url desktop: StandardPaths.writableLocation(StandardPaths.DesktopLocation)
        readonly property url home: StandardPaths.writableLocation(StandardPaths.HomeLocation)
        readonly property url documents: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        readonly property url pictures: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
    }

    // Qt5 properties: selectExisting, selectFolder, selectMultiple → Qt6: fileMode
    property bool selectExisting: true
    property bool selectFolder: false
    property bool selectMultiple: false

    fileMode: {
        if (selectFolder)
            return FileDialog.OpenFolder
        if (selectMultiple)
            return FileDialog.OpenFiles
        if (selectExisting)
            return FileDialog.OpenFile
        return FileDialog.SaveFile
    }

    // Qt5 property: fileUrls (list of URLs) → Qt6: selectedFiles
    readonly property var fileUrls: selectedFiles
}
