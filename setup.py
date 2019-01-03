# -*- coding: utf-8 -*-
import shutil
from setuptools import setup, find_packages
import distutils.command.install
from setuptools.command.install import install
import os
import sys
import distutils.dir_util
from shutil import copyfile
from distutils import log

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

#datadir = os.path.join('share','wxPython2.8-win64-unicode-2.8.12.1-py2.7')
#datafiles = [(d, [os.path.join(d,f) for f in files])
#    for d, folders, files in os.walk(datadir)]



def _pre_install():
      print("Verifying architecture.")

      if sys.platform != 'win32':
            raise SystemError("This package can only be installed on Windows systems.")

      is_64bits = sys.maxsize > 2**32

      if is_64bits is False:
            raise SystemError("This package can only be installed on 64-bit environment.")
            
def _post_install():
    python_home = sys.exec_prefix
    scripts_dir = python_home + os.sep + "Scripts"
    dlls_dir = python_home + os.sep + "DLLs"
    site_packages_dir = python_home + os.sep + "Lib" + os.sep + "site-packages"
    alyvix_dir = site_packages_dir + os.sep + "alyvix"
    external_pkgs_dir = alyvix_dir + os.sep + "extra" + os.sep + "_external_pkgs"

    src_dlls_dir = external_pkgs_dir + os.sep + "win64\\python-tesseract-0.9-0.4.win-amd64-py2.7\\DATA\\DLLS"
    src_site_dir = external_pkgs_dir + os.sep + "win64\\python-tesseract-0.9-0.4.win-amd64-py2.7\\PLATLIB"

    distutils.dir_util.copy_tree(src_dlls_dir, dlls_dir, verbose=1)
    distutils.dir_util.copy_tree(src_site_dir, site_packages_dir, verbose=1)

    src_scripts_dir = external_pkgs_dir + os.sep + "win64\\wxPython2.8-win64-unicode-2.8.12.1-py2.7\\SCRIPTS"
    src_site_dir = external_pkgs_dir + os.sep + "win64\\wxPython2.8-win64-unicode-2.8.12.1-py2.7\\PURELIB"

    distutils.dir_util.copy_tree(src_scripts_dir, scripts_dir, verbose=1)
    distutils.dir_util.copy_tree(src_site_dir, site_packages_dir, verbose=1)
    copyfile(external_pkgs_dir + os.sep + "win64\\wxPython2.8-win64-unicode-2.8.12.1-py2.7\\wx.pth", site_packages_dir + os.sep + "wx.pth")

    src_dlls_dir = external_pkgs_dir + os.sep + "win64\\autohotkey-1.1.13"
    distutils.dir_util.copy_tree(src_dlls_dir, dlls_dir, verbose=1)

    copyfile(external_pkgs_dir + os.sep + "win64\\sip.pyd", site_packages_dir + os.sep + "sip.pyd")

    src_scripts_dir = external_pkgs_dir + os.sep + "winAll\\alyvix-utilities"
    distutils.dir_util.copy_tree(src_scripts_dir, scripts_dir, verbose=1)

    copyfile(external_pkgs_dir + os.sep + "winAll\\alyvix_pybot.bat", scripts_dir + os.sep + "alyvix_pybot.bat")
    copyfile(external_pkgs_dir + os.sep + "winAll\\images2gif.py", site_packages_dir + os.sep + "images2gif.py")
    copyfile(external_pkgs_dir + os.sep + "winAll\\alyvix.pth", site_packages_dir + os.sep + "alyvix.pth")
    
    src_site_dir = external_pkgs_dir + os.sep + "winAll\\robotide"

    distutils.dir_util.copy_tree(src_site_dir, site_packages_dir + os.sep + "robotide", verbose=1)

    import win32com.client
    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(scripts_dir + os.sep + '\\ride.lnk')
    scut.TargetPath = '"' + python_home + '\\pythonw.exe"'
    scut.Arguments = '-c "from robotide import main; main()"'
    scut.Save()

    shutil.rmtree(external_pkgs_dir)
    
    
     
#class _CustomInstall(distutils.command.install.install):
class _CustomInstall(install):
    def run(self):
        _pre_install()
        install.run(self)
        _post_install()
        
long_description = """\
Alyvix is a synthetic monitoring system based on computer vision. It automates any application, interacting with GUIs exactly as a human would do. It measures all transactions and visualizes their performances in your monitoring system. It reports HTML pages containing the details of each test case step, so that it provides certifications on end user perceived quality of IT services. Browse the Alyvix documentation here: http://www.alyvix.com/doc/
"""
        
setup(
    name='alyvix',
    version='2.7.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='GPL V3',
    long_description=long_description,
    cmdclass={ 'install': _CustomInstall }



)