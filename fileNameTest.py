from datetime import datetime
import unittest

from component.fileName import FileName

class FileNameTest(unittest.TestCase):
    def test_filename(self):
        original = "[200101-0010][GR16][TOKYO MX1][a]これはたいとる"
        filename: FileName = FileName(original)
        self.assertEqual(filename.recorded_at, datetime(year=2020, month=1, day=1, hour=0, minute=10, second=0))
        self.assertEqual(filename.channel, "GR16")
        self.assertEqual(filename.title, "[a]これはたいとる")

if __name__  == '__main__':
    unittest.main()
