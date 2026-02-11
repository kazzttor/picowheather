"""
Simple Console with Tab Autocomplete for PicoWeather
Optimized for MicroPython console environment
"""

class SimpleTabConsole:
    """Simplified console with Tab autocomplete for MicroPython"""
    
    def __init__(self, max_history=10):
        self.max_history = max_history
        self.history = []
        self.commands = {}
        self.subcommands = {}
    
    def setup_commands(self, commands, subcommands):
        """Setup commands and subcommands"""
        self.commands = commands
        self.subcommands = subcommands
    
    def get_input_with_tab(self, prompt="pico> "):
        """Get input with Tab autocomplete - simplified for MicroPython"""
        try:
            # Try to read input normally first
            line = input(prompt)
            
            # Process for Tab character
            if '\t' in line:
                return self._process_tab_input(line, prompt)
            else:
                return self._add_to_history(line.strip())
                
        except KeyboardInterrupt:
            print("^C")
            return ""
        except EOFError:
            print("^D")
            return ""
    
    def _process_tab_input(self, line_with_tab, prompt):
        """Process input containing Tab character"""
        # Remove Tab and get partial command
        partial = line_with_tab.replace('\t', '').strip()
        
        if not partial:
            return self._add_to_history("")
        
        # Get suggestions
        suggestions = self._get_suggestions(partial)
        
        if len(suggestions) == 1:
            # Auto-complete with single suggestion
            completed = self._complete_partial(partial, suggestions[0])
            print(f"\n{prompt}{completed}")
            return self._add_to_history(completed)
        elif suggestions:
            # Show multiple suggestions
            print(f"\n{self.t('messages.autocomplete_suggestions')}:")
            for s in suggestions:
                print(f"  {s}")
            print(f"{prompt}{partial}", end="", flush=True)
            try:
                additional = input()
                final_line = partial + " " + additional.strip()
                return self._add_to_history(final_line)
            except:
                return self._add_to_history(partial)
        else:
            # No suggestions
            return self._add_to_history(partial)
    
    def _get_suggestions(self, partial):
        """Get suggestions for partial input"""
        parts = partial.strip().split()
        
        if not parts:
            return []
        
        suggestions = []
        
        if len(parts) == 1:
            # Complete main commands
            partial_cmd = parts[0].lower()
            suggestions = [cmd for cmd in self.commands.keys()
                          if cmd.startswith(partial_cmd)]
        
        elif len(parts) >= 2:
            # Complete subcommands
            cmd_name = parts[0].lower()
            if cmd_name in self.subcommands:
                if len(parts) == 2:
                    partial_sub = parts[1].lower()
                    suggestions = [sub for sub in self.subcommands[cmd_name]
                                  if sub.startswith(partial_sub)]
        
        return suggestions[:5]
    
    def _complete_partial(self, partial, suggestion):
        """Complete partial input with suggestion"""
        parts = partial.strip().split()
        
        if len(parts) == 1:
            return suggestion
        elif len(parts) == 2:
            return parts[0] + " " + suggestion
        else:
            return partial
    
    def _add_to_history(self, command):
        """Add command to history"""
        if not command or command.strip() == "":
            return command
        
        command = command.strip()
        
        # Remove if exists
        if command in self.history:
            self.history.remove(command)
        
        # Add to front
        self.history.insert(0, command)
        
        # Limit size
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
        
        return command
    
    def t(self, key, **kwargs):
        """Translation function - will be overridden"""
        return key


def test_tab_autocomplete():
    """Test function for Tab autocomplete"""
    # Test data
    commands = {
        'help': lambda: None,
        'fm': lambda: None,
        'wifi': lambda: None,
        'exit': lambda: None
    }
    
    subcommands = {
        'fm': ['status', 'frequency', 'volume', 'mute'],
        'wifi': ['status', 'scan', 'connect']
    }
    
    console = SimpleTabConsole()
    console.setup_commands(commands, subcommands)
    console.t = lambda key, **kwargs: key
    
    # Test cases
    test_cases = [
        "hel\t",      # Should complete to 'help'
        "fm s\t",     # Should show ['status', 'scan'] for 'fm s'
        "xyz\t",      # Should show no suggestions
        "wifi\t",     # Should show ['status', 'scan', 'connect']
    ]
    
    for test in test_cases:
        print(f"Testing: {repr(test)}")
        result = console._process_tab_input(test, "test> ")
        print(f"Result: {result}")
        print("-" * 40)


if __name__ == "__main__":
    test_tab_autocomplete()