"""Time utilities for PicoWeather with offline support."""
import time

try:
    import ntptime  # type: ignore
except Exception:
    ntptime = None  # type: ignore


class TimeManager:
    def __init__(self):
        self._offset = 0  # seconds
        self._ntp_synced = False

    def sync_ntp(self):
        if ntptime is None:
            self._ntp_synced = False
            return False
        try:
            ntptime.settime()
            self._ntp_synced = True
            self._offset = 0
            return True
        except Exception:
            self._ntp_synced = False
            return False

    def adjust_time_minutes(self, minutes):
        self._offset += minutes * 60

    def _now_tuple(self):
        t = time.localtime(time.time() + self._offset)
        return t

    def now(self):  # Return a tuple similar to time.localtime()
        return self._now_tuple()

    def formatted_now(self):
        t = self._now_tuple()
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6])
