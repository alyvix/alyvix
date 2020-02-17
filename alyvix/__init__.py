# Alyvix allows you to automate and monitor all types of applications
# Copyright (C) 2015 Alan Pipitone
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Developer: Alan Pipitone (Violet Atom) - http://www.violetatom.com/
# Supporter: Wuerth Phoenix - http://www.wuerth-phoenix.com/
# Official website: http://www.alyvix.com/


from alyvix.tools.info import InfoManager
from alyvix.tools.screen import ScreenManager
import sys


#update all info
info_manager = InfoManager()
info_manager.update()

screen_manager = ScreenManager()
scaling_factor = screen_manager.get_scaling_factor_before_start()

if sys.platform == "linux" or sys.platform == "linux2":
    #linux...
    pass
elif sys.platform == "darwin":
    #mac...
    pass
elif sys.platform == "win32":
    #window...
    if scaling_factor > 1:
        import winreg

        python_interpreter = sys.executable
        regedit_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
        key_name = python_interpreter


        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                          regedit_path, 0,
                                          winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, key_name)
            winreg.CloseKey(registry_key)
        except WindowsError:
            try:
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, regedit_path)
                registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regedit_path, 0,
                                              winreg.KEY_WRITE)
                winreg.SetValueEx(registry_key, key_name, 0, winreg.REG_SZ, "~HIGHDPIAWARE")
                winreg.CloseKey(registry_key)
                print("Scaling factor setup completed. Please restart Alyvix.")
                sys.exit(2)
            except WindowsError:
                pass
