import sys
import win32com.client
ws = win32com.client.Dispatch("wscript.shell")
scut = ws.CreateShortcut(sys.argv[1] + '\\ride.lnk')
scut.TargetPath = '"' + sys.argv[2] + '\\pythonw.exe"'
scut.Arguments = '-c "from robotide import main; main()"'
scut.Save()