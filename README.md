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
| [`pares_referencia.json`](pares_referencia.json) | O protocolo de medição, no nível de pares, confronta a saída do módulo com esse gabarito |

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

Quanto à dificuldade da base, 145 dos 1.000 pares de referência têm título idêntico —
o padrão mais comum de duplicação na plataforma, em que o cadastro é refeito com o
mesmo título — enquanto os demais diferem por caixa, pontuação, sinônimos ou sufixos.
Entre os não-duplicatas, 68 dos 100 têm título idêntico ao do projeto-base
correspondente, de modo que a discriminação desses casos recai inteiramente sobre a
lista de integrantes, na fase de validação.

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

## Licença e uso

A base é inteiramente fictícia. Títulos, descrições, nomes de integrantes e
identificadores Lattes foram inventados e não correspondem a projetos, pesquisadores
ou currículos reais. Pode ser reutilizada livremente para avaliação de métodos de
deduplicação, com citação do artigo de referência.
