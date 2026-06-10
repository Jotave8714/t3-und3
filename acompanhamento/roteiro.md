# Ficha de Acompanhamento — Waif Until Dark

- **Link:** <https://open.kattis.com/problems/waif>
- **Resolução completa:** [../src/main.py](../src/main.py) · detalhes em [../README.md](../README.md)

## 1. Resumo do problema (em linguagem própria)

Uma creche tem um conjunto de crianças e um conjunto de brinquedos. Cada criança
só aceita brincar com alguns brinquedos específicos. Um brinquedo só pode ser
dado a uma criança, e cada criança fica satisfeita com no máximo um brinquedo.

Há ainda uma regra de grupo: certos brinquedos são agrupados em **categorias**,
e de cada categoria no máximo `r` brinquedos podem ser usados ao mesmo tempo
(ex.: "no máximo 2 brinquedos barulhentos ao mesmo tempo"). Brinquedos fora de
qualquer categoria não têm esse limite.

**Pergunta:** qual o maior número de crianças que dá para deixar satisfeitas
simultaneamente, respeitando todas as restrições?

É um **emparelhamento bipartido** (criança ↔ brinquedo) com um limite extra por
categoria — resolvido como **fluxo máximo**.

## 2. Interpretação da entrada e da saída

### Entrada (lida de `stdin`)

```
n m p
<para cada criança j = 1..n>  k  b1 b2 ... bk
<para cada categoria j = 1..p> l  t1 t2 ... tl  r
```

- Linha 1: `n` crianças, `m` brinquedos, `p` categorias.
- `n` blocos de criança: `k` = quantos brinquedos ela aceita, seguido dos `k`
  índices de brinquedo.
- `p` blocos de categoria: `l` = quantos brinquedos na categoria, os `l` índices,
  e por fim `r` = limite de uso da categoria.
- Brinquedo que não aparece em nenhuma categoria é "livre" (sem limite de grupo).

O parser lê todos os tokens de uma vez ([../src/main.py:146](../src/main.py#L146))
e consome com `nxt()`, então quebras de linha não importam.

### Saída (escrita em `stdout`)

Um único inteiro: o **número máximo de crianças satisfeitas**
([../src/main.py:192](../src/main.py#L192)).

## 3. Modelagem da rede de fluxo

Grafo dirigido com origem `S` e sorvedouro `T`:

```
S --(1)--> criança --(1)--> brinquedo aceito
                                  |
              (com categoria) --(1)--> categoria --(r)--> T
              (sem categoria) --------------(1)----------> T
```

| Aresta | Cap. | Por quê |
| --- | --- | --- |
| `S → criança` | 1 | cada criança satisfeita no máximo uma vez |
| `criança → brinquedo` | 1 | só liga brinquedos que a criança aceita |
| `brinquedo → categoria` | 1 | cada brinquedo usado no máximo uma vez |
| `categoria → T` | `r` | **único** ponto que aplica o limite agregado |
| `brinquedo sem categoria → T` | 1 | vai direto ao sorvedouro, sem limite de grupo |

Numeração dos vértices: `S=0`, crianças `1..n`, brinquedos `n+1..n+m`,
categorias `n+m+1..n+m+p`, `T = n+m+p+1`
([../src/main.py:159](../src/main.py#L159)).

Cada unidade de fluxo `S → criança → brinquedo → … → T` representa **uma criança
satisfeita por um brinquedo válido**. Logo o **valor do fluxo máximo é a
resposta**.

## 4. Ford-Fulkerson vs. Edmonds-Karp — justificativa

| | Ford-Fulkerson (DFS) | Edmonds-Karp (BFS) — **escolhido** |
| --- | --- | --- |
| Busca do caminho aumentante | DFS (caminho qualquer) | BFS (caminho mais curto em nº de arestas) |
| Complexidade | depende das capacidades; pode degenerar | `O(V·E²)`, independente das capacidades |
| Previsibilidade | caminhos ruins podem alongar a convergência | sempre escolhe o caminho mais curto primeiro |

**Decisão:** Edmonds-Karp. Embora aqui as capacidades sejam pequenas (1 ou `r`)
e o FF puro também terminasse rápido, a BFS dá um **limite de tempo garantido
`O(V·E²)`** e evita os caminhos aumentantes longos que a DFS poderia escolher.
Custo a mais de implementação é mínimo (trocar a busca por uma fila), então
ganha-se previsibilidade sem perda prática. Implementado em
[../src/main.py:93](../src/main.py#L93) (`_has_augmenting_path` usa `deque`).

## 5. Instância pequena

Arquivo [../dados/entradas_do_problema.txt](../dados/entradas_do_problema.txt):

```
4 3 1
2 1 2
2 1 2
1 3
1 3
2 1 2 1
```

Interpretação:

- `n=4` crianças, `m=3` brinquedos, `p=1` categoria.
- Criança 1 aceita brinquedos {1, 2}.
- Criança 2 aceita brinquedos {1, 2}.
- Criança 3 aceita brinquedo {3}.
- Criança 4 aceita brinquedo {3}.
- Categoria 1 = {brinquedos 1, 2}, limite `r = 1`.
- Brinquedo 3 não está em categoria nenhuma (livre).

Rede resultante:

```
S → c1, c2, c3, c4              (cap 1 cada)
c1 → t1, t2     c2 → t1, t2     c3 → t3     c4 → t3   (cap 1)
t1 → cat1       t2 → cat1       (cap 1)
cat1 → T        (cap 1)         t3 → T      (cap 1)
```

## 6. Execução manual passo a passo (Edmonds-Karp)

BFS sempre pega o caminho aumentante mais curto disponível. Gargalo = menor
capacidade residual no caminho.

**Iteração 1**
Caminho: `S → c1 → t1 → cat1 → T`. Capacidades 1,1,1,1 → gargalo **1**.
Empurra 1. Saturadas: `S→c1`, `t1→cat1`, `cat1→T`. **Fluxo total = 1**.

**Iteração 2**
Caminho: `S → c3 → t3 → T`. Capacidades 1,1,1 → gargalo **1**.
Empurra 1. Saturadas: `S→c3`, `t3→T`. **Fluxo total = 2**.

**Iteração 3 (busca falha)**
Sobram crianças c2 e c4. Tentativas:
- `S → c2 → t1/t2 → cat1 → T`: chega em `cat1`, mas `cat1 → T` já está
  **saturada** (`r = 1`). Sem residual.
- `S → c4 → t3 → T`: `t3 → T` já está **saturada**. Sem residual.

Nenhuma aresta reversa ajuda (trocar c1↔c2 ou c3↔c4 não cria capacidade nova nos
gargalos `cat1→T` e `t3→T`). **Não há caminho aumentante → BFS de `T` falha.**

Algoritmo para. **Fluxo máximo = 2.**

## 7. Verificação da resposta final

Pareamento ótimo encontrado:

| Criança | Brinquedo | Observação |
| --- | --- | --- |
| c1 | t1 | usa a única vaga da categoria 1 (`r=1`) |
| c3 | t3 | brinquedo livre |
| c2 | — | bloqueada: categoria 1 esgotada |
| c4 | — | bloqueada: `t3` já usado |

**É ótimo?** Sim:
- Crianças 1 e 2 só aceitam t1/t2, ambos na categoria 1 com `r=1` → no máximo
  **1** delas satisfeita.
- Crianças 3 e 4 só aceitam t3, e `t3` serve **1** criança → no máximo **1**.
- Teto teórico = 1 + 1 = **2**, que o fluxo atinge. ✔

Confirmação por execução real:

```bash
cd src
python3 main.py < ../dados/entradas_do_problema.txt
# saída: 2
```

A saída `2` bate com o passo a passo manual e com o limite teórico. ✔

![Waif Until Dark](GvDDSPmNMoGsiHDR.png)
