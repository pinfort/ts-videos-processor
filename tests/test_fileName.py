from datetime import datetime

from main.component.fileName import FileName

def test_filename():
    original = "[200101-0010][GR16][TOKYO MX1][a]これはたいとる"
    filename: FileName = FileName(original)
    assert filename.recorded_at == datetime(year=2020, month=1, day=1, hour=0, minute=10, second=0)
    assert filename.channel == "GR16"
    assert filename.channelName == "TOKYO MX1"
    assert filename.title == "[a]これはたいとる"
