import re
from abc import ABC, abstractmethod
from typing import List

class EncryptedText(ABC):
    def __init__(self, text: str, owner_name: str, date: str):
        self.text = text
        self.owner_name = owner_name
        self.date = date
    
    @abstractmethod
    def encrypt(self) -> str:
        pass
    
    @abstractmethod
    def decrypt(self) -> str:
        pass
    
    @abstractmethod
    def print(self):
        pass
    
    def get_owner(self) -> str:
        return self.owner_name
    
    def get_date(self) -> str:
        return self.date
    
    def get_text_length(self) -> int:
        return len(self.text)
    
    def get_raw_text(self) -> str:
        return self.text

class SubstitutionCipher(EncryptedText):
    def __init__(self, text: str, owner_name: str, date: str, 
                 source_alphabet: str, target_alphabet: str):
        super().__init__(text, owner_name, date)
        self.source_alphabet = source_alphabet.lower()
        self.target_alphabet = target_alphabet.lower()
        self.encrypted_text = self.encrypt()
    
    def encrypt(self) -> str:
        result = []
        for char in self.text:
            if char.lower() in self.source_alphabet:
                pos = self.source_alphabet.index(char.lower())
                encrypted_char = self.target_alphabet[pos]
                if char.isupper():
                    encrypted_char = encrypted_char.upper()
                result.append(encrypted_char)
            else:
                result.append(char)
        return ''.join(result)
    
    def decrypt(self) -> str:
        result = []
        for char in self.encrypted_text:
            if char.lower() in self.target_alphabet:
                pos = self.target_alphabet.index(char.lower())
                decrypted_char = self.source_alphabet[pos]
                if char.isupper():
                    decrypted_char = decrypted_char.upper()
                result.append(decrypted_char)
            else:
                result.append(char)
        return ''.join(result)
    
    def print(self):
        decrypted = self.decrypt()
        print(f"SUBSTITUTION: owner='{self.owner_name}', date='{self.date}', "
              f"original='{self.text}', encrypted='{self.encrypted_text}', decrypted='{decrypted}'")

class ShiftCipher(EncryptedText):
    def __init__(self, text: str, owner_name: str, date: str, shift_value: int):
        super().__init__(text, owner_name, date)
        self.shift_value = shift_value
        self.encrypted_text = self.encrypt()
    
    def encrypt(self) -> str:
        result = []
        for char in self.text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                encrypted_char = chr((ord(char) - base + self.shift_value) % 26 + base)
                result.append(encrypted_char)
            else:
                result.append(char)
        return ''.join(result)
    
    def decrypt(self) -> str:
        result = []
        for char in self.encrypted_text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                decrypted_char = chr((ord(char) - base - self.shift_value) % 26 + base)
                result.append(decrypted_char)
            else:
                result.append(char)
        return ''.join(result)
    
    def print(self):
        decrypted = self.decrypt()
        print(f"SHIFT: owner='{self.owner_name}', date='{self.date}', shift={self.shift_value}, "
              f"original='{self.text}', encrypted='{self.encrypted_text}', decrypted='{decrypted}'")

class CommandProcessor:
    def __init__(self):
        self.texts: List[EncryptedText] = []
    
    def parse_quoted_string(self, text: str):
        match = re.match(r'^"([^"]*)"', text.strip())
        if match:
            return match.group(1), text[match.end():].strip()
        return None, text
    
    def process_command(self, line: str):
        line = line.strip()
        if not line:
            return
        
        parts = line.split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        
        if cmd == "ADD":
            self.process_add_command(rest)
        elif cmd == "REM":
            self.process_remove_command(rest)
        elif cmd == "PRINT":
            self.process_print_command()
        else:
            print(f"Unknown command: {cmd}")
    
    def process_add_command(self, command: str):
        parts = command.split(maxsplit=1)
        if not parts:
            print("Invalid ADD command")
            return
        
        cipher_type = parts[0]
        rest = parts[1] if len(parts) > 1 else ""
        
        if cipher_type == "SUBSTITUTION":
            self.add_substitution_cipher(rest)
        elif cipher_type == "SHIFT":
            self.add_shift_cipher(rest)
        else:
            print(f"Unknown cipher type: {cipher_type}")
    
    def add_substitution_cipher(self, command: str):
        text, rest = self.parse_quoted_string(command)
        if text is None:
            print("Invalid text format")
            return
        
        parts = rest.split()
        if len(parts) < 4:
            print("Invalid SUBSTITUTION command format")
            return
        
        owner = parts[0]
        date = parts[1]
        
        source_alpha, rest_after_source = self.parse_quoted_string(' '.join(parts[2:]))
        if source_alpha is None:
            print("Invalid source alphabet format")
            return

        target_alpha, _ = self.parse_quoted_string(rest_after_source)
        if target_alpha is None:
            print("Invalid target alphabet format")
            return
        
        cipher = SubstitutionCipher(text, owner, date, source_alpha, target_alpha)
        self.texts.append(cipher)
        print(f"Added SUBSTITUTION cipher for owner '{owner}'")
    
    def add_shift_cipher(self, command: str):
        text, rest = self.parse_quoted_string(command)
        if text is None:
            print("Invalid text format")
            return
        
        parts = rest.split()
        if len(parts) < 3:
            print("Invalid SHIFT command format")
            return
        
        owner = parts[0]
        date = parts[1]
        
        try:
            shift = int(parts[2])
        except ValueError:
            print("Invalid shift value")
            return
        
        cipher = ShiftCipher(text, owner, date, shift)
        self.texts.append(cipher)
        print(f"Added SHIFT cipher for owner '{owner}'")
    
    def process_remove_command(self, command: str):
        parts = command.split()
        if len(parts) < 3:
            print("Invalid REM command format")
            return
        
        field = parts[0]
        operator = parts[1]
        value_str = ' '.join(parts[2:])
        
        if value_str.startswith('"') and value_str.endswith('"'):
            value_str = value_str[1:-1]
        
        original_count = len(self.texts)
        
        if field == "owner" and operator == "==":
            self.texts = [t for t in self.texts if t.get_owner() != value_str]
        elif field == "owner" and operator == "!=":
            self.texts = [t for t in self.texts if t.get_owner() == value_str]
        elif field == "date" and operator == "==":
            self.texts = [t for t in self.texts if t.get_date() != value_str]
        elif field == "length" and operator == ">":
            try:
                value = int(value_str)
                self.texts = [t for t in self.texts if t.get_text_length() <= value]
            except ValueError:
                print("Invalid length value")
                return
        elif field == "length" and operator == "<":
            try:
                value = int(value_str)
                self.texts = [t for t in self.texts if t.get_text_length() >= value]
            except ValueError:
                print("Invalid length value")
                return
        else:
            print(f"Unknown REM condition: {field} {operator} {value_str}")
            return
        
        removed_count = original_count - len(self.texts)
        print(f"Removed {removed_count} items")
    
    def process_print_command(self):
        if not self.texts:
            print("No encrypted texts available")
            return
        
        print("\nENCRYPTED TEXTS")
        for i, text in enumerate(self.texts, 1):
            print(f"{i}. ", end="")
            text.print()
        print()
    
    def process_file(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        print(f"Processing line {line_num}: {line}")
                        self.process_command(line)
                        print()
        except FileNotFoundError:
            print(f"File '{filename}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")

def main():
    processor = CommandProcessor()
    processor.process_file("commands.txt")

if __name__ == "__main__":
    main()