# Cross-Platform Installation & Usage

This library is designed to work seamlessly across different operating systems. However, depending on your environment (Windows vs. Linux/macOS), there are a few considerations to ensure the best experience.

## Windows Users

### Shell Environment
The prompts in this library often include example commands (like `grep`, `curl`, `export`).
- **PowerShell (Recommended):** Most commands will work, but you may need to adapt some Unix-specific syntax (e.g., using backticks `` ` `` instead of backslashes `\` for line continuation).
- **Git Bash / WSL:** If you use Git Bash or the Windows Subsystem for Linux (WSL), the commands will work exactly as written.
- **Command Prompt (cmd.exe):** Legacy `cmd.exe` does not support many standard development tools used in the examples. We widely recommend using PowerShell or WSL.

### Path Handling
The library uses standard path separators (`/`) which are generally accepted by modern Windows tools and Node.js environments. If you encounter issues with file paths in generated code, ensure you are using the appropriate separator for your specific toolchain.

### Troubleshooting
If you see errors related to "command not found" in the generated output:
1. **Adapt the command:** The AI might suggest `grep`; on PowerShell, you can use `Select-String`.
2. **Context Matters:** The prompts are instructions *to the AI*. If the AI generates a bash script, and you are on Windows, ask the AI to "convert this to PowerShell".

## Linux & macOS Users

The library is natively optimized for POSIX-compliant environments. No special configuration is usually required.

### Permissions
Ensure you have the necessary permissions to run the `gemini` executable and that it is in your `PATH`.
