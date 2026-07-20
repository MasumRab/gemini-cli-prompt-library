# Semantic Integration Patterns

This reference documents common patterns for integrating semantic tooling into codebases.

## Tree-sitter Integration Patterns

### Python Pattern

```python
# tree_sitter_parser.py
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def parse_code(source_code: str):
    tree = parser.parse(bytes(source_code, "utf8"))
    return tree.root_node
```

### Node.js Pattern

```javascript
// tree-sitter-parser.js
const Parser = require("tree-sitter");
const Python = require("tree-sitter-python");

const parser = new Parser();
parser.setLanguage(Python);

function parseCode(sourceCode) {
  return parser.parse(sourceCode);
}
```

## LSP Server Patterns

### Python (pygls)

```python
# lsp_server.py
from pygls.server import LanguageServer

server = LanguageServer("semantic-lsp", "v0.1")

@server.feature("textDocument/didOpen")
def did_open(ls, params):
    document = params.textDocument
    ls.show_message_log(f"Opened: {document.uri}")
```

### Node.js (vscode-languageserver)

```javascript
// lsp-server.js
const { createConnection, TextDocuments } = require("vscode-languageserver");

const connection = createConnection();
const documents = new TextDocuments();

connection.onInitialize(() => ({
  capabilities: { textDocumentSync: 1 },
}));
```

## AST Analysis Patterns

### Python (ast module)

```python
# ast_analyzer.py
import ast

def analyze_python_ast(source_code: str):
    tree = ast.parse(source_code)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return {
        "functions": [f.name for f in functions],
        "classes": [c.name for c in classes]
    }
```

### JavaScript (babel/estree)

```javascript
// ast-analyzer.js
const babel = require("@babel/parser");

function analyzeJsAst(sourceCode) {
  const ast = babel.parse(sourceCode, { sourceType: "module" });
  const functions = [];
  const classes = [];

  // walk AST and collect
  return { functions, classes };
}
```

## Validation Checklist

When adding semantic tools, verify:

1. **Tree-sitter**
   - [ ] Parser loads without error
   - [ ] Query captures expected nodes
   - [ ] Handles edge cases (syntax errors, partial code)

2. **LSP**
   - [ ] Server starts and responds to initialize
   - [ ] Handles textDocument/didChange
   - [ ] Provides completions/hover for test files

3. **AST Analyzer**
   - [ ] Parses all target languages
   - [ ] Extracts expected symbols
   - [ ] Handles malformed input gracefully
