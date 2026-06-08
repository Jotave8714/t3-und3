# Apresentação — Waif Until Dark (≤ 5 min)

## 1. Contexto e objetivo (1 min)

Creche com `n` crianças e `m` brinquedos. Cada criança aceita só alguns
brinquedos; cada brinquedo serve 1 criança. Categorias limitam a `r` brinquedos
usados por categoria. **Objetivo: maximizar crianças satisfeitas.**
É emparelhamento bipartido + restrição de categoria → **fluxo máximo**.

## 2. Modelagem da rede (1 min)

`S → crianças → brinquedos → categorias → T`

- **`S` (origem):** estoque de crianças; 1 unidade por criança → nenhuma é
  contada duas vezes.
- **`T` (sorvedouro):** chegar = uma criança satisfeita validamente.
- **Capacidades:**
  - `S → criança`: **1** (criança satisfeita 1 vez).
  - `criança → brinquedo aceito`: **1** (compatibilidade).
  - `brinquedo → categoria`: **1** (brinquedo usado 1 vez).
  - `categoria → T`: **r** (limite agregado da categoria — único gargalo da
    categoria).
  - `brinquedo sem categoria → T`: **1** (livre).

Uma unidade de fluxo `S→…→T` = um par (criança, brinquedo) válido.

## 3. Estratégia algorítmica (1 min)

**Ford-Fulkerson / Edmonds-Karp (BFS).**
- Caminho aumentante por **BFS** (mais curto) → `O(V·E²)`, previsível.
- **Grafo residual:** cada aresta guarda `capacity − flow` (direto) e `flow`
  (reverso). A **aresta reversa** permite desfazer um pareamento e liberar
  solução melhor.
- **Gargalo** = menor capacidade residual no caminho; empurra-se esse valor.
- **Parada:** não existe mais caminho de `S` a `T` no residual.

## 4. Do fluxo para a resposta (1 min)

**Valor do fluxo máximo = número máximo de crianças satisfeitas.**
O pareamento sairia das arestas `criança → brinquedo` com `flow > 0`.
Max-flow = min-cut: o gargalo da rede é exatamente a resposta ótima.

Exemplo (Sample): `4 3 1` com categoria `{1,2}` e `r=1` → resposta **2**
(1 criança via categoria + 1 via brinquedo livre `3`).

## 5. Complexidade e casos especiais (1 min)

- `V = n+m+p+2`, `E = O(n·m)`. Tempo `O(V·E²)`; com `n,m ≤ 100`, trivial.
- Memória: lista de arestas residuais, `O(E)`.
- Casos: `p=0` (sem categorias), `r=0` (categoria bloqueada), brinquedo que
  ninguém quer, disputa pelo mesmo brinquedo, correção via aresta reversa.
