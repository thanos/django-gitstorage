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

from django.test.testcases import TestCase

from gitstorage import factories
from gitstorage import models
from gitstorage import utils
from gitstorage import wrappers
from gitstorage.tests import utils as tests_utils


class BlobMetadataManagerTestCase(tests_utils.VanillaRepositoryMixin, TestCase):

    def guess_mimetype_from_name(self):
        mimetype = models.guess_mimetype(name="my_pic.jpg")
        self.assertEqual(mimetype, "image/jpeg")

    def test_create_from_content(self):
        repository = wrappers.Repository(self.location)
        blob = repository['257cc5642cb1a054f08cc83f2d943e56fd3ebe99']
        mimetype = models.guess_mimetype(buffer=blob.data)
        self.assertEqual(mimetype, "text/plain")


class BlobMetadataTestCase(TestCase):

    def setUp(self):
        self.metadata = factories.BlobMetadataFactory(id="c0d11342c4241087e3c126f7666d618586e39068",
                                                      mimetype="image/jpeg")

    def test_str(self):
        self.assertEqual(str(self.metadata), "c0d11342c4241087e3c126f7666d618586e39068 type=image/jpeg")


class TreeMetadataTestCase(TestCase):

    def setUp(self):
        self.metadata = factories.TreeMetadataFactory.build(id="c0d11342c4241087e3c126f7666d618586e39068")

    def test_str(self):
        self.assertEqual(str(self.metadata), "c0d11342c4241087e3c126f7666d618586e39068")


class TreePermissionManagerTestCase(TestCase):

    def setUp(self):
        self.anonymous = factories.AnonymousUserFactory()
        self.superuser = factories.SuperUserFactory()
        self.user = factories.UserFactory(username="john_doe")
        self.other_user = factories.UserFactory(username="alice_bob")
        self.permission = factories.TreePermissionFactory(parent_path="my/path", name="my_name", user=self.user)

    def test_current_permissions(self):
        path = utils.Path("my/path/my_name")
        current_permissions = models.TreePermission.objects.current_permissions(path)
        self.assertQuerysetEqual(current_permissions, ["<TreePermission: john_doe on my/path/my_name>"])

        path = utils.Path("my/path")
        current_permissions = models.TreePermission.objects.current_permissions(path)
        self.assertQuerysetEqual(current_permissions, [])

    def test_allowed_names(self):
        allowed_names = models.TreePermission.objects.allowed_names(self.anonymous, "my/path")
        self.assertEqual(list(allowed_names), [])

        allowed_names = models.TreePermission.objects.allowed_names(self.superuser, "my/path")
        self.assertIsNone(allowed_names)

        allowed_names = models.TreePermission.objects.allowed_names(self.user, "my/path")
        self.assertEqual(list(allowed_names), ["my_name"])

        allowed_names = models.TreePermission.objects.allowed_names(self.other_user, "my/path")
        self.assertEqual(list(allowed_names), [])

    def test_is_allowed(self):
        path = utils.Path("my/path/my_name")
        self.assertFalse(models.TreePermission.objects.is_allowed(self.anonymous, path))
        self.assertTrue(models.TreePermission.objects.is_allowed(self.superuser, path))
        self.assertTrue(models.TreePermission.objects.is_allowed(self.user, path))
        self.assertFalse(models.TreePermission.objects.is_allowed(self.other_user, path))

    def test_add(self):
        models.TreePermission.objects.add([self.user, self.other_user], utils.Path("my/path/my_name"))
        self.assertQuerysetEqual(models.TreePermission.objects.order_by("pk"),
                                 ["<TreePermission: john_doe on my/path/my_name>",
                                  "<TreePermission: alice_bob on my/path/my_name>"])

    def test_remove(self):
        models.TreePermission.objects.remove([self.user], utils.Path("my/path/my_name"))
        # Nothing raised
        models.TreePermission.objects.remove([self.other_user], utils.Path("my/path/my_name"))
