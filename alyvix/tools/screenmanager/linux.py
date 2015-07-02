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

import Image
import numpy
from gi.repository import Gtk, Gdk, GdkPixbuf
import cairo
from .base import ScreenManagerBase


class ScreenManager(ScreenManagerBase):

    def __init__(self):
        super(ScreenManager, self).__init__()

    def grab_desktop(self, return_type=0):
        """
        grab desktop screenshot.

        :type return_type: int
        :param return_type: 0 for pil image, 1 for color matrix, 2 for gray matrix
        :rtype: numpy.ndarray or Image.Image
        :return: the screenshot image
        """

        ret_image = None

        root_win = Gdk.get_default_root_window()

        width = root_win.get_width()
        height = root_win.get_height()

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        #ims = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        pb = Gdk.pixbuf_get_from_window(root_win, 0, 0, width, height)

        cr = cairo.Context(ims)
        Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
        cr.paint()

        # Cairo has ARGB. Convert this to RGB for PIL which supports only RGB or
        # RGBA.
        argbArray = numpy.fromstring( ims.get_data(), 'c' ).reshape( -1, 4 )
        rgbArray = argbArray[ :, 2::-1 ]
        pilData = rgbArray.reshape( -1 ).tostring()

        ret_image = Image.frombuffer("RGB",( ims.get_width(),ims.get_height() ), pilData ,"raw","RGB",0,1)

        ret_image = ret_image.convert("RGB")

        #return ret_image

        if return_type == self.get_color_mat:
            return self._get_cv_color_mat(ret_image)
        if return_type == self.get_gray_mat:
            mat = self._get_cv_color_mat(ret_image)
            return self._get_cv_gray_mat(mat)
        else:
            return ret_image