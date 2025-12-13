# Installation for Gemini CLI Forks

This prompt library is compatible with `gemini-cli` forks such as `qwen-code` and `llxprt`. Since these tools share the same underlying extension architecture, you can install this library using their respective CLI commands.

## qwen-code

To install the library with `qwen-code`:

```bash
qwen-code extensions install yourusername/prompt-library-extension
```

Or for local development:

```bash
git clone https://github.com/yourusername/prompt-library-extension.git
cd prompt-library-extension
qwen-code extensions link .
```

## llxprt

To install the library with `llxprt`:

```bash
llxprt extensions install yourusername/prompt-library-extension
```

Or for local development:

```bash
git clone https://github.com/yourusername/prompt-library-extension.git
cd prompt-library-extension
llxprt extensions link .
```

## Usage

Once installed, the slash commands will work identically to the standard `gemini-cli`.

```bash
# Example
/code-review:security "path/to/file.js"
```

*Note: Replace `yourusername` with the actual GitHub username or organization where this repository is hosted.*

---

## 🔧 Developer Guide: Porting Gemini Extensions to Qwen

If you have an existing Gemini CLI extension and want to make it compatible with `qwen-code`, follow these steps.

### 1. Create `qwen-extension.json`

Create a new file named `qwen-extension.json` in the root of your repository. This file mirrors the structure of `gemini-extension.json`.

```json
{
  "name": "your-extension-name",
  "version": "1.0.0",
  "contextFileName": "QWEN.md"
}
```

- **name**: Should generally match your `gemini-extension.json` name.
- **contextFileName**: This is the critical field. It tells `qwen-code` which markdown file serves as the registry for your prompts/commands.

### 2. Create the Context Registry File

Create the markdown file referenced in `contextFileName` (e.g., `QWEN.md`).

You can typically copy your existing `GEMINI.md` file:

```bash
cp GEMINI.md QWEN.md
```

This file is used by the tool to understand available commands and context. Ensure the content is appropriate for the Qwen environment (e.g., updating references if necessary), though often an exact copy works fine.

### 3. Verify

Run `qwen-code extensions link .` in your directory to test that the extension is recognized and loaded correctly.
