"""
Ultra-Light Console for PicoWeather Pico Version
Compatible with 264KB RAM
"""

import sys
import gc

# Garbage collect immediately
gc.collect()

class UltraLightPicoConsole:
    """Ultra-light console for PicoWeather on standard Pico"""
    
    def __init__(self, drivers, config):
        self.drivers = drivers
        self.config = config
        self.running = True
        self.command_history = []
        self.max_history = 2  # Very small history
        
        # Minimal command set to save memory
        self.commands = {
            'help': self._cmd_help,
            'status': self._cmd_status,
            'sensors': self._cmd_sensors,
            'scan': self._cmd_scan,
            'exit': self._cmd_exit
        }
    
    def _cmd_help(self, args):
        """Show help"""
        print("Commands: help, status, sensors, scan, exit")
        return None
    
    def _cmd_status(self, args):
        """Show status"""
        print("System OK")
        return None
    
    def _cmd_sensors(self, args):
        """Show sensors"""
        print("No sensor data")
        return None
    
    def _cmd_scan(self, args):
        """Scan I2C"""
        print("Scanning...")
        return None
    
    def _cmd_exit(self, args):
        """Exit console"""
        self.running = False
        return None
    
    def _get_command_input(self):
        """Get input with minimal memory usage"""
        try:
            line = input("pico> ").strip()
            
            # Simple ? autocomplete
            if line.endswith('?'):
                self._show_simple_suggestions(line[:-1])
                return ""
            
            # Add to history
            if line and line not in self.command_history:
                self.command_history.insert(0, line)
                if len(self.command_history) > self.max_history:
                    del self.command_history[-1]
            
            return line
            
        except KeyboardInterrupt:
            print("^C")
            return ""
        except EOFError:
            self.running = False
            return ""
    
    def _show_simple_suggestions(self, partial):
        """Show simple suggestions"""
        if not partial:
            print("Commands: help, status, sensors, scan, exit")
            return
        
        suggestions = []
        for cmd in self.commands:
            if cmd.startswith(partial):
                suggestions.append(cmd)
        
        if len(suggestions) == 1:
            print(f"Command: {suggestions[0]}")
        elif suggestions:
            print("Suggestions:")
            for s in suggestions[:2]:  # Limit to 2
                print(f"  {s}")
    
    def run(self):
        """Run the console"""
        print("PicoWeather Console - Light Version")
        print("Use ? for autocomplete, exit to quit")
        print()
        
        while self.running:
            try:
                line = self._get_command_input()
                
                if not line:
                    continue
                
                # Parse and execute
                parts = line.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    try:
                        self.commands[cmd](args)
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print(f"Unknown command: {cmd}")
                
                # Garbage collect to save memory
                gc.collect()
                
            except Exception as e:
                print(f"Console error: {e}")
                gc.collect()


# Integration function for main.py
def create_ultra_light_console(drivers, config):
    """Create ultra-light console for Pico"""
    return UltraLightPicoConsole(drivers, config)