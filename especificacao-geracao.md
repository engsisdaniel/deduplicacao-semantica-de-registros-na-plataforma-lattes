# Especificação de Geração da Base Sintética

> **Nota sobre este documento.** Esta é a especificação que orientou a construção da
> base sintética de avaliação, elaborada e refinada ao longo de uma sessão de trabalho
> com o modelo *Claude Sonnet 4.6* (Anthropic). Não se trata de um único *prompt*
> literal: a geração foi conduzida de forma incremental e dirigida por esta
> especificação, que fixa *a priori* a estrutura da base, as regras de variação de
> cada bloco e o critério de verdade. O modelo redigiu os **100 projetos-base**
> (título, descrição, integrantes); os **500 registros derivados** foram produzidos por
> transformações determinísticas implementadas em
> [`scripts/generate_test_batch.py`](scripts/generate_test_batch.py).
> Ver [`README.md`](README.md) para o protocolo completo e a discussão sobre
> independência entre geração e avaliação.

## Objetivo

Criar uma base de dados sintética com **600 projetos de pesquisa brasileiros** para testar a acurácia do sistema de deduplicação. Os projetos simulam cadastros da plataforma Lattes/CNPq, com variações realistas entre duplicatas e casos desafiadores de não-duplicatas.

---

## Estrutura dos dados

Cada entrada segue o mesmo schema de `projects.json`:

```json
{
  "id": number,
  "titulo_projeto": string,
  "descricao_projeto": string,
  "lattes_ids": string,
  "nomes_integrante": string
}
```

Os 600 projetos estão organizados em **100 quíntuplas de duplicatas** + **100 não-duplicatas**:

| Bloco | IDs | Papel | Nível de variação |
|-------|-----|-------|-------------------|
| Base | 1–100 | Projeto original | — |
| 1ª duplicata | 101–200 | Duplicata próxima | Baixo (ruído superficial) |
| 2ª duplicata | 201–300 | Duplicata mais distante | Moderado (paráfrase) |
| 3ª duplicata | 301–400 | Duplicata sem descrição | Sutil no título, **descrição vazia** |
| 4ª duplicata | 401–500 | Duplicata com 1 autor | Similar à 1ª, **apenas 1 autor** |
| Não-duplicata | 501–600 | Projeto diferente, conteúdo similar | Conteúdo próximo ao base, **autores completamente diferentes** |

### Tuplas de duplicatas reais

```
(1, 101, 201, 301, 401)
(2, 102, 202, 302, 402)
...
(100, 200, 300, 400, 500)
```

### Não-duplicatas (tuplas de 1 elemento)

```
(501), (502), ..., (600)
```

Os registros 501–600 **não são duplicatas de ninguém**. Apesar de terem título e descrição semanticamente próximos aos projetos 1–100, seus autores são completamente distintos — representando diferentes grupos de pesquisa trabalhando em temas similares.

---

## Domínios dos 100 projetos base

| IDs | Domínio | Exemplos de temas |
|-----|---------|-------------------|
| 1–10 | Educação / Pedagogia / Extensão | PIBID, letramento digital, educação inclusiva, EJA |
| 11–20 | Biologia / Ecologia / Biodiversidade | Mata Atlântica, macroinvertebrados, parasitologia |
| 21–30 | Computação / IA / Sistemas | Machine learning em saúde, NLP, IoT, blockchain |
| 31–40 | Agronomia / Fitossanidade | Soja, café, viticultura, qualidade de sementes |
| 41–50 | Saúde / Medicina / Farmácia | Diabetes, dengue, AVC, resistência bacteriana |
| 51–60 | Ciências Sociais / Direito / Antropologia | Segregação urbana, indigenismo, MST, gênero |
| 61–70 | Engenharia (civil, elétrica, mecânica) | Concreto, fotovoltaica, tribologia, catálise |
| 71–80 | Letras / Linguística / Literatura | Literatura afro-brasileira, EJA, terminologia |
| 81–90 | Química / Física / Matemática | Compostos bioativos, nanomateriais, epidemiologia |
| 91–100 | Ciências Ambientais / Geologia | Pantanal, cerrado, ilha de calor, sedimentos |

---

## Tipo de variação por bloco

### 1ª duplicata (101–200) — ruído baixo

Simula um segundo cadastro do mesmo projeto com pequenas diferenças de digitação ou formatação.

- Título: maiúsculas/minúsculas, separador `" - "` → `": "`, ponto final adicionado
- Descrição: substituição de uma expressão por sinônimo próximo
  - ex.: `"tem como objetivo"` → `"tem por objetivo"`, `"Este projeto"` → `"O presente projeto"`
- Autores: normalização de maiúsculas (ex.: `"FERNANDA ROCHA"` → `"Fernanda Rocha"`)
- `lattes_ids`: ocasionalmente 1 dígito diferente (erro de digitação)

### 2ª duplicata (201–300) — ruído moderado

Simula um cadastro reescrito do mesmo projeto, como quando o coordenador reescreve para outro edital.

- Título: substituição de palavra-chave por sinônimo (`"Avaliação"` → `"Análise"`, `"Monitoramento"` → `"Vigilância"`)
- Descrição: múltiplas paráfrases + truncamento (remoção das 2 últimas frases ou da primeira)
- Autores: remoção ocasional do último autor ou inversão do formato (`"Ana Lima"` → `"LIMA, Ana"`)
- `lattes_ids`: variação ocasional de 2 dígitos finais

### 3ª duplicata (301–400) — sem descrição

Simula registro incompleto ou importação parcial de dados.

- Título: variação sutil com sufixo adicionado (ex.: `" - Relatório Final"`, `" - Fase 2"`, `" - Etapa II"`)
- Descrição: **campo vazio** (`""`)
- Autores: mesma lista com variação de formato (maiúsculas ou inversão sobrenome/nome)
- `lattes_ids`: igual ao original

### 4ª duplicata (401–500) — 1 autor

Simula cadastro feito apenas pelo coordenador principal do projeto.

- Título: variação sutil, mesmo nível da 1ª duplicata
- Descrição: variação sutil, mesmo nível da 1ª duplicata
- Autores: **apenas 1 autor** da lista original
- `lattes_ids`: igual ao original

### Não-duplicata (501–600) — conteúdo similar, autores completamente diferentes

Caso desafiador: projetos diferentes que tratam do mesmo tema com metodologia similar, mas de grupos de pesquisa distintos. O sistema **não deve** classificá-los como duplicatas dos projetos 1–100.

- Título: muito próximo ao base (mesma variação da 1ª duplicata)
- Descrição: similar ao base (mesma variação da 2ª duplicata — parafraseada)
- Autores: **pool completamente novo**, sem qualquer sobreposição com autores de 1–500
- `lattes_ids`: completamente diferentes

---

## Processo de geração incremental

### Fase 1 — Mapa de projetos (`cache/test_map.json`)

Arquivo leve com os metadados das 100 triplas: domínio, palavras-chave, autores pré-definidos e `lattes_id` base. Garante que **autores não se repitam entre tuplas diferentes**.

### Fase 2 — Geração em lotes (`cache/test_batch_NN.json`)

O script `scripts/generate_test_batch.py` opera em **20 lotes de 30 projetos** cada:

| Lotes | Bases cobertas | IDs gerados |
|-------|---------------|-------------|
| 01–10 | 1–100 | base + v1 + v2 → ids 1–300 |
| 11–20 | 1–100 | v3 + v4 + non-dup → ids 301–600 |

Cada lote é autocontido e pode ser regenerado independentemente.

### Fase 3 — Mesclagem (`cache/test.json`)

Os 20 lotes são combinados, ordenados por `id` e escritos em `test.json`:

```bash
python3 scripts/generate_test_batch.py --merge
```

---

## Uso do script gerador

```bash
# Ver status de todos os lotes (1-20)
python3 scripts/generate_test_batch.py --status

# Gerar um lote específico
# Lotes 1-10:  base + v1 + v2  (ids N, N+100, N+200)
# Lotes 11-20: v3 + v4 + non-dup (ids N+300, N+400, N+500)
python3 scripts/generate_test_batch.py --batch <1-20>

# Gerar todos os lotes de uma vez
for i in $(seq 1 20); do python3 scripts/generate_test_batch.py --batch $i; done

# Mesclar todos os lotes em cache/test.json
python3 scripts/generate_test_batch.py --merge
```

---

## Validações realizadas

| Verificação | Resultado |
|-------------|-----------|
| Total de projetos | 600 ✓ |
| IDs de 1 a 600 sem lacunas | ✓ |
| Nenhum ID duplicado | ✓ |
| Todos os campos presentes | ✓ |
| Bloco 301–400: descrição vazia | ✓ |
| Bloco 401–500: exatamente 1 autor por registro | ✓ |
| Bloco 501–600: zero sobreposição de autores com 1–100 | ✓ |
| Descrições únicas dentro de cada quintupla | ✓ |
| Títulos base únicos entre tuplas diferentes | ✓ |

---

## Critério de sucesso dos testes

O sistema de deduplicação deve identificar corretamente as quíntuplas `(N, N+100, N+200, N+300, N+400)` como referências ao mesmo projeto, e **não** sinalizar os registros 501–600 como duplicatas de nenhum outro.

| Par | Expectativa |
|-----|-------------|
| (N, N+100) | Duplicata identificada com **alta confiança** |
| (N, N+200) | Duplicata identificada com **confiança moderada a alta** |
| (N, N+300) | Duplicata identificada (sem descrição, apoio no título e autores) |
| (N, N+400) | Duplicata identificada (1 autor coincidente, título/descrição próximos) |
| (N, N+500) | **Não é duplicata** — conteúdo similar, autores completamente distintos |
| (N, M) onde N≠M e nenhum é +100/+200/+300/+400 do outro | **Não é duplicata** |
