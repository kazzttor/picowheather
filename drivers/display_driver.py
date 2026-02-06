"""
Display Driver - Hardware abstraction for framebuffer rendering
Receives complete framebuffer from DisplayManager and sends to hardware
"""

import time
import json
import sys

# Try to import MicroPython modules, fallback gracefully
try:
    import machine
    from machine import SPI, I2C, Pin
except ImportError:
    machine = None
    SPI = None
    I2C = None
    Pin = None

try:
    from framebuf import FrameBuffer, MONO_VLSB
except ImportError:
    FrameBuffer = None
    MONO_VLSB = None

try:
    import utime
except ImportError:
    utime = None

# Import display libraries
SSD1306_AVAILABLE = False
SSD1306_I2C = None
try:
    from ssd1306 import SSD1306_I2C
    SSD1306_AVAILABLE = True
except ImportError:
    try:
        from lib.ssd1306 import SSD1306_I2C
        SSD1306_AVAILABLE = True
    except ImportError:
        pass

ST7567_AVAILABLE = False
ST7567 = None
try:
    from st7567 import ST7567
    ST7567_AVAILABLE = True
except ImportError:
    try:
        from lib.st7567 import ST7567
        ST7567_AVAILABLE = True
    except ImportError:
        pass


def print_exception(e):
    """Print exception with MicroPython compatibility"""
    try:
        sys.print_exception(e)
    except AttributeError:
        print(f"[EXCEPTION] {e}")


class DisplayDriver:
    """Hardware display driver - receives framebuffer and sends to hardware"""
    
    def __init__(self, config, hardware):
        self.config = config
        self.hardware = hardware
        self.display = None
        self.display_type = None
        self.detected = False
        self.initialized = False
        
        self._initialize_display()
        print(f"[DISPLAY] Display driver initialized for {self.display_type}")
    
    def _initialize_display(self):
        """Initialize display hardware"""
        display_config = self.config.get("display", {})
        self.display_type = display_config.get("type", "st7567_spi")
        
        print(f"[DISPLAY] Initializing {self.display_type}")
        
        try:
            if self.display_type == "ssd1306_i2c":
                if not SSD1306_AVAILABLE:
                    print("[DISPLAY] Error: SSD1306 library not available")
                    return
                self._init_ssd1306(display_config)
            elif self.display_type == "st7567_spi":
                if not ST7567_AVAILABLE:
                    print("[DISPLAY] Error: ST7567 library not available")
                    return
                self._init_st7567(display_config)
            else:
                print(f"[DISPLAY] Unsupported: {self.display_type}")
                return
            
            self.detected = True
            self.initialized = True
            print(f"[DISPLAY] {self.display_type} ready")
                
        except Exception as e:
            print(f"[DISPLAY] Initialization error: {e}")
            print_exception(e)
    
    def show_framebuffer(self, framebuffer):
        """
        Main interface: receive complete framebuffer and send to hardware
        """
        if not self.is_healthy():
            return False
        
        try:
            if self.display_type == "ssd1306_i2c":
                # SSD1306 uses display.fill() and display.show() directly
                if isinstance(framebuffer, (bytes, bytearray)):
                    # Raw buffer received - copy to SSD1306
                    if hasattr(self.display, 'buffer'):
                        for i in range(min(len(framebuffer), len(self.display.buffer))):
                            self.display.buffer[i] = framebuffer[i]
                    self.display.show()
                else:
                    # FrameBuffer object received
                    self.display.fill(0)
                    if hasattr(self.display, 'blit'):
                        self.display.blit(framebuffer, 0, 0)
                    else:
                        # Fallback: assume it has internal buffer
                        if hasattr(framebuffer, 'buffer'):
                            for i in range(len(framebuffer.buffer)):
                                self.display.buffer[i] = framebuffer.buffer[i]
                    self.display.show()
                    
            elif self.display_type == "st7567_spi":
                # ST7567 receives raw framebuffer buffer (bytes/bytearray)
                if not isinstance(framebuffer, (bytes, bytearray)):
                    print(f"[DISPLAY] ST7567: Invalid buffer type: {type(framebuffer)}, expected bytes/bytearray")
                    return False
                
                # Framebuffer sent to hardware
                # Send to ST7567 hardware
                self.display.show(framebuffer)
            
            return True
            
        except Exception as e:
            print(f"[DISPLAY] Show framebuffer error: {e}")
            return False
    
    def clear_display(self):
        """Clear the display"""
        if not self.is_healthy():
            return False
        
        try:
            if self.display_type == "ssd1306_i2c":
                self.display.fill(0)
                self.display.show()
            elif self.display_type == "st7567_spi":
                empty_buffer = bytearray(self.config.get("display", {}).get("width", 128) * 
                                      self.config.get("display", {}).get("height", 64) // 8)
                self.display.show(empty_buffer)
            return True
        except Exception as e:
            print(f"[DISPLAY] Clear error: {e}")
            return False
    
    def _init_ssd1306(self, config):
        """Initialize SSD1306 using existing library"""
        if not I2C:
            print("[DISPLAY] I2C not available")
            return
            
        i2c_bus_config = config.get("i2c_bus", 0)
        i2c_config = self.config.get("i2c_buses", {}).get(f"i2c{i2c_bus_config}", {})
        
        if not i2c_config.get("enabled", False):
            print(f"[DISPLAY] I2C bus {i2c_bus_config} not enabled")
            return
        
        pins_config = i2c_config.get("pins", {})
        sda_pin_name = pins_config.get("sda", "i2c0_sda")
        scl_pin_name = pins_config.get("scl", "i2c0_scl")
        
        if sda_pin_name not in self.hardware["pins"]:
            print(f"[DISPLAY] Pin {sda_pin_name} not found in hardware config")
            return
        if scl_pin_name not in self.hardware["pins"]:
            print(f"[DISPLAY] Pin {scl_pin_name} not found in hardware config")
            return
            
        sda_pin = self.hardware["pins"][sda_pin_name]
        scl_pin = self.hardware["pins"][scl_pin_name]
        freq = i2c_config.get("frequency", 400000)
        
        print(f"[DISPLAY] Initializing I2C on bus {i2c_bus_config}, SDA={sda_pin}, SCL={scl_pin}")
        
        i2c_bus = I2C(i2c_bus_config, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        
        # Try to detect device
        devices = i2c_bus.scan()
        if not devices:
            print("[DISPLAY] No I2C devices found")
            return
        
        print(f"[DISPLAY] Found I2C devices: {[hex(addr) for addr in devices]}")
        
        # Use address from config or default
        i2c_address = config.get("i2c_address", 0x3C)
        if i2c_address not in devices:
            print(f"[DISPLAY] Device at 0x{i2c_address:02X} not found, trying alternative 0x3D")
            i2c_address = 0x3D
            if i2c_address not in devices:
                print(f"[DISPLAY] Device at 0x{i2c_address:02X} also not found")
                return
        
        self.display = SSD1306_I2C(128, 64, i2c_bus, addr=i2c_address)
        
        # Test
        self.display.fill(0)
        self.display.text("SSD1306 OK", 0, 0)
        self.display.text(f"Addr: 0x{i2c_address:02X}", 0, 10)
        self.display.show()
        time.sleep(0.5)
    
    def _init_st7567(self, config):
        """Initialize ST7567 using existing library"""
        if not SPI or not Pin:
            print("[DISPLAY] SPI or Pin not available")
            return
            
        spi_bus_config = config.get("spi_bus", 1)
        pins_config = config.get("pins", {})
        
        # Get pin names from config
        sck_pin_name = pins_config.get("sck", "spi1_sck")
        mosi_pin_name = pins_config.get("mosi", "spi1_mosi")
        dc_pin_name = pins_config.get("dc", "spi1_dc")
        cs_pin_name = pins_config.get("cs", "spi1_cs")
        rst_pin_name = pins_config.get("rst", "spi1_rst")
        
        # Get actual pin numbers
        sck_pin = self.hardware["pins"].get(sck_pin_name, 14)
        mosi_pin = self.hardware["pins"].get(mosi_pin_name, 15)
        dc_pin = self.hardware["pins"].get(dc_pin_name, 12)
        cs_pin = self.hardware["pins"].get(cs_pin_name, 13)
        rst_pin = self.hardware["pins"].get(rst_pin_name, 11)
        
        print(f"[DISPLAY] Initializing ST7567 on SPI bus {spi_bus_config}")
        print(f"[DISPLAY] Pins: SCK={sck_pin}, MOSI={mosi_pin}, DC={dc_pin}, CS={cs_pin}, RST={rst_pin}")
        
        spi_bus = SPI(
            spi_bus_config,
            baudrate=config.get("spi_settings", {}).get("baudrate", 200000),
            polarity=config.get("spi_settings", {}).get("polarity", 1),
            phase=config.get("spi_settings", {}).get("phase", 1),
            sck=Pin(sck_pin),
            mosi=Pin(mosi_pin)
        )
        
        # Create pin objects for optional pins
        dc_pin_obj = Pin(dc_pin, Pin.OUT)
        cs_pin_obj = Pin(cs_pin, Pin.OUT) if cs_pin else None
        rst_pin_obj = Pin(rst_pin, Pin.OUT) if rst_pin else None
        
        self.display = ST7567(
            spi_bus,
            dc=dc_pin_obj,
            cs=cs_pin_obj,
            rst=rst_pin_obj,
            contrast=config.get("contrast", 31),
            flipX=config.get("flip_x", False),
            flipY=config.get("flip_y", True)
        )
        
        # Test using frame buffer
        if FrameBuffer:
            buffer = bytearray(128 * 64 // 8)
            fb = FrameBuffer(buffer, 128, 64, MONO_VLSB)
            fb.fill(0)
            fb.text("ST7567 OK", 0, 0)
            fb.text("128x64 LCD", 0, 10)
            self.display.show(buffer)
            time.sleep(0.5)
    
    
    
    
    
    def is_healthy(self):
        """Check if display is working"""
        return self.detected and self.initialized and self.display is not None
    
    def get_status(self):
        """Get display status for console and diagnostics"""
        status = {
            'detected': self.detected,
            'initialized': self.initialized,
            'type': self.display_type,
            'healthy': self.is_healthy(),
            'display_available': self.display is not None,
        }
        
        if self.is_healthy():
            if self.display_type == "st7567_spi":
                status.update({
                    'resolution': '128x64',
                    'library': 'ST7567',
                    'width': 128,
                    'height': 64,
                })
            elif self.display_type == "ssd1306_i2c":
                status.update({
                    'resolution': '128x64', 
                    'library': 'SSD1306',
                    'width': 128,
                    'height': 64,
                })
        
        return status
    
    def clear(self):
        """Clear the display"""
        if self.is_healthy():
            try:
                if self.display_type == "ssd1306_i2c":
                    self.display.fill(0)
                    self.display.show()
                elif self.display_type == "st7567_spi":
                    if FrameBuffer:
                        buffer = bytearray(128 * 64 // 8)
                        fb = FrameBuffer(buffer, 128, 64, MONO_VLSB)
                        fb.fill(0)
                        self.display.show(buffer)
            except Exception as e:
                print(f"[DISPLAY] Clear error: {e}")
                print_exception(e)
    
    def test_display(self):
        """Simple test"""
        if not self.is_healthy():
            print("[DISPLAY] Display not healthy")
            return False
        
        try:
            if self.display_type == "ssd1306_i2c":
                self.display.fill(0)
                self.display.text("TEST OK", 30, 25)
                self.display.text(self.display_type, 20, 35)
                self.display.show()
                time.sleep(2)
                self.display.fill(0)
                self.display.show()
            elif self.display_type == "st7567_spi":
                if FrameBuffer:
                    buffer = bytearray(128 * 64 // 8)
                    fb = FrameBuffer(buffer, 128, 64, MONO_VLSB)
                    fb.fill(0)
                    fb.text("TEST OK", 30, 25)
                    fb.text(self.display_type, 20, 35)
                    self.display.show(buffer)
                    time.sleep(2)
                    fb.fill(0)
                    self.display.show(buffer)
            
            return True
        except Exception as e:
            print(f"[DISPLAY] Test error: {e}")
            print_exception(e)
            return False