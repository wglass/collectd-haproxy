import unittest

from mock import Mock, patch


from collectd_haproxy import compat


class CompatTests(unittest.TestCase):

    @patch.object(compat, "PY3", False)
    def test_iteritems_python2_uses_iteritems(self):
        dictionary = Mock()

        self.assertEqual(
            compat.iteritems(dictionary),
            dictionary.iteritems.return_value
        )

    @patch.object(compat, "PY3", True)
    def test_iteritems_python3_uses_items(self):
        dictionary = Mock()

        self.assertEqual(
            compat.iteritems(dictionary),
            dictionary.items.return_value
        )

    @patch.object(compat, "PY3", True)
    def test_coerce_long_python3_uses_int(self):
        self.assertEqual(compat.coerce_long("123"), int("123"))
