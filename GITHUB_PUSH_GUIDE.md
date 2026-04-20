# 📚 GUIA: Como Fazer Push do SENTRA para GitHub

## ✅ O que já foi feito:
- ✓ Repositório Git local inicializado
- ✓ Todos os arquivos adicionados e commitados
- ✓ `.gitignore` criado para excluir arquivos desnecessários
- ✓ README.md com documentação completa

## 🚀 Próximos Passos - Execute na ordem:

### 1. Crie um repositório vazio no GitHub

Abra o navegador e vá para: https://github.com/new

**Configure assim:**
- **Repository name**: `sentra` (ou outro nome que preferir)
- **Description**: Scanner de Segurança de Redes (opcional)
- **Public** ou **Private**: Sua escolha
- **Desmarque**: "Initialize this repository with:"
- **Clique**: "Create repository"

**Você receberá uma URL como:**
```
https://github.com/seu-usuario/sentra.git
```

---

### 2. No PowerShell, execute na pasta do projeto:

```powershell
cd "c:\Users\CLIENTE\Desktop\Sentra\Sentra"
```

### 3. Adicione o repositório remoto:

```powershell
git remote add origin https://github.com/seu-usuario/sentra.git
```

**Substitua:**
- `seu-usuario` pelo seu username do GitHub

### 4. Faça o push da branch main:

```powershell
git branch -M main
git push -u origin main
```

**Na primeira vez, pode pedir autenticação:**
- **Username**: seu email do GitHub
- **Password**: seu Personal Access Token (veja abaixo se não tiver)

---

### 5. (SE SOLICITADO) Criar um Personal Access Token:

Se o Git pedir autenticação e você não tiver um token:

1. Vá para: https://github.com/settings/tokens/new
2. **Clique em**: "Generate new token (classic)"
3. **Nome**: `git-cli` (ou similar)
4. **Selecione escopos**:
   - ✓ `repo` (acesso completo a repositórios privados e públicos)
   - ✓ `workflow` (para actions)
5. **Clique**: "Generate token"
6. **Copie** o token exibido (só aparece uma vez!)
7. **Use** esse token como senha no PowerShell

---

### ✨ Resultado Final:

Após todos os passos, você verá:
```
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

**E seu repositório estará no GitHub com:**
- ✅ Todos os arquivos do projeto
- ✅ README.md com descrição profissional
- ✅ Histórico de commits
- ✅ Copyright e direitos reservados declarados
- ✅ Pronto para apresentar aos professores!

---

## 📝 Resumo do que foi feito localmente:

```
✅ git init - Inicializado repositório local
✅ .gitignore - Criado para excluir arquivos desnecessários
✅ git add . - Todos os 33 arquivos adicionados
✅ git commit - Commit inicial com mensagem descritiva
```

**Commit Hash**: `9ddd7bb`

---

## 💡 Comandos úteis depois:

```powershell
# Ver status
git status

# Ver histórico
git log

# Ver remoto
git remote -v

# Fazer novo commit (depois de editar arquivos)
git add .
git commit -m "Descrição da mudança"
git push
```

---

**Agora é com você! Siga os 5 passos acima no PowerShell para fazer o push! 🚀**
