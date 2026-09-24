' Double-clickable launcher for the tray indicator.
' Uses pythonw.exe so no console window appears.

Option Explicit

Dim shell, fso, scriptDir, target, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
target = scriptDir & "\run_monitor.py"

If Not fso.FileExists(target) Then
    MsgBox "Cannot find run_monitor.py next to this launcher." & vbCrLf & _
           "Expected: " & target, vbExclamation, "Claude Token Monitor"
    WScript.Quit 1
End If

shell.CurrentDirectory = scriptDir
command = "pythonw.exe """ & target & """"

On Error Resume Next
shell.Run command, 0, False
If Err.Number <> 0 Then
    On Error GoTo 0
    ' pythonw is not on PATH; fall back to python with a hidden window.
    shell.Run "python.exe """ & target & """", 0, False
End If
On Error GoTo 0
