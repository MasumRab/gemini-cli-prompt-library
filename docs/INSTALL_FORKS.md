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
