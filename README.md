# Base sintética de avaliação do *deduply*

Material complementar ao artigo **"Deduplicação semântica de registros na Plataforma
Lattes: um módulo baseado em similaridade vetorial"** (III MCSM, 2026).

Este diretório reúne a base sintética usada na avaliação quantitativa do módulo, a
especificação que orientou sua geração e o gabarito de pares duplicados, de modo que
os resultados de precisão, *recall* e *F1-score* relatados no artigo possam ser
reproduzidos e auditados de forma independente.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`base_sintetica.json`](base_sintetica.json) | Os 600 registros de projetos de pesquisa (`id`, `titulo_projeto`, `descricao_projeto`, `lattes_ids`, `nomes_integrante`) |
| [`pares_referencia.json`](pares_referencia.json) | Os 1.000 pares de referência (gabarito), como listas `[a, b]` com `a < b` |
| [`especificacao-geracao.md`](especificacao-geracao.md) | A especificação (*prompt*) que orientou a geração da base |
| [`scripts/generate_test_batch.py`](scripts/generate_test_batch.py) | O gerador: os 100 projetos-base e as regras determinísticas de derivação |
| [`scripts/ablacao_codigo.py`](scripts/ablacao_codigo.py) | O protocolo de medição no nível de pares e a ablação do código de cadastro |

## Organização da base

Os 600 registros formam 100 quíntuplas de duplicatas e 100 registros isolados:

| Bloco | IDs | Papel |
|---|---|---|
| Base | 1–100 | Projeto original |
| 1ª duplicata | 101–200 | Reescrita e erros de ortografia (ruído baixo) |
| 2ª duplicata | 201–300 | Paráfrase com ruído mais acentuado |
| 3ª duplicata | 301–400 | Descrição ausente |
| 4ª duplicata | 401–500 | Lista de integrantes incompleta (1 autor) |
| Não-duplicata | 501–600 | Conteúdo semanticamente próximo, integrantes inteiramente distintos |

O gabarito é **estrutural**: para cada `n` de 1 a 100, os registros
`(n, n+100, n+200, n+300, n+400)` referem-se ao mesmo projeto. Os pares de referência
são todos os pares internos a cada quíntupla, totalizando
100 × C(5,2) = **1.000 pares duplicados**. Os registros 501–600 não são duplicata de
nenhum outro e funcionam como negativos difíceis para a fase de validação.

## Protocolo de geração

A construção da base ocorreu em duas etapas com papéis deliberadamente separados.

### Etapa 1 — Corpus-base (modelo generativo)

O modelo *Claude Sonnet 4.6* (Anthropic) redigiu os **100 projetos-base** (IDs 1–100):
título, descrição, lista de integrantes e identificador Lattes fictício, distribuídos
por dez domínios do conhecimento (educação, biologia, computação, agronomia, saúde,
ciências sociais, engenharia, letras, ciências exatas e ciências ambientais). O papel
do modelo limitou-se a produzir texto acadêmico plausível em português; ele **não
decidiu quais registros são duplicatas**, não produziu as variantes e não atribuiu
rótulos.

Esses 100 registros estão fixados literalmente no dicionário `PROJECTS_DATA` de
[`generate_test_batch.py`](scripts/generate_test_batch.py), o que torna a base
integralmente reproduzível sem nova chamada ao modelo.

### Etapa 2 — Registros derivados (transformações determinísticas)

Os 500 registros restantes são obtidos dos projetos-base por funções determinísticas
de manipulação de *string*, sem qualquer participação de modelo de linguagem. As
regras são fixas, auditáveis e selecionadas por aritmética sobre o identificador:

| Função | IDs | Transformações |
|---|---|---|
| `make_duplicate_v1` | 101–200 | Caixa alta no título, `" - "` → `": "`, ponto final; uma substituição lexical de lista fixa na descrição; normalização de caixa nos autores; erro de 1 dígito no `lattes_ids` |
| `make_duplicate_v2` | 201–300 | Substituição de palavra-chave do título por sinônimo de lista fixa; múltiplas paráfrases de lista fixa e truncamento das duas últimas (ou da primeira) frases; remoção do último autor ou inversão `Nome Sobrenome` → `SOBRENOME, Nome`; variação de 2 dígitos no `lattes_ids` |
| `make_v3` | 301–400 | Sufixo fixo no título (`" - Relatório Final"`, `" - Fase 2"`, …); **descrição vazia**; variação de formato dos autores |
| `make_v4` | 401–500 | Variação sutil de título e descrição (mesmo nível de `v1`); **apenas 1 autor** da lista original |
| `make_non_dup` | 501–600 | Título e descrição próximos ao base; **conjunto de autores e `lattes_ids` inteiramente novo**, sem sobreposição com os registros 1–500 |

Reprodução:

```bash
python3 scripts/generate_test_batch.py --status          # situação dos 20 lotes
python3 scripts/generate_test_batch.py --batch <1-20>    # regenera um lote
python3 scripts/generate_test_batch.py --merge           # consolida em base_sintetica.json
```

### Verificações realizadas

600 registros, IDs de 1 a 600 sem lacunas nem repetição, todos os campos presentes,
bloco 301–400 com descrição vazia, bloco 401–500 com exatamente um autor por registro,
bloco 501–600 sem qualquer sobreposição de autores com 1–100, descrições distintas
dentro de cada quíntupla e títulos-base distintos entre quíntuplas.

## Sobre o risco de circularidade metodológica

Uma objeção legítima a bases sintéticas geradas por modelos de linguagem é a
**circularidade**: se o mesmo tipo de modelo produz os dados e resolve a tarefa, o
resultado pode medir a afinidade entre modelos em vez da eficácia do método. Três
características do protocolo delimitam esse risco.

**1. Não há LLM no pipeline avaliado.** O *deduply* opera com lematização via *spaCy*,
*embeddings* de sentença do modelo `all-MiniLM-L6-v2` (*sentence-transformers*) e busca
vetorial com *FAISS*. Trata-se de um codificador de sentenças, sem relação de família,
arquitetura ou dados de treinamento com o modelo generativo empregado na Etapa 1.
Nenhuma fase — *blocking*, *matching* ou *clustering* — invoca um modelo generativo.

**2. O modelo generativo não produziu as duplicatas nem os rótulos.** A relação de
duplicidade é introduzida na Etapa 2, por transformações textuais determinísticas
especificadas antes da geração, e o gabarito decorre da aritmética de identificadores.
Não existe, portanto, caminho pelo qual o modelo generativo pudesse marcar pares
duplicados com algum padrão latente que o codificador viesse a reconhecer: o modelo
sequer teve acesso à noção de par ao redigir o corpus-base.

**3. Os negativos difíceis são construídos contra o próprio método.** Os registros
501–600 preservam a proximidade semântica de título e descrição e alteram apenas os
integrantes — exatamente o sinal de que a fase de validação depende. São casos
deliberadamente adversos, e não amostras favoráveis ao pipeline.

**Limitação residual.** O que o protocolo não elimina é a **regularidade estilística**
do corpus-base: texto redigido por um modelo de linguagem tende a ser mais padronizado
e coeso do que os registros reais da Plataforma Lattes, que apresentam truncamentos,
erros de digitação, siglas, alternância de idioma e ruído de codificação. Essa
regularidade pode tornar a fase de *blocking* mais fácil do que no cenário real. Os
valores absolutos de precisão e *recall* relatados no artigo devem, por isso, ser
lidos como referência obtida em condições controladas, e não como previsão de
desempenho sobre dados reais. Trata-se de uma limitação relativa ao **realismo
distribucional** da base — e não de circularidade entre gerador e avaliado.

## Nota: o código de cadastro removido dos títulos

Os 100 projetos-base foram redigidos com um código de cadastro no início do título
(`"12045.21.00001.03 - "`), cerca de 18% dos caracteres. Esse código **não tem
contrapartida nos títulos de projeto da Plataforma Lattes** e, na base derivada, era
constante dentro de cada quíntupla — e igual ao do registro não-duplicata (5xx)
correspondente, de modo que os 600 registros se distribuíam por apenas 100 códigos.
Ele é removido na mesclagem (`remove_codigo_cadastro`, em
[`generate_test_batch.py`](scripts/generate_test_batch.py)), e a base publicada
contém apenas o título do projeto.

O efeito da remoção foi medido antes da decisão, reexecutando as oito configurações
sobre três variantes que diferiam **apenas** no título — a base com o código como fora
gerada, sem o código, e com um código distinto por registro. Os valores brutos estão em
[`ablacao-codigo.json`](ablacao-codigo.json); a coluna do meio é a base atual.

| # | τ_g | τ_v | com código | **sem código (atual)** | código único por registro |
|---|---|---|---|---|---|
| 1 | 0,8500 | 0,700 | 1,0000 / 0,4120 / 0,5836 | **1,0000 / 0,4220 / 0,5935** | 1,0000 / 0,4120 / 0,5836 |
| 2 | 0,8500 | 0,700 | 1,0000 / 0,7480 / 0,8558 | **1,0000 / 0,7410 / 0,8512** | 1,0000 / 0,7230 / 0,8392 |
| 3 | 0,8500 | 0,700 | 1,0000 / 0,7480 / 0,8558 | **1,0000 / 0,7410 / 0,8512** | 1,0000 / 0,7230 / 0,8392 |
| 4 | 0,9350 | 0,700 | 1,0000 / 0,6670 / 0,8002 | **1,0000 / 0,6410 / 0,7812** | 1,0000 / 0,4910 / 0,6586 |
| 5 | 0,7650 | 0,700 | 1,0000 / 0,7520 / 0,8584 | **1,0000 / 0,7520 / 0,8584** | 1,0000 / 0,7480 / 0,8558 |
| 6 | 0,7650 | 0,770 | 1,0000 / 0,6440 / 0,7835 | **1,0000 / 0,6440 / 0,7835** | 1,0000 / 0,6410 / 0,7812 |
| 7 | 0,7650 | 0,630 | 0,9849 / 0,9120 / 0,9470 | **0,9849 / 0,9120 / 0,9470** | 0,9848 / 0,9080 / 0,9448 |
| 8 | 0,6885 | 0,567 | 0,8127 / 0,9760 / 0,8869 | **0,8668 / 0,9760 / 0,9182** | 0,8013 / 0,9760 / 0,8801 |

Três leituras:

**1. A configuração de melhor desempenho é insensível ao código.** No experimento 7 as
três variantes coincidem até a quarta casa (F1 = 0,9470; 0,9448 com códigos únicos). Em
τ_g = 0,765 o conteúdo do título já resolve o agrupamento, e o código não participa da
decisão.

**2. O código inflava o *recall* em τ_g alto.** No experimento 4 (τ_g = 0,935) o
*recall* caía de 0,6670 para 0,4910 quando cada registro recebia um código próprio.
Nesse regime o agrupamento é tão restritivo que eram os caracteres do código
compartilhado que levavam muitos pares acima do limiar.

**3. O código era ruído para o codificador, não sinal.** A lematização remove a
pontuação, de modo que todo código vira uma sequência de dígitos; o codificador mapeia
essas sequências para uma região estreita do espaço vetorial e aproxima títulos sem
relação entre si. No experimento 8, os falsos positivos entre quíntuplas distintas caem
de 90 para 25 com a remoção, elevando a precisão de 0,8127 para 0,8668.

**Efeito colateral registrado.** Para 40% do bloco `v1` e parte do `v4`, a variação de
título produzida pelo gerador incidia sobre o próprio código (troca de `" - "` por
`": "`, pontos por vírgulas). Com o código removido, esses títulos passam a ser
idênticos ao do projeto-base: dos 1.000 pares de referência, 145 têm título idêntico
(eram 85), e 68 dos 100 registros não-duplicatas têm título idêntico ao seu base (eram
48). O primeiro efeito facilita o *blocking* desses pares; o segundo torna os negativos
mais difíceis, já que a discriminação recai inteiramente sobre os integrantes. Título
idêntico entre dois cadastros do mesmo projeto é, de resto, o padrão de duplicação mais
comum na plataforma.

Reprodução da ablação:

```bash
python3 -m venv .venv && .venv/bin/pip install -e /caminho/para/deduply
KMP_DUPLICATE_LIB_OK=TRUE OMP_NUM_THREADS=1 .venv/bin/python scripts/ablacao_codigo.py
```

## Licença e uso

A base é inteiramente fictícia. Títulos, descrições, nomes de integrantes e
identificadores Lattes foram inventados e não correspondem a projetos, pesquisadores
ou currículos reais. Pode ser reutilizada livremente para avaliação de métodos de
deduplicação, com citação do artigo de referência.
