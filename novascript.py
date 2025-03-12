import sys
import os
import threading
import asyncio
import gc
import psutil
import llvmlite.binding as llvm
import time
import re
import struct

# ✅ Initialize LLVM
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

# ✅ NovaScript Interpreter with Async Execution & System Optimization

# NovaScript command mappings
nova_commands = {
    "print": lambda args: print(" ".join(args)),
    "applyTerminalTheme": lambda args: print(f"Applied terminal theme: {args[0]}"),
    "enableAISuggestions": lambda args: print("AI-Assisted Terminal Suggestions Enabled."),
    # Add more command mappings as needed
}

# Token patterns
TOKEN_PATTERNS = [
    (r'let', 'LET'),
    (r'function', 'FUNCTION'),
    (r'if', 'IF'),
    (r'else', 'ELSE'),
    (r'while', 'WHILE'),
    (r'print', 'PRINT'),
    (r'input', 'INPUT'),
    (r'open|read|close', 'FILE_OP'),
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
    (r'[-+*/=^><|!&]', 'OPERATOR'),  # Add caret (^) for power operation, > for comparison, | for bitwise OR, ! for negation, and & for bitwise AND
    (r'\d+', 'NUMBER'),
    (r'".*?"', 'STRING'),
    (r'[(){},;\[\]:]', 'SYMBOL'),  # Add patterns for [ and ] and :
    (r'\.', 'DOT'),  # Add this line to handle the '.' character
]

def tokenize(code):
    tokens = []
    for line in code.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue  # Skip lines that are comments
        while line:
            match = None
            for pattern, token_type in TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(line)
                if match:
                    tokens.append((token_type, match.group(0)))
                    line = line[match.end():].strip()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character: {line[0]}")
    return tokens

def parse_and_execute(tokens):
    variables = {}

    i = 0
    while i < len(tokens):
        token_type, token_value = tokens[i]

        if token_type == 'LET':  # Variable declaration
            var_name = tokens[i+1][1]
            value = tokens[i+3][1]  # Assume simple `let x = 10;`
            variables[var_name] = int(value) if value.isdigit() else value
            i += 4  # Skip processed tokens

        elif token_type == 'PRINT':  # Print statement
            to_print = tokens[i+1][1]
            if to_print in variables:
                print(variables[to_print])
            else:
                print(to_print.strip('"'))  # Remove quotes
            i += 2

        else:
            i += 1  # Skip unknown tokens

def compile_novascript(tokens):
    bytecode = []
    i = 0

    while i < len(tokens):
        token_type, token_value = tokens[i]
        if token_type == "LET":
            bytecode.append(0x01)  # Example opcode for variable declaration
            i += 4  # Skip processed tokens
        elif token_type == "PRINT":
            bytecode.append(0x02)  # Example opcode for print
            i += 2
        elif token_type == "NUMBER":
            number = int(token_value)
            if 0 <= number <= 255:
                bytecode.append(0x03)  # Example opcode for number
                bytecode.append(number)
            else:
                bytecode.append(0x03)  # Example opcode for number
                bytecode.extend(struct.pack(">I", number))  # Pack as 4-byte integer
            i += 1
        elif token_type == "STRING":
            bytecode.append(0x04)  # Example opcode for string
            encoded_string = token_value.encode()
            length = len(encoded_string)
            if length <= 255:
                bytecode.append(length)
                bytecode.extend(encoded_string)
            else:
                raise ValueError(f"String length out of range: {length}")
            i += 1
        elif token_type == "IF":
            bytecode.append(0x05)  # Example opcode for if
            i += 1
        elif token_type == "ELSE":
            bytecode.append(0x06)  # Example opcode for else
            i += 1
        elif token_type == "WHILE":
            bytecode.append(0x07)  # Example opcode for while
            i += 1
        elif token_type == "FUNCTION":
            bytecode.append(0x08)  # Example opcode for function
            i += 1
        else:
            i += 1  # Skip unknown tokens

    return struct.pack("B" * len(bytecode), *bytecode)  # Convert to binary

def run_nova_bytecode(bytecode):
    i = 0
    while i < len(bytecode):
        opcode = bytecode[i]

        if opcode == 0x01:  # Variable declaration
            print("💾 Declaring Variable...")
        elif opcode == 0x02:  # Print
            print("📢 Printing...")
        elif opcode == 0x03:  # Number
            number = struct.unpack(">I", bytecode[i+1:i+5])[0]
            print(f"🔢 Number: {number}")
            i += 4
        elif opcode == 0x04:  # String
            length = bytecode[i+1]
            print(f"📝 String: {bytecode[i+2:i+2+length].decode()}")
            i += length + 1
        elif opcode == 0x05:  # If
            print("🔍 If condition...")
        elif opcode == 0x06:  # Else
            print("🔍 Else condition...")
        elif opcode == 0x07:  # While
            print("🔄 While loop...")
        elif opcode == 0x08:  # Function
            print("🔧 Function definition...")
        i += 1

# ✅ Function to Run a NovaScript File
async def run_novascript(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as script:
            code = script.read()

            # ✅ Syntax Check
            if not is_valid_novascript(code):
                print(f"❌ Syntax Error in {file_path}. Execution aborted.")
                return

            print(f"\n🚀 Running NovaScript file: {file_path}\n")
            await execute_script(code)
    else:
        print(f"❌ Error: File '{file_path}' not found.")

# ✅ Multi-Threaded Execution
def run_in_thread(file_path):
    thread = threading.Thread(target=asyncio.run, args=(run_novascript(file_path),))
    thread.start()

# ✅ Function to Validate NovaScript Syntax
def is_valid_novascript(code):
    if "function" not in code and "print" not in code:
        return False  # Basic validation: Must contain a function or print statement
    return True

# ✅ Execute NovaScript Code (With LLVM & Async)
async def execute_script(code):
    try:
        # Convert lines starting with '//' to Python comments
        code = '\n'.join(line.replace('//', '#', 1) if line.strip().startswith('//') else line for line in code.split('\n'))
        
        # Tokenize the NovaScript code
        tokens = tokenize(code)
        
        # Compile the tokens into bytecode
        bytecode = compile_novascript(tokens)
        print(f"Compiled Bytecode: {bytecode}")
        
        # Run the compiled bytecode
        run_nova_bytecode(bytecode)
        
        await asyncio.sleep(0)  # Ensures async compatibility
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
    except Exception as e:
        print(f"❌ Runtime Error: {e}")

# ✅ Recursively find all .ns scripts in subdirectories
def list_novascript_files():
    print("\n📂 Available NovaScript Files:")
    
    script_files = []

    # Debugging: print what directories are being scanned
    current_dir = os.getcwd()
    print(f"\n Current Directory: {current_dir}")
    
    for root, _, files in os.walk(current_dir):  # Use absolute path instead of "."
        print(f"  Scanning: {root}")  # Show each directory scanned

        for file in files:
            if file.endswith(".ns"):
                full_path = os.path.join(root, file)
                print(f"  Found: {full_path}")  # Debugging: Show each directory checked
                script_files.append(full_path)
    
    if script_files:
        for i, file in enumerate(script_files, 1):
            print(f"  {i}. {file}")
    else:
        print("  ⚠️ No NovaScript files found.")
    
    return script_files  # Return list of all found .ns files

# ✅ Interactive Mode for NovaScript
def interactive_mode():
    print("\n🔹 Entering NovaScript Interactive Mode (Type 'exit' to quit)")
    while True:
        try:
            user_input = input("NovaScript > ").strip()
            if user_input.lower() == "exit":
                print("👋 Exiting Interactive Mode.")
                break
            elif user_input:
                asyncio.run(execute_script(user_input))
        except Exception as e:
            print(f"❌ Error: {e}")

# ✅ Nova System Optimizer (Monitors Nova OS Performance)
async def nova_system_optimizer():
    counter = 0
    while counter < 5:
        await asyncio.sleep(10)  # Runs every 10 seconds
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory()

        print("\n📊 System Optimization Report")
        print(f"🔹 CPU Usage: {cpu_usage}%")
        print(f"🔹 Memory Usage: {memory_usage.percent}% (Available: {memory_usage.available // (1024 * 1024)} MB)")

        # ✅ Optimize Garbage Collection
        gc.collect()

# ✅ Start System Optimizer in Background
optimizer_thread = threading.Thread(target=asyncio.run, args=(nova_system_optimizer(),), daemon=True)
optimizer_thread.start()

# ✅ Main Execution Logic
if __name__ == "__main__":
    if len(sys.argv) > 1:
        script_file = sys.argv[1]
        run_in_thread(script_file)
    else:
        print("\n⚠️ No script file provided. Please enter the path to a NovaScript file.")

        # ✅ List and retrieve available `.ns` files from all directories
        script_files = list_novascript_files()
        script_path = input("\n> ").strip()

        # ✅ Handle numbered selection
        if script_path.isdigit():
            index = int(script_path) - 1
            if 0 <= index < len(script_files):
                script_path = script_files[index]  # Correctly map number to file path
            else:
                print("❌ Invalid selection. Please enter a valid file name or number.")
                exit(1)
        else:
            script_path = script_path if os.path.exists(script_path) else None

        # ✅ Run the selected script
        if script_path:
            run_in_thread(script_path)
        else:
            print("❌ No valid file selected. Exiting NovaScript.")