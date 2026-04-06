# Configuração do Editor (VSCode/Cursor)

Este guia ajuda você a configurar o editor para formatar automaticamente o código ao salvar.

## 📦 Extensões Necessárias

Instale as seguintes extensões no VSCode/Cursor:

### Essenciais para Python:

1. **Python** (`ms-python.python`)
   - Suporte principal para Python
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

2. **Black Formatter** (`ms-python.black-formatter`)
   - Formatador automático de código
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)

3. **isort** (`ms-python.isort`)
   - Organização automática de imports
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)

4. **Ruff** (`charliermarsh.ruff`)
   - Linter rápido e moderno
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

5. **Mypy Type Checker** (`ms-python.mypy-type-checker`)
   - Verificação de tipos
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker)

### Recomendadas:

6. **EditorConfig** (`EditorConfig.EditorConfig`)
   - Suporte ao `.editorconfig`
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)

7. **Even Better TOML** (`tamasfe.even-better-toml`)
   - Suporte para arquivos TOML
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)

8. **YAML** (`redhat.vscode-yaml`)
   - Suporte para arquivos YAML
   - [Instalar](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

## 🚀 Instalação Rápida

### Opção 1: Via Linha de Comando

Se você usar VSCode, pode instalar todas as extensões de uma vez:

```bash
# Extensões essenciais
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension charliermarsh.ruff
code --install-extension ms-python.mypy-type-checker

# Extensões recomendadas
code --install-extension EditorConfig.EditorConfig
code --install-extension tamasfe.even-better-toml
code --install-extension redhat.vscode-yaml
```

### Opção 2: Via Interface

1. Abra o VSCode/Cursor
2. Pressione `Cmd+Shift+X` (Mac) ou `Ctrl+Shift+X` (Windows/Linux)
3. Procure cada extensão pelo nome
4. Clique em "Install"

### Opção 3: Recomendações Automáticas

1. Abra o projeto no VSCode/Cursor
2. Uma notificação aparecerá sugerindo instalar as extensões recomendadas
3. Clique em "Install All"

## ⚙️ Configurações Aplicadas

As configurações já estão no arquivo `.vscode/settings.json`:

### Formatação Automática ao Salvar
```json
"editor.formatOnSave": true
```

### Organização de Imports ao Salvar
```json
"editor.codeActionsOnSave": {
  "source.organizeImports": "explicit",
  "source.fixAll": "explicit"
}
```

### Indentação Python (4 espaços)
```json
"[python]": {
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.detectIndentation": false
}
```

### Linha Máxima (100 caracteres)
```json
"black-formatter.args": ["--line-length=100"],
"[python]": {
  "editor.rulers": [100]
}
```

## ✅ Verificação

Para verificar se está funcionando:

1. **Abra um arquivo Python** (ex: `main.py`)

2. **Adicione código mal formatado:**
   ```python
   def test(   ):
       x=1+2
       y    =    3
       return x+y
   ```

3. **Salve o arquivo** (`Cmd+S` ou `Ctrl+S`)

4. **O código deve ser formatado automaticamente:**
   ```python
   def test():
       x = 1 + 2
       y = 3
       return x + y
   ```

## 🔧 Solução de Problemas

### A formatação não está funcionando?

1. **Verifique se o ambiente virtual está ativado:**
   - Pressione `Cmd+Shift+P` → "Python: Select Interpreter"
   - Escolha o interpretador do venv: `./venv/bin/python`

2. **Verifique se o Black está instalado:**
   ```bash
   ./venv/bin/black --version
   ```

3. **Reinicie o VSCode/Cursor**

4. **Verifique a saída do formatador:**
   - Pressione `Cmd+Shift+U` → selecione "Black Formatter"
   - Veja se há erros

### Imports não estão sendo organizados?

1. **Verifique se o isort está instalado:**
   ```bash
   ./venv/bin/isort --version
   ```

2. **Salve o arquivo com `Cmd+Shift+S`** (Save All)

3. **Execute manualmente:**
   - Pressione `Cmd+Shift+P` → "Organize Imports"

### Linter não está funcionando?

1. **Verifique se o Ruff está instalado:**
   ```bash
   ./venv/bin/ruff --version
   ```

2. **Veja os problemas:**
   - Pressione `Cmd+Shift+M` para abrir o painel de problemas

## 🎯 Atalhos Úteis

| Ação | Mac | Windows/Linux |
|------|-----|---------------|
| Salvar | `Cmd+S` | `Ctrl+S` |
| Formatar Documento | `Shift+Option+F` | `Shift+Alt+F` |
| Organizar Imports | `Shift+Option+O` | `Shift+Alt+O` |
| Comando Rápido | `Cmd+Shift+P` | `Ctrl+Shift+P` |
| Painel de Problemas | `Cmd+Shift+M` | `Ctrl+Shift+M` |

## 📝 Dicas

1. **Use `Cmd+S` frequentemente** - A formatação acontece automaticamente
2. **Observe a régua em 100 caracteres** - Indica o limite de linha
3. **Preste atenção aos problemas** - O editor mostra sublinhados para erros
4. **Use o terminal integrado** - `Ctrl+` ` para abrir

## 🆘 Precisa de Ajuda?

Se algo não estiver funcionando:

1. Verifique se todas as extensões estão instaladas
2. Certifique-se de que o venv está ativado
3. Reinicie o editor
4. Execute `make check` no terminal para ver se há erros

---

**Pronto!** Agora seu editor está configurado para formatar automaticamente ao salvar! 🎉
