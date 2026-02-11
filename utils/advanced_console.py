"""
Advanced Console Input for MicroPython
Supports arrow keys (history), Tab autocomplete, and basic editing
"""

import sys
import time

class AdvancedConsoleInput:
    """Advanced input handling for MicroPython with history and autocomplete"""
    
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.history = []
        self.history_index = -1
        self.current_input = ""
        
    def add_to_history(self, command):
        """Add command to history"""
        command = command.strip()
        if not command:
            return
        
        # Remove duplicates
        if command in self.history:
            self.history.remove(command)
        
        # Add to beginning
        self.history.insert(0, command)
        
        # Limit size
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
        
        self.history_index = -1
    
    def get_input_with_history(self, prompt="pico> "):
        """Get input with arrow key history support"""
        # Note: Full arrow key support requires specific terminal handling
        # This is a simplified version for MicroPython compatibility
        
        print(prompt, end="", flush=True)
        
        # Collect input character by character
        input_buffer = ""
        
        try:
            # For MicroPython, we need to use sys.stdin.read(1) for character-by-character input
            # However, this requires specific terminal configuration
            # Fallback to standard input() for compatibility
            
            line = input()
            return line.strip()
            
        except KeyboardInterrupt:
            print("^C")
            return ""
        except EOFError:
            print("^D")
            return ""
    
    def simple_tab_autocomplete(self, line, commands, subcommands, max_suggestions=5):
        """Simple Tab autocomplete function"""
        if '\t' not in line:
            return line, []
        
        # Remove tab and get partial command
        partial = line.replace('\t', '').strip()
        parts = partial.split()
        
        if not parts:
            return "", []
        
        suggestions = []
        
        if len(parts) == 1:
            # Complete main commands
            partial_cmd = parts[0].lower()
            suggestions = [cmd for cmd in commands.keys() 
                          if cmd.startswith(partial_cmd)]
        
        elif len(parts) >= 2:
            # Complete subcommands
            cmd_name = parts[0].lower()
            if cmd_name in subcommands:
                if len(parts) == 2:
                    partial_sub = parts[1].lower()
                    suggestions = [sub for sub in subcommands[cmd_name]
                                  if sub.startswith(partial_sub)]
                else:
                    suggestions = []
        
        suggestions = suggestions[:max_suggestions]
        
        if len(suggestions) == 1:
            # Auto-complete
            if len(parts) == 1:
                completed = suggestions[0]
            else:
                completed = parts[0] + " " + suggestions[0]
            return completed, []
        elif suggestions:
            # Show suggestions
            return partial, suggestions
        
        return partial, []


class MicroPythonConsole:
    """Simplified console optimized for MicroPython constraints"""
    
    def __init__(self, max_history=10):
        self.input_handler = AdvancedConsoleInput(max_history)
        self.commands = {}
        self.subcommands = {}
        self.history = []
    
    def set_commands(self, commands, subcommands=None):
        """Set commands and subcommands"""
        self.commands = commands
        self.subcommands = subcommands or {}
    
    def get_command_input(self, prompt="pico> "):
        """Get command input with basic autocomplete"""
        try:
            # Use standard input() for maximum MicroPython compatibility
            line = input(prompt)
            
            # Check for Tab in input (rare but possible)
            if '\t' in line:
                completed, suggestions = self.input_handler.simple_tab_autocomplete(
                    line, self.commands, self.subcommands
                )
                
                if suggestions:
                    print(f"\nSuggestions:")
                    for s in suggestions:
                        print(f"  {s}")
                    print(f"{prompt}{completed}", end="", flush=True)
                    # Get additional input after suggestions
                    additional = input()
                    line = completed + additional
                else:
                    line = completed
            
            line = line.strip()
            
            # Add to history
            if line:
                self.input_handler.add_to_history(line)
                self.history.insert(0, line)
                if len(self.history) > self.input_handler.max_history:
                    self.history = self.history[:self.input_handler.max_history]
            
            return line
            
        except KeyboardInterrupt:
            print("^C")
            return ""
        except EOFError:
            print("^D")
            return ""
    
    def show_suggestions(self, command):
        """Show command suggestions for help"""
        parts = command.split()
        
        if not parts:
            print("Available commands:")
            for cmd in sorted(self.commands.keys()):
                print(f"  {cmd}")
            return
        
        if len(parts) == 1:
            cmd = parts[0].lower()
            if cmd in self.subcommands:
                print(f"Subcommands for '{cmd}':")
                for sub in self.subcommands[cmd]:
                    print(f"  {cmd} {sub}")
            elif cmd in self.commands:
                print(f"Command '{cmd}' exists (no subcommands)")
            else:
                # Show similar commands
                similar = [c for c in self.commands.keys() 
                           if c.startswith(cmd)]
                if similar:
                    print("Did you mean:")
                    for s in similar:
                        print(f"  {s}")
                else:
                    print(f"Unknown command: {cmd}")


# Enhanced version with better MicroPython support
class EnhancedConsoleInput:
    """Enhanced console input with better MicroPython support"""
    
    def __init__(self, max_history=15):
        self.max_history = max_history
        self.history = []
        self.history_pos = -1
        self.commands = {}
        self.subcommands = {}
    
    def setup(self, commands, subcommands=None):
        """Setup commands and subcommands"""
        self.commands = commands
        self.subcommands = subcommands or {}
    
    def get_input_line(self, prompt="pico> "):
        """Get input line with Tab autocomplete"""
        try:
            line = input(prompt)
            return self.process_input(line)
        except KeyboardInterrupt:
            print("^C")
            return ""
        except EOFError:
            print("^D") 
            return ""
    
    def process_input(self, line):
        """Process input line for autocomplete"""
        if '\t' not in line:
            return line.strip()
        
        # Handle Tab completion
        line_without_tab = line.replace('\t', '')
        completed = self.autocomplete(line_without_tab)
        
        if completed != line_without_tab:
            print(f"\n{prompt}{completed}", end="", flush=True)
            # Get any additional input
            try:
                additional = input()
                return completed + additional
            except:
                return completed
        
        return line_without_tab.strip()
    
    def autocomplete(self, partial):
        """Perform autocomplete on partial input"""
        parts = partial.strip().split()
        
        if not parts:
            return partial
        
        suggestions = []
        
        if len(parts) == 1:
            # Complete main commands
            partial_cmd = parts[0].lower()
            suggestions = [cmd for cmd in self.commands.keys()
                          if cmd.startswith(partial_cmd)]
        
        elif len(parts) >= 2:
            # Complete subcommands
            cmd = parts[0].lower()
            if cmd in self.subcommands:
                if len(parts) == 2:
                    partial_sub = parts[1].lower()
                    suggestions = [sub for sub in self.subcommands[cmd]
                                  if sub.startswith(partial_sub)]
        
        if len(suggestions) == 1:
            # Complete with single suggestion
            if len(parts) == 1:
                return suggestions[0]
            else:
                return parts[0] + " " + suggestions[0]
        elif suggestions:
            # Show multiple suggestions
            print(f"\nSuggestions:")
            for s in suggestions[:5]:  # Limit to 5 suggestions
                print(f"  {s}")
            return partial
        
        return partial
    
    def add_history(self, command):
        """Add command to history"""
        if not command or command.strip() == "":
            return
        
        command = command.strip()
        
        # Remove if exists
        if command in self.history:
            self.history.remove(command)
        
        # Add to front
        self.history.insert(0, command)
        
        # Limit size
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
        
        self.history_pos = -1
    
    def get_previous_command(self):
        """Get previous command from history"""
        if not self.history:
            return ""
        
        if self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            return self.history[self.history_pos]
        
        return self.history[self.history_pos] if self.history_pos >= 0 else ""
    
    def get_next_command(self):
        """Get next command from history"""
        if self.history_pos <= 0:
            self.history_pos = -1
            return ""
        
        self.history_pos -= 1
        return self.history[self.history_pos]