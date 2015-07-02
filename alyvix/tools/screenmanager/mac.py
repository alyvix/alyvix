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
import Quartz
import Quartz.CoreGraphics as CG
import objc
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

        # Create screenshot as CGImage
        image = CG.CGWindowListCreateImage(
            CG.CGRectInfinite,
            CG.kCGWindowListOptionOnScreenOnly,
            CG.kCGNullWindowID,
            CG.kCGWindowImageDefault)


        width = CG.CGImageGetWidth(image);
        height = CG.CGImageGetHeight(image);

        # Allocate enough space to hold our pixels
        imageData = objc.allocateBuffer(int(4 * width * height))

        # Create the bitmap context
        bitmapContext = CG.CGBitmapContextCreate(
                imageData, # image data we just allocated...
                width, # width
                height, # height
                8, # 8 bits per component
                4 * width, # bytes per pixel times number of pixels wide
                CG.CGImageGetColorSpace(image), # use the same colorspace as the original image
                CG.kCGImageAlphaPremultipliedLast) # use premultiplied alpha

        CG.CGContextDrawImage(bitmapContext, CG.CGRectMake(0, 0, width, height), image)

        #Now your rawData contains the image data in the RGBA8888 pixel format.

        #del bitmapContext

        ret_image = Image.frombuffer(
            "RGBA",
            (width, height),
            imageData,
            "raw",
            "RGBA",
            0,
            1
        )

        #return ret_image
        #ret_image.save('out.jpg')
        ret_image = ret_image.convert('RGB')
        #ret_image.save('out.jpg')


        if return_type == self.get_color_mat:
            return self._get_cv_color_mat(ret_image)
        if return_type == self.get_gray_mat:
            mat = self._get_cv_color_mat(ret_image)
            return self._get_cv_gray_mat(mat)
        else:
            return ret_image