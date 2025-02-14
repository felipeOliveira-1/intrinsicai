# Análise de Valor Intrínseco de Ações

## Abordagem de Valuation de acordo com Warren Buffett

Este programa foi concebido com base em princípios de valuation que seguem a filosofia de Warren Buffett, um dos maiores investidores de todos os tempos. Buffett ensina que o valor intrínseco de uma empresa é determinado pela soma dos fluxos de caixa futuros descontados ao valor presente, ou seja, o quanto a empresa “imprime dinheiro” a cada ano. Ao calcular o valor intrínseco, o investidor compara esse número com a capitalização de mercado da empresa para identificar oportunidades onde o preço atual está significativamente abaixo do valor real do negócio. Essa margem de segurança é crucial para minimizar os riscos, uma vez que o futuro é incerto e nem todas as projeções se concretizam.

A importância deste programa reside em proporcionar uma ferramenta prática e interativa que permita ao investidor:
- **Entender e aplicar os fundamentos do valuation**: Ao focar em elementos como o fluxo de caixa livre (FCF), o crescimento projetado e o desconto desses fluxos com uma taxa adequada (WACC ou outra taxa de retorno desejada), o usuário pode estimar de forma fundamentada o valor intrínseco da empresa.
- **Tomar decisões de investimento informadas**: Comparar o valor intrínseco calculado com o preço de mercado ajuda a identificar ações potencialmente subavaliadas, oferecendo uma visão clara dos riscos e oportunidades.
- **Incorporar uma abordagem conservadora e robusta**: Seguindo a metodologia de Buffett, que enfatiza a importância da margem de segurança, o programa oferece uma análise que visa proteger o investidor contra previsões excessivamente otimistas e incertezas do mercado.

Esta ferramenta é essencial para investidores que desejam aplicar uma análise financeira sólida e baseada em princípios consagrados, facilitando a identificação de oportunidades de compra que possam oferecer retornos superiores a longo prazo.

---

## Análise de Valor Intrínseco de Ações

Uma ferramenta profissional que combina análise financeira tradicional com inteligência artificial para avaliar ações. O programa oferece uma interface interativa e amigável, permitindo buscar empresas tanto pelo nome quanto pelo ticker.

### Funcionalidades Principais

#### 1. Interface Interativa
- Menu principal intuitivo  
- Navegação simplificada  
- Interface colorida e bem formatada  
- Mensagens claras e informativas

<div align="center">
  <img src="docs/imgs/first.jpeg" alt="Tela principal do programa" width="600">
</div>

#### 2. Busca Inteligente de Ações
- Busca por nome da empresa usando IA  
- Identificação automática do ticker correto  
- Suporte para ações brasileiras (B3) e americanas (NYSE/NASDAQ)  
- Validação e confirmação do ticker encontrado

<div align="center">
  <img src="docs/imgs/second.jpeg" alt="Busca por nome e identificação do ticker" width="600">
</div>

#### 3. Análise Financeira Completa
- Cálculo do valor intrínseco  
- Análise do Fluxo de Caixa Livre (FCF)  
- Métricas de qualidade e crescimento  
- Formatação inteligente de números (B para bilhões, M para milhões)

<div align="center">
  <img src="docs/imgs/third.jpeg" alt="Detalhes da análise financeira" width="600">
</div>

#### 4. Análise com IA
- Avaliação detalhada por IA especialista  
- Contexto de mercado  
- Riscos e oportunidades  
- Recomendações personalizadas

<div align="center">
  <img src="docs/imgs/fourth.jpeg" alt="Análise com IA" width="600">
</div>

<div align="center">
  <img src="docs/imgs/fifth.jpeg" alt="Recomendações e insights" width="600">
</div>

---

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
   - Crie um arquivo `.env` no diretório `backend`
   - Adicione sua chave:
     ```bash
     OPENAI_API_KEY=sua_chave_api_aqui
     ```

---

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
   - Veja informações detalhadas, instruções de uso e dicas importantes

   **Opção 4: Sair**
   - Encerra o programa

---

## Estrutura do Projeto

### Módulos Principais
- `main.py`: Interface do usuário e controle principal  
- `ticker_finder.py`: Identificação inteligente de tickers  
- `yahoo_finance.py`: Obtenção de dados financeiros  
- `ai_analysis.py`: Análise especializada com IA

---

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

---

## Dependências Principais
- `yfinance`: Dados financeiros  
- `openai`: Análise com IA  
- `rich`: Interface do usuário  
- `typer`: CLI  
- `pandas`: Manipulação de dados

---

## Segurança
- Nunca compartilhe sua chave API  
- Mantenha o arquivo `.env` seguro  
- Use apenas em ambiente confiável

---

## Suporte

Para dúvidas ou problemas, abra uma issue no [GitHub do projeto](https://github.com/felipeOliveira-1/intrinsicai/tree/main).
