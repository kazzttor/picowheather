"""
Ultra-Light Console for PicoWeather
Minimal memory usage for Pico with 264KB RAM
"""

class UltraLightConsole:
    """Ultra-light console with minimal memory footprint"""
    
    def __init__(self):
        # Use built-in types only, no complex structures
        self.history = []  # Simple list, no objects
        self.max_history = 5  # Reduced from 15 to save memory
        
    def get_input(self, prompt="pico> "):
        """Get input with minimal memory usage"""
        try:
            line = input(prompt)
            return line.strip()
        except:
            return ""
    
    def add_to_history(self, cmd):
        """Add to history with minimal overhead"""
        if not cmd:
            return
        
        cmd = cmd.strip()
        if not cmd:
            return
        
        # Simple history management
        if cmd in self.history:
            self.history.remove(cmd)
        
        self.history.insert(0, cmd)
        
        # Keep only last few commands
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
    
    def get_suggestions(self, partial, commands, subcommands):
        """Get suggestions with minimal memory usage"""
        parts = partial.split()
        if not parts:
            return []
        
        suggestions = []
        
        if len(parts) == 1:
            # Complete main commands
            p = parts[0].lower()
            for cmd in commands:
                if cmd.startswith(p):
                    suggestions.append(cmd)
        
        elif len(parts) == 2:
            # Complete subcommands
            cmd = parts[0].lower()
            if cmd in subcommands:
                p = parts[1].lower()
                for sub in subcommands[cmd]:
                    if sub.startswith(p):
                        suggestions.append(sub)
        
        # Return only first 3 to save memory
        return suggestions[:3]


def setup_ultra_light_console():
    """Setup ultra-light console for PicoWeather"""
    return UltraLightConsole()


def test_memory_usage():
    """Test memory usage of ultra-light console"""
    import gc
    
    print("Testing memory usage...")
    gc.collect()
    mem_before = gc.mem_free()
    
    console = UltraLightConsole()
    gc.collect()
    mem_after = gc.mem_free()
    
    print(f"Memory used by console: {mem_before - mem_after} bytes")
    print(f"Free memory: {mem_after} bytes")
    
    # Test basic functionality
    suggestions = console.get_suggestions("fm s", 
                                       {"fm": None, "wifi": None},
                                       {"fm": ["status", "scan"]})
    print(f"Suggestions: {suggestions}")


if __name__ == "__main__":
    test_memory_usage()