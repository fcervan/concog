# AGENTS.md - Instruções para Agentes de Código

> **Propósito**: Este arquivo define regras e limites para qualquer IA/assistente trabalhando neste projeto. Leia **antes** de executar qualquer tarefa.

---

## 🚫 Regras de Ouro (NUNCA viole sem autorização explícita)

1. **Alteração mínima**: Faça a MENOR mudança possível que resolva o problema. Não refatore, não "melhore" código adjacente, não adicione features não solicitadas.

2. **Escopo fechado**: Se a tarefa diz "corrija o login", altere APENAS arquivos de autenticação. NÃO toque em uploads, lançamentos, dashboard, banco de dados, integrações ou configuração de ambiente.

3. **Sem instalações automáticas**: NÃO execute `pip install`, `npm install`, `apt-get` ou similar sem permissão explícita. NÃO modifique `requirements.txt`, `package.json` ou `Dockerfile`.

4. **Pergunte antes de expandir**: Se a solução requer mudar algo fora do escopo inicial, PARE e explique o porquê antes de prosseguir.

---

## 📁 Arquivos Protegidos (NÃO modifique sem autorização)

### Infraestrutura & Deploy
- `docker-compose.yml`, `Dockerfile`, `.env`, `.env-example`
- `infra/`, `build/`, `volume/`

### Banco de Dados & Integrações
- `backend/app/integrations.py`
- `backend/app/core/database/` (pool, unit_of_work, base_repository)
- Qualquer arquivo com `uow`, `UnitOfWork` ou conexão a banco

### Serviços de Negócio
- `backend/app/modules/conciliacao_contabil/services/`
- `backend/app/modules/conciliacao_contabil/repositories/`

### IA/ML
- `backend/app/core/ai/` (spacy, llm, prompts)
- `backend/app/core/ai/nlp/spacy/modelo_spacy/`

### Dependências
- `requirements.txt`, `requirements-local.txt`
- `backend/venv/`, `frontend/node_modules/`

---

## ✅ Como Trabalhar Corretamente

### 1. Antes de editar
```
1. Leia os arquivos relevantes
2. Identifique a causa raiz do problema
3. Liste os arquivos que pretende alterar
4. Confirme que estão dentro do escopo permitido
```

### 2. Durante a edição
```
- Mantenha mudanças localizadas
- Preserve estilo e convenções existentes
- Não adicione comentários desnecessários
- Não remova código "morto" sem pedir
```

### 3. Após editar
```
- Liste TODOS os arquivos modificados
- Explique brevemente o que cada mudança faz
- Sugira comandos de teste (se aplicável)
- NÃO rode commits ou pushes sem autorização
```

---

## 🎯 Exemplos de Bom vs Ruim

### ❌ Ruim
**Pedido**: "Corrija o erro de login"
**Ação do agente**: Instala pacotes, modifica integrations.py, ajusta banco de dados, refatora auth.py, altera Dockerfile

### ✅ Bom
**Pedido**: "Corrija o erro de login"
**Ação do agente**: 
1. Identifica que o problema está em `frontend/js/config.js` (porta errada)
2. Altera APENAS esse arquivo
3. Lista a mudança e sugere teste: `curl -X POST http://localhost:8001/auth/login ...`

---

## 🧠 Diretrizes de Comunicação

- **Seja conciso**: Respostas curtas e diretas. Evite explicações longas sem necessidade.
- **Foco na tarefa**: Não sugira melhorias não solicitadas ("seria bom adicionar...", "no futuro poderia...").
- **Transparência**: Se algo não pode ser feito sem alterar arquivos protegidos, diga claramente e peça orientação.
- **Sem surpresas**: Nunca execute comandos que alterem o sistema (instalações, builds, deploys) sem aviso prévio.

---

## 🔧 Comandos Permitidos (sem autorização extra)

| Categoria | Comandos |
|-----------|----------|
| Leitura | `ls`, `cat`, `head`, `grep`, `find`, `git status`, `git diff` |
| Teste | `curl`, `python -c "..."` (apenas para testes rápidos) |
| Edição | Criar/modificar arquivos dentro do escopo da tarefa |

### 🚫 Comandos que exigem autorização
- `pip install`, `npm install`, `apt-get`, `yum`, `brew`
- `docker build`, `docker-compose up`, `systemctl`
- `git commit`, `git push`, `git merge`
- Qualquer comando que altere o ambiente ou repositório permanentemente

---

## 📝 Template de Resposta (use quando editar arquivos)

```
### Arquivos Modificados
- `caminho/do/arquivo1`: breve descrição da mudança
- `caminho/do/arquivo2`: breve descrição da mudança

### O que foi feito
[1-2 linhas explicando a solução]

### Como testar
[comando ou passo para validar]

### Notas
[se algo ficou pendente ou requer atenção]
```

---

> ⚠️ **Lembrete final**: Você é um assistente, não um arquiteto. Sua função é resolver o problema solicitado da forma mais limpa e mínima possível. Se precisar "consertar" algo que não foi pedido, PARE e pergunte.
