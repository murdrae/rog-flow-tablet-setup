import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "user.dictation"

  property string state: "idle"
  readonly property bool isRecording: state === "recording"
  readonly property bool isTranscribing: state === "transcribing"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  function update(raw) {
    var data = Util.parseModuleJson(raw)
    root.state = String(data.alt || data.class || "idle")
  }

  Process {
    command: ["bash", "-c", "omarchy-voxtype-status"]
    running: true
    stdout: SplitParser {
      onRead: function(data) { root.update(data) }
    }
  }

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.isRecording ? "󰍬" : (root.isTranscribing ? "󰔟" : "󰍬")
    slotSize: Math.max(38, Style.bar.iconSlot)
    opticalSize: Math.max(28, Style.bar.iconCanvas)
    fontSize: Style.bar.iconFont
    horizontalMargin: 8
    active: root.isRecording
    dimmed: !root.isRecording && !root.isTranscribing
    tooltipText: root.isRecording ? "Recording... (Tap to stop & transcribe)" : (root.isTranscribing ? "Transcribing..." : "Tap to Dictate (Voxtype)")
    onPressed: function(mouseButton) {
      if (mouseButton === Qt.RightButton) {
        root.bar.run("voxtype record cancel")
      } else {
        root.bar.run("voxtype record toggle")
      }
    }
  }
}
