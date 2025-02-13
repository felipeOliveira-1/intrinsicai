# Stock Intrinsic Value Analysis Tool

Uma ferramenta de linha de comando que analisa ações com base em seu Fluxo de Caixa Livre (FCF) e fornece análise especializada usando IA para determinar se são boas oportunidades de investimento.

## Funcionalidades

- Interface interativa com menu principal
- Busca de ações por nome da empresa ou ticker
- Identificação automática de tickers usando IA
- Suporte para ações brasileiras (B3) e americanas (NYSE/NASDAQ)
- Análise de valor intrínseco usando FCF
- Análise especializada usando GPT-4
- Interface bonita com cores e formatação
- Tratamento robusto de erros
- Formatação inteligente de números (B para bilhões, M para milhões)

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

3. Configure sua chave da API OpenAI no arquivo .env:
```bash
OPENAI_API_KEY=sua_chave_api_aqui
```

## Uso

Execute o programa:
```bash
python main.py
```

### Menu Principal

O programa apresentará um menu interativo com as seguintes opções:

1. **Analisar por nome da empresa**
   - Digite o nome da empresa (ex: "Petrobras")
   - A IA identificará o ticker correto
   - Confirme se deseja usar o ticker encontrado
   - Veja a análise completa

2. **Analisar por ticker**
   - Digite o ticker diretamente
   - Para ações brasileiras, use .SA (ex: PETR4.SA)
   - Para ações americanas, use o ticker normal (ex: AAPL)

3. **Sobre o programa**
   - Informações sobre funcionalidades
   - Instruções de uso
   - Observações importantes

4. **Sair**
   - Encerra o programa

### Exemplos de Uso

#### 1. Análise por Nome da Empresa

```bash
python main.py
# Escolha opção 1
# Digite: Petrobras
```

O programa vai:
- Identificar o ticker correto (PETR4.SA)
- Mostrar informações sobre o ticker
- Pedir confirmação
- Realizar a análise completa

#### 2. Análise por Ticker

```bash
python main.py
# Escolha opção 2
# Digite: PETR4.SA
```

Para ações brasileiras, adicione .SA:
```bash
PETR4.SA  # Petrobras
VALE3.SA  # Vale
ITUB4.SA  # Itaú
```

Para ações americanas, use o ticker normal:
```bash
AAPL  # Apple
MSFT  # Microsoft
GOOGL # Google
```

### Análise Fornecida

Para cada ação, o programa mostra:
1. **Dados Básicos**
   - Preço atual e market cap
   - Fluxo de caixa operacional
   - CAPEX e outros dados financeiros

2. **Análise de Valor**
   - Cálculo do valor intrínseco
   - Preço justo com margem de segurança
   - Recomendação de compra/venda

3. **Análise da IA**
   - Contexto de mercado
   - Análise fundamentalista
   - Riscos e oportunidades
   - Recomendações detalhadas

## Observações

- Para ações brasileiras, sempre use o sufixo .SA
- A análise considera dados históricos e projeções
- As recomendações da IA são baseadas em dados públicos
- O programa requer conexão com internet
- Mantenha sua chave API segura no arquivo .env
