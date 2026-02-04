"""
Time Driver - Time management with RTC and NTP synchronization
Handles all time operations including manual adjustment and NTP sync
"""

import time
import utime
import machine


class TimeDriver:
    """Time management driver with RTC and NTP support"""
    
    def __init__(self, config, network_driver=None):
        self.config = config
        self.network_driver = network_driver
        self.rtc = machine.RTC()
        
        # Time settings from config
        time_config = config.get("time", {})
        self.timezone = time_config.get("timezone", 0)  # Hours from UTC
        self.auto_sync = time_config.get("auto_sync", True)
        self.last_sync_attempt = 0
        self.last_sync_success = 0
        self.sync_interval = 3600 * 1000  # 1 hour in milliseconds
        
        # Manual time settings from config
        self.manual_time_set = False
        self.manual_year = time_config.get("manual_year", 2024)
        self.manual_month = time_config.get("manual_month", 1)
        self.manual_day = time_config.get("manual_day", 1)
        self.manual_hour = time_config.get("manual_hour", 12)
        self.manual_minute = time_config.get("manual_minute", 0)
        self.manual_second = time_config.get("manual_second", 0)
        
        # NTP settings from config
        wifi_config = config.get("wifi", {})
        self.ntp_server = wifi_config.get("ntp_server", "pool.ntp.org")
        
        # Status tracking
        self.initialized = False
        self.error_count = 0
        self.has_valid_time = False
        
        self._initialize()
    
    def _initialize(self):
        """Initialize time system"""
        try:
            # First check if RTC has valid time (not default 2000-01-01)
            current_time = self.rtc.datetime()
            year, month, day = current_time[0], current_time[1], current_time[2]
            
            # Check if RTC time is reasonable (not default 2000-01-01 or earlier)
            if year < 2021:  # Year seems too old or default
                print("[TIME] RTC has invalid/default time, setting from config...")
                # Set from config values
                success = self.set_manual_time(
                    self.manual_year, self.manual_month, self.manual_day,
                    self.manual_hour, self.manual_minute, self.manual_second
                )
                if success:
                    print(f"[TIME] Time set from config: {self.get_formatted_time()}")
                    self.has_valid_time = True
                else:
                    print("[TIME] Failed to set time from config")
                    self.has_valid_time = False
            else:
                print(f"[TIME] RTC has valid time: {self.get_formatted_time()}")
                self.has_valid_time = True
                self.manual_time_set = True
            
            self.initialized = True
            print(f"[TIME] Time driver initialized, timezone: {self.timezone}")
            
        except Exception as e:
            self.error_count += 1
            print(f"[TIME] Initialization error: {e}")
            # Try to set basic time as last resort
            try:
                self.rtc.datetime((2024, 1, 1, 0, 12, 0, 0, 0))
                self.has_valid_time = True
            except:
                self.has_valid_time = False
    
    def get_current_time(self):
        """
        Get current time in MicroPython RTC format
        Returns: (year, month, day, weekday, hour, minute, second, microsecond)
        """
        try:
            datetime = self.rtc.datetime()
            
            # Apply timezone offset if needed
            if self.timezone != 0:
                # Simple timezone adjustment (doesn't handle DST)
                hour = datetime[4] + self.timezone
                if hour >= 24:
                    hour -= 24
                    # Would need to adjust day/month/year here
                elif hour < 0:
                    hour += 24
                
                # Create new tuple with adjusted hour
                datetime = (datetime[0], datetime[1], datetime[2], datetime[3],
                          hour, datetime[5], datetime[6], datetime[7])
            
            return datetime
        except Exception as e:
            self.error_count += 1
            print(f"[TIME] RTC read error: {e}")
            # Fallback to system time if RTC fails
            try:
                timestamp = utime.time()
                if timestamp > 1609459200:  # 2021-01-01 (valid timestamp)
                    dt = utime.localtime(timestamp)
                    # MicroPython localtime returns: (year, month, mday, hour, minute, second, weekday, yearday)
                    # RTC expects: (year, month, day, weekday, hour, minute, second, microsecond)
                    return (dt[0], dt[1], dt[2], dt[6], dt[3], dt[4], dt[5], 0)
            except:
                pass
            
            # Ultimate fallback: return config time
            return (self.manual_year, self.manual_month, self.manual_day, 
                    0, self.manual_hour, self.manual_minute, self.manual_second, 0)
    
    def get_formatted_time(self):
        """Get formatted time string"""
        year, month, day, weekday, hour, minute, second, _ = self.get_current_time()
        return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    
    def get_formatted_date(self):
        """Get formatted date string"""
        year, month, day, _, _, _, _, _ = self.get_current_time()
        
        # Try to use locale formatting if available
        try:
            from utils.locale_manager import get_locale
            locale = get_locale()
            if locale:
                format_str = locale.get_display_text("formats.date")
                # Convert format placeholders
                # dd/mm/yyyy -> DD/MM/YYYY
                format_lower = str(format_str).lower()
                # Debug: mostrar qual formato está sendo usado
                print(f"[TIME] Using format: {format_str}")
                
                # Importante: ordem correta DD/MM/YYYY
                if "dd/mm/yyyy" in format_lower:
                    return f"{day:02d}/{month:02d}/{year:04d}"
                elif "mm/dd/yyyy" in format_lower:
                    return f"{month:02d}/{day:02d}/{year:04d}"
                elif "dd-mm-yyyy" in format_lower:
                    return f"{day:02d}-{month:02d}-{year:04d}"
                # Add more formats as needed
        except:
            pass
        
        # Fallback to YYYY-MM-DD
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    def get_time_only(self):
        """Get time only string"""
        _, _, _, _, hour, minute, second, _ = self.get_current_time()
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    
    def get_timestamp(self):
        """Get Unix timestamp"""
        try:
            # Try to get from system time first
            timestamp = utime.time()
            if timestamp > 1609459200:  # Valid timestamp (after 2021-01-01)
                return timestamp
            
            # Calculate from RTC time
            year, month, day, _, hour, minute, second, _ = self.get_current_time()
            
            # Simple Unix timestamp calculation (not accounting for leap years)
            # This is approximate but works for basic timekeeping
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            
            # Calculate days since 1970-01-01
            days = 0
            for y in range(1970, year):
                days += 366 if ((y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)) else 365
            
            for m in range(1, month):
                days += days_in_month[m-1]
                if m == 2 and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
                    days += 1  # Leap day
            
            days += day - 1
            
            # Calculate total seconds
            timestamp = days * 86400 + hour * 3600 + minute * 60 + second
            
            return timestamp
            
        except Exception as e:
            print(f"[TIME] Timestamp calculation error: {e}")
            return 0
    
    def set_manual_time(self, year, month, day, 
                       hour, minute, second = 0):
        """Set time manually"""
        try:
            # Validate values
            if not (2020 <= year <= 2100): 
                print(f"[TIME] Invalid year: {year}")
                return False
            if not (1 <= month <= 12): 
                print(f"[TIME] Invalid month: {month}")
                return False
            if not (1 <= day <= 31): 
                print(f"[TIME] Invalid day: {day}")
                return False
            if not (0 <= hour <= 23): 
                print(f"[TIME] Invalid hour: {hour}")
                return False
            if not (0 <= minute <= 59): 
                print(f"[TIME] Invalid minute: {minute}")
                return False
            if not (0 <= second <= 59): 
                print(f"[TIME] Invalid second: {second}")
                return False
            
            # Calculate weekday (0=Monday, 6=Sunday)
            # Zeller's Congruence algorithm for weekday calculation
            if month < 3:
                month += 12
                year -= 1
            
            century = year // 100
            year_in_century = year % 100
            
            weekday = (day + ((13 * (month + 1)) // 5) + year_in_century + 
                      (year_in_century // 4) + (century // 4) - (2 * century)) % 7
            
            # Convert to MicroPython format (0=Monday, 6=Sunday)
            # Zeller gives 0=Saturday, 1=Sunday, ..., 6=Friday
            # So we adjust: 0=Monday, 1=Tuesday, ..., 6=Sunday
            weekday = (weekday + 1) % 7
            
            # Set RTC time
            self.rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
            
            # Update manual settings
            self.manual_year = year
            self.manual_month = month
            self.manual_day = day
            self.manual_hour = hour
            self.manual_minute = minute
            self.manual_second = second
            self.manual_time_set = True
            self.has_valid_time = True
            
            print(f"[TIME] Manual time set: {self.get_formatted_time()}")
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"[TIME] Manual time set error: {e}")
            return False
    
    def adjust_time(self, minutes = 0, hours = 0, days = 0):
        """Adjust current time by specified amounts"""
        try:
            current_time = self.get_current_time()
            year, month, day, weekday, hour, minute, second, _ = current_time
            
            # Convert to timestamp for easier adjustment
            timestamp = self.get_timestamp()
            
            # Apply adjustments in seconds
            timestamp += days * 86400 + hours * 3600 + minutes * 60
            
            # Convert back to datetime
            # Note: This is simplified - would need proper conversion
            # For now, we'll use the simple method
            
            # Simple adjustment (doesn't handle month/year boundaries well)
            new_minute = minute + minutes
            carry_hours = new_minute // 60
            new_minute = new_minute % 60
            
            new_hour = hour + hours + carry_hours
            carry_days = new_hour // 24
            new_hour = new_hour % 24
            
            new_day = day + days + carry_days
            
            # Handle month/year carry (simplified)
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
                days_in_month[1] = 29  # February in leap year
            
            while new_day > days_in_month[month - 1]:
                new_day -= days_in_month[month - 1]
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                    # Recalculate leap year
                    days_in_month[1] = 29 if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)) else 28
            
            return self.set_manual_time(year, month, new_day, new_hour, new_minute, second)
            
        except Exception as e:
            self.error_count += 1
            print(f"[TIME] Time adjustment error: {e}")
            return False
    
    def sync_with_ntp(self, timeout_ms = 10000):
        """Synchronize time with NTP server using network driver"""
        if not self.auto_sync:
            print("[TIME] Auto sync disabled")
            return False
        
        try:
            current_time_ms = utime.ticks_ms()
            
            # Rate limiting
            if utime.ticks_diff(current_time_ms, self.last_sync_attempt) < 300000:  # 5 minutes
                print("[TIME] Rate limited - waiting before next sync")
                return False
            
            self.last_sync_attempt = current_time_ms
            
            print(f"[TIME] Attempting NTP sync with {self.ntp_server}")
            
            # Try to sync using network driver
            if self.network_driver and self.network_driver.is_connected():
                try:
                    if self.network_driver.sync_ntp_time(self.ntp_server):
                        self.last_sync_success = current_time_ms
                        self.has_valid_time = True
                        print(f"[TIME] NTP sync successful: {self.get_formatted_time()}")
                        return True
                    else:
                        print("[TIME] Network driver NTP sync failed")
                except Exception as nd_error:
                    print(f"[TIME] Network driver NTP error: {nd_error}")
            else:
                print("[TIME] No network connection available for NTP sync")
            
            print("[TIME] NTP sync failed - continuing with current time")
            return False
            
        except Exception as e:
            self.error_count += 1
            print(f"[TIME] NTP sync error: {e}")
            return False
    
    def check_and_sync(self):
        """Check if sync is needed and attempt it"""
        if not self.auto_sync:
            return False
        
        current_time_ms = utime.ticks_ms()
        
        # Check if enough time has passed since last successful sync
        if utime.ticks_diff(current_time_ms, self.last_sync_success) > self.sync_interval:
            return self.sync_with_ntp()
        
        return False
    
    def get_status(self):
        """Get time system status"""
        current_time_ms = utime.ticks_ms()
        
        status = {
            'initialized': self.initialized,
            'has_valid_time': self.has_valid_time,
            'current_time': self.get_formatted_time(),
            'timezone': self.timezone,
            'auto_sync': self.auto_sync,
            'manual_time_set': self.manual_time_set,
            'error_count': self.error_count,
            'ntp_server': self.ntp_server,
            'timestamp': self.get_timestamp()
        }
        
        if self.auto_sync:
            status['last_sync_attempt'] = self.last_sync_attempt
            status['last_sync_success'] = self.last_sync_success
            
            if self.last_sync_success > 0:
                time_since_sync = utime.ticks_diff(current_time_ms, self.last_sync_success) // 1000
                status['time_since_sync'] = f"{time_since_sync}s"
            else:
                status['time_since_sync'] = "Never"
        
        return status
    
    def set_timezone(self, timezone_hours):
        """Set timezone offset from UTC"""
        if -12 <= timezone_hours <= 14:  # Valid timezone range
            self.timezone = timezone_hours
            print(f"[TIME] Timezone set to {timezone_hours}")
    
    def enable_auto_sync(self, enabled):
        """Enable/disable automatic NTP sync"""
        self.auto_sync = enabled
        print(f"[TIME] Auto sync {'enabled' if enabled else 'disabled'}")
    
    def set_ntp_server(self, server):
        """Set NTP server"""
        if server:
            self.ntp_server = server
            print(f"[TIME] NTP server set to {server}")
    
    def set_network_driver(self, network_driver):
        """Set the network driver for NTP synchronization"""
        self.network_driver = network_driver
        print("[TIME] Network driver set for time synchronization")
    
    def set_sync_interval(self, hours):
        """Set NTP sync interval in hours"""
        if hours >= 1:
            self.sync_interval = hours * 3600 * 1000
            print(f"[TIME] Sync interval set to {hours} hours")
    
    def reset_error_count(self):
        """Reset error counter"""
        self.error_count = 0
    
    def is_healthy(self):
        """Check if time system is healthy"""
        # Time driver is considered healthy if initialized and has valid time
        return self.initialized and self.has_valid_time and self.error_count < 10
    
    def force_sync(self):
        """Force immediate NTP sync"""
        self.last_sync_attempt = 0  # Reset to bypass rate limiting
        return self.sync_with_ntp()
    
    def update_from_rtc_device(self):
        """Update time from external RTC device if available"""
        # This would be implemented if an external RTC (like PCF8563) is connected
        # For now, it's a placeholder
        print("[TIME] External RTC update not implemented")
        return False