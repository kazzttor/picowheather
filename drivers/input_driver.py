"""
Input Driver - Button and input management for PicoWeather
Handles all button inputs with debouncing and callback system
"""

import time
import utime

from machine import Pin


class Button:
    """Individual button with debouncing and callback support"""
    
    def __init__(self, name, pin_num, pull_up = True):
        self.name = name
        self.pin_num = pin_num
        self.pull_up = pull_up
        self.pin = None
        self.callback = None
        self.long_callback = None
        
        # Debounce settings
        self.debounce_ms = 50
        self.long_press_ms = 2000
        
        # State tracking
        self.last_state = 0
        self.last_press_time = 0
        self.pressed_time = 0
        self.long_pressed = False
        self.press_count = 0
        
        self.detected = False
        self.error_count = 0
    
    def initialize(self):
        """Initialize button pin"""
        try:
            if self.pull_up:
                self.pin = Pin(self.pin_num, Pin.IN, Pin.PULL_UP)
            else:
                self.pin = Pin(self.pin_num, Pin.IN)
            
            self.last_state = self.pin.value()
            self.detected = True
            print(f"[INPUT] Button {self.name} initialized on pin {self.pin_num}")
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"[INPUT] Button {self.name} init error: {e}")
            return False
    
    def set_callback(self, callback):
        """Set normal press callback"""
        self.callback = callback
    
    def set_long_callback(self, callback):
        """Set long press callback"""
        self.long_callback = callback
    
    def check(self):
        """Check button state and return event"""
        if not self.detected or not self.pin:
            return ""
        
        try:
            current_state = self.pin.value()
            current_time = utime.ticks_ms()
            
            # Handle pull-up logic (inverted)
            if self.pull_up:
                is_pressed = (current_state == 0)
            else:
                is_pressed = (current_state == 1)
            
            was_pressed = (self.last_state == 0) if self.pull_up else (self.last_state == 1)
            
            # Button just pressed
            if is_pressed and not was_pressed:
                self.pressed_time = current_time
                self.long_pressed = False
                
            # Button just released
            elif not is_pressed and was_pressed:
                press_duration = utime.ticks_diff(current_time, self.pressed_time)
                
                if press_duration > self.debounce_ms:
                    if not self.long_pressed:
                        # Normal press
                        if self.callback:
                            self.callback()
                        self.press_count += 1
                        return f"{self.name}_press"
            
            # Check for long press while pressed
            elif is_pressed and was_pressed:
                press_duration = utime.ticks_diff(current_time, self.pressed_time)
                
                if (press_duration > self.long_press_ms and not self.long_pressed):
                    self.long_pressed = True
                    if self.long_callback:
                        self.long_callback()
                    return f"{self.name}_long"
            
            self.last_state = current_state
            return ""
            
        except Exception as e:
            self.error_count += 1
            print(f"[INPUT] Button {self.name} check error: {e}")
            return ""
    
    def get_status(self):
        """Get button status"""
        current_state = 0
        if self.pin:
            try:
                current_state = self.pin.value()
            except:
                pass
                
        return {
            'name': self.name,
            'pin': self.pin_num,
            'detected': self.detected,
            'pull_up': self.pull_up,
            'current_state': current_state,
            'pressed': (current_state == 0) if self.pull_up else (current_state == 1),
            'press_count': self.press_count,
            'error_count': self.error_count
        }
    
    def simulate_press(self):
        """Simulate button press (for testing)"""
        if self.callback:
            self.callback()
        self.press_count += 1
    
    def simulate_long_press(self):
        """Simulate long button press (for testing)"""
        if self.long_callback:
            self.long_callback()
    
    def reset_press_count(self):
        """Reset press counter"""
        self.press_count = 0


class InputDriver:
    """Main input driver manager"""
    
    def __init__(self, config, hardware):
        self.config = config
        self.hardware = hardware
        self.buttons = {}
        self.callbacks = {}
        self.enabled = False
        self.last_check = 0
        self.check_interval = 20  # Check every 20ms
        
        self._initialize_buttons()
    
    def _initialize_buttons(self):
        """Initialize all buttons from configuration"""
        buttons_config = self.config.get("buttons", {})
        
        if not buttons_config.get("enabled", True):
            print("[INPUT] Buttons disabled in config")
            return
        
        debounce_ms = buttons_config.get("debounce_ms", 50)
        long_press_ms = buttons_config.get("long_press_ms", 2000)
        pins_config = buttons_config.get("pins", {})
        
        for button_name, pin_name in pins_config.items():
            if pin_name not in self.hardware["pins"]:
                print(f"[INPUT] Pin {pin_name} not found in hardware config")
                continue
            
            pin_num = self.hardware["pins"][pin_name]
            
            button = Button(button_name, pin_num, pull_up=True)
            button.debounce_ms = debounce_ms
            button.long_press_ms = long_press_ms
            
            if button.initialize():
                self.buttons[button_name] = button
            else:
                print(f"[INPUT] Failed to initialize button {button_name}")
        
        if self.buttons:
            self.enabled = True
            print(f"[INPUT] {len(self.buttons)} buttons initialized")
        else:
            print("[INPUT] No buttons configured")
    
    def check_all(self):
        """Check all buttons and return list of events"""
        events = []
        current_time = utime.ticks_ms()
        
        # Rate limiting
        if utime.ticks_diff(current_time, self.last_check) < self.check_interval:
            return events
        
        if not self.enabled:
            return events
        
        for button in self.buttons.values():
            event = button.check()
            if event:
                events.append(event)
        
        self.last_check = current_time
        return events
    
    def register_callback(self, button_name, callback):
        """Register callback for button press"""
        if button_name in self.buttons:
            self.buttons[button_name].set_callback(callback)
            self.callbacks[f"{button_name}_press"] = callback
            print(f"[INPUT] Callback registered for {button_name}")
    
    def register_long_callback(self, button_name, callback):
        """Register callback for button long press"""
        if button_name in self.buttons:
            self.buttons[button_name].set_long_callback(callback)
            self.callbacks[f"{button_name}_long"] = callback
            print(f"[INPUT] Long callback registered for {button_name}")
    
    def get_button(self, name):
        """Get button by name"""
        return self.buttons.get(name)
    
    def get_all_status(self):
        """Get status of all buttons"""
        status = {}
        for name, button in self.buttons.items():
            status[name] = button.get_status()
        return status
    
    def simulate_press(self, button_name):
        """Simulate button press (for testing)"""
        if button_name in self.buttons:
            self.buttons[button_name].simulate_press()
    
    def simulate_long_press(self, button_name):
        """Simulate long button press (for testing)"""
        if button_name in self.buttons:
            self.buttons[button_name].simulate_long_press()
    
    def reset_all_press_counts(self):
        """Reset press counters for all buttons"""
        for button in self.buttons.values():
            button.reset_press_count()
    
    def is_enabled(self):
        """Check if input driver is enabled"""
        return self.enabled
    
    def get_button_count(self):
        """Get number of configured buttons"""
        return len(self.buttons)
    
    def is_healthy(self):
        """Check if input driver is healthy"""
        if not self.enabled:
            return True  # Disabled is OK
            
        # Check if at least one button is working
        working_buttons = sum(1 for b in self.buttons.values() 
                             if b.detected and b.error_count < 10)
        
        return working_buttons > 0
    
    def enable(self):
        """Enable input checking"""
        self.enabled = True
        print("[INPUT] Input driver enabled")
    
    def disable(self):
        """Disable input checking"""
        self.enabled = False
        print("[INPUT] Input driver disabled")
    
    def set_check_interval(self, interval_ms):
        """Set button check interval"""
        self.check_interval = max(10, interval_ms)  # Minimum 10ms
    
    def get_check_interval(self):
        """Get current check interval"""
        return self.check_interval