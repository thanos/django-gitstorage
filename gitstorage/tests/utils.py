# Copyright Bors LTD
# This file is part of django-gitstorage.
#
#    Django-gitstorage is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Django-gitstorage is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-gitstorage.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import tempfile

from django.conf import settings


class NewRepositoryMixin(object):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp("gitstorage")
        self.location = os.path.join(self.tempdir, "scratch")
        settings.GIT_STORAGE_ROOT = self.location

    def tearDown(self):
        delattr(settings, 'GIT_STORAGE_ROOT')
        shutil.rmtree(self.tempdir, ignore_errors=True)


class VanillaRepositoryMixin(object):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp("gitstorage")
        self.location = os.path.join(self.tempdir, "vanilla")
        shutil.copytree(os.path.join(os.path.dirname(__file__), "vanilla"), self.location)
        settings.GIT_STORAGE_ROOT = self.location

    def tearDown(self):
        delattr(settings, 'GIT_STORAGE_ROOT')
        shutil.rmtree(self.tempdir, ignore_errors=True)
