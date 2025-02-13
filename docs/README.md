# Análise de Valor Intrínseco de Ações

Uma ferramenta profissional que combina análise financeira tradicional com inteligência artificial para avaliar ações. O programa oferece uma interface interativa e amigável, permitindo buscar empresas tanto pelo nome quanto pelo ticker.

## Funcionalidades Principais

### 1. Interface Interativa
- Menu principal intuitivo
- Navegação simplificada
- Interface colorida e bem formatada
- Mensagens claras e informativas

### 2. Busca Inteligente de Ações
- Busca por nome da empresa usando IA
- Identificação automática do ticker correto
- Suporte para ações brasileiras (B3) e americanas (NYSE/NASDAQ)
- Validação e confirmação do ticker encontrado

### 3. Análise Financeira Completa
- Cálculo do valor intrínseco
- Análise do Fluxo de Caixa Livre (FCF)
- Métricas de qualidade e crescimento
- Formatação inteligente de números (B para bilhões, M para milhões)

### 4. Análise com IA
- Avaliação detalhada por IA especialista
- Contexto de mercado
- Riscos e oportunidades
- Recomendações personalizadas

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/felipeOliveira-1/intrinsicai.git
cd intrinsicai
```

2. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure sua chave da API OpenAI:
- Crie um arquivo `.env` no diretório backend
- Adicione sua chave:
```bash
OPENAI_API_KEY=sua_chave_api_aqui
```

## Como Usar

1. Inicie o programa:
```bash
cd backend
python main.py
```

2. No menu principal, escolha uma opção:

   **Opção 1: Analisar por nome da empresa**
   - Digite o nome da empresa (ex: "Petrobras", "Intel")
   - A IA identificará o ticker correto
   - Confirme se deseja usar o ticker encontrado
   - Veja a análise completa

   **Opção 2: Analisar por ticker**
   - Digite o ticker diretamente
   - Para ações brasileiras: use .SA (ex: PETR4.SA)
   - Para ações americanas: use o ticker normal (ex: AAPL)

   **Opção 3: Sobre o programa**
   - Veja informações detalhadas
   - Instruções de uso
   - Dicas importantes

   **Opção 4: Sair**
   - Encerra o programa

## Estrutura do Projeto

### Módulos Principais
- `main.py`: Interface do usuário e controle principal
- `ticker_finder.py`: Identificação inteligente de tickers
- `yahoo_finance.py`: Obtenção de dados financeiros
- `ai_analysis.py`: Análise especializada com IA

## Observações Importantes

1. **Ações Brasileiras**
   - Use sempre o sufixo .SA
   - Ex: PETR4.SA, VALE3.SA, ITUB4.SA

2. **Ações Americanas**
   - Use o ticker oficial
   - Ex: AAPL, MSFT, GOOGL

3. **Análise da IA**
   - Baseada em dados públicos
   - Considera múltiplos fatores
   - Fornece recomendações contextualizadas

4. **Requisitos**
   - Conexão com internet
   - Python 3.8 ou superior
   - Chave API OpenAI válida

## Dependências Principais
- `yfinance`: Dados financeiros
- `openai`: Análise com IA
- `rich`: Interface do usuário
- `typer`: CLI
- `pandas`: Manipulação de dados

## Segurança
- Nunca compartilhe sua chave API
- Mantenha o arquivo .env seguro
- Use apenas em ambiente confiável

## Suporte
Para dúvidas ou problemas, abra uma issue no GitHub do projeto.
