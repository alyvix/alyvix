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

screenshot_of_last_obj_found = None


class CacheManager():

    def GetLastObjFoundFullImg(self):
        """
        get the last image where the object was successfully found.

        :rtype: numpy.ndarray
        :return: the gray image
        """
        global screenshot_of_last_obj_found
        return screenshot_of_last_obj_found

    def SetLastObjFoundFullImg(self, image):
        """
        set the last image where the object was successfully found.

        :type image: numpy.ndarray
        :param image: the gray image
        """
        global  screenshot_of_last_obj_found
        screenshot_of_last_obj_found = image.copy()


