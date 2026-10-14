# 🌐 GraphRAG Decision Support Web App

**Frontend:** Next.js 15 (App Router, TypeScript, Tailwind CSS, Lucide Icons)  
**Backend:** FastAPI / Python Serverless (`api/index.py`)  
**Mecanismo de Grafo:** Neo4j (AuraDB Free) + NetworkX (Fallback in-memory)  
**Provedor de IA:** Google Gemini API (`text-embedding-004` e `gemini-2.5-flash`)

---

## 🚀 Execução Rápida

### 1. Instalação das Dependências

Na raiz deste diretório (`graphrag-web`):

```bash
# Dependências do frontend
npm install

# Dependências do backend Python
pip install -r api/requirements.txt
```

### 2. Configuração de Variáveis de Ambiente

Crie o arquivo `.env` baseado no `.env.example`:

```bash
copy .env.example .env
```

Conteúdo esperado:

```env
# Google AI Studio API Key (Gratuita)
GEMINI_API_KEY=sua_chave_aqui

# Neo4j AuraDB Free ou Local (Opcional - caso ausente, usa NetworkX em memória)
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=sua_senha_aqui
```

### 3. Execução Local

```bash
npm run dev
```

Acesse [http://localhost:3000](http://localhost:3000).

---

## 🔌 Especificação dos Endpoints da API

O Next.js redireciona automaticamente qualquer chamada `/api/*` para o microserviço FastAPI localizado em `api/index.py`:

| Método | Endpoint | Descrição |
| :---: | :--- | :--- |
| **GET** | `/api/health` | Verifica status da conexão com Neo4j, nós carregados e status da chave Gemini. |
| **GET** | `/api/ontology` | Retorna todos os nós e arestas cadastrados na ontologia do corpus. |
| **POST**| `/api/query` | Executa a recuperação em 4 etapas (embedding, expansão topológica e formatação LLM), além do baseline vetorial se solicitado. |
| **POST**| `/api/evaluate` | Executa a bateria de 20 testes com gabarito formal e retorna o *Hit Rate* e a *Taxa de Fabricação*. |

### Exemplo de Payload para `/api/query`:

```json
{
  "query": "Como apoiar a tomada de decisão na gestão de atrasos de obras?",
  "top_k": 2,
  "max_hops": 2,
  "use_neo4j": false,
  "comparar_baseline": true
}
```

---

## ☁️ Deploy na Vercel (Custo R$ 0,00)

A aplicação foi projetada para deploy sem a necessidade de contêineres Docker:

1. Suba o código para um repositório no GitHub.
2. No painel da [Vercel](https://vercel.com), importe o repositório.
3. Configure o **Root Directory** como `graphrag-web`.
4. Em **Environment Variables**, adicione `GEMINI_API_KEY`, `NEO4J_URI`, `NEO4J_USERNAME` e `NEO4J_PASSWORD`.
5. Clique em **Deploy**. A Vercel compilará o frontend Next.js e o backend Python serverless simultaneamente.
