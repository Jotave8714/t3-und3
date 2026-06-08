"""
Kattis - Waif Until Dark   (https://open.kattis.com/problems/waif)

Arquivo unico e autocontido para submissao no Kattis. Reune a logica de fluxo
maximo (FlowEdge, FlowNetwork, FordFulkerson) implementada pelo grupo, seguindo
a estrutura conceitual do algs4-py. Sem bibliotecas externas (apenas stdlib).

Modelagem como rede de fluxo (emparelhamento bipartido com restricoes de
categoria modeladas por uma camada intermediaria de capacidade):

  origem S
    --(cap 1)--> cada CRIANCA          (cada crianca satisfaz no maximo 1)
  cada CRIANCA
    --(cap 1)--> cada BRINQUEDO que ela aceita   (compatibilidade)
  cada BRINQUEDO de categoria c
    --(cap 1)--> no da CATEGORIA c      (cada brinquedo usado no maximo 1 vez)
  no da CATEGORIA c
    --(cap r)--> sorvedouro T           (no maximo r brinquedos da categoria)
  cada BRINQUEDO sem categoria
    --(cap 1)--> sorvedouro T           (sem limite de categoria)

Uma unidade de fluxo de S a T = uma crianca satisfeita com um brinquedo que ela
gosta. O fluxo maximo e o numero maximo de criancas satisfeitas.
"""

import sys
from collections import deque


class FlowEdge:
    """
    Aresta de rede de fluxo. A mesma instancia e compartilhada pelos dois
    vertices, servindo ao mesmo tempo como aresta direta e reversa no residual:
      - residual no sentido v -> w : capacity - flow  (direta)
      - residual no sentido w -> v : flow             (reversa)
    """

    def __init__(self, v, w, capacity):
        self._v = v
        self._w = w
        self._capacity = capacity
        self._flow = 0

    def from_vertex(self):
        return self._v

    def to_vertex(self):
        return self._w

    def other(self, vertex):
        if vertex == self._v:
            return self._w
        if vertex == self._w:
            return self._v
        raise ValueError("vertice invalido na aresta")

    def residual_capacity_to(self, vertex):
        if vertex == self._v:        # sentido reverso (w -> v)
            return self._flow
        if vertex == self._w:        # sentido direto (v -> w)
            return self._capacity - self._flow
        raise ValueError("vertice invalido na aresta")

    def add_residual_flow_to(self, vertex, delta):
        if vertex == self._v:        # reverso: devolve fluxo
            self._flow -= delta
        elif vertex == self._w:      # direto: adiciona fluxo
            self._flow += delta
        else:
            raise ValueError("vertice invalido na aresta")


class FlowNetwork:
    """Rede de fluxo como lista de adjacencia."""

    def __init__(self, V):
        self._V = V
        self._adj = [[] for _ in range(V)]

    def V(self):
        return self._V

    def add_edge(self, e):
        v = e.from_vertex()
        w = e.to_vertex()
        self._adj[v].append(e)   # direta a partir de v
        self._adj[w].append(e)   # mesma aresta vista como reversa a partir de w

    def adj(self, v):
        return self._adj[v]


class FordFulkerson:
    """
    Fluxo maximo por Ford-Fulkerson na variante Edmonds-Karp (caminho
    aumentante por BFS). BFS garante O(V * E^2) e e mais previsivel que DFS.
    """

    def __init__(self, G, s, t):
        self._value = 0
        self._marked = None
        self._edge_to = None

        while self._has_augmenting_path(G, s, t):
            # gargalo = menor capacidade residual ao longo do caminho
            bottle = float("inf")
            v = t
            while v != s:
                bottle = min(bottle, self._edge_to[v].residual_capacity_to(v))
                v = self._edge_to[v].other(v)

            # empurra o gargalo, atualizando diretas e reversas
            v = t
            while v != s:
                self._edge_to[v].add_residual_flow_to(v, bottle)
                v = self._edge_to[v].other(v)

            self._value += bottle

    def _has_augmenting_path(self, G, s, t):
        self._edge_to = [None] * G.V()
        self._marked = [False] * G.V()

        queue = deque([s])
        self._marked[s] = True
        while queue:
            v = queue.popleft()
            for e in G.adj(v):
                w = e.other(v)
                if e.residual_capacity_to(w) > 0 and not self._marked[w]:
                    self._edge_to[w] = e
                    self._marked[w] = True
                    queue.append(w)

        return self._marked[t]

    def value(self):
        return self._value

    def in_cut(self, v):
        """True se v esta no lado da origem do corte minimo."""
        return self._marked[v]


def main():
    data = sys.stdin.buffer.read().split()
    idx = 0

    def nxt():
        nonlocal idx
        val = int(data[idx])
        idx += 1
        return val

    n = nxt()   # criancas
    m = nxt()   # brinquedos
    p = nxt()   # categorias

    S = 0
    child = lambda j: j                 # 1..n
    toy = lambda i: n + i               # n+1..n+m
    category = lambda j: n + m + j      # n+m+1..n+m+p
    T = n + m + p + 1
    V = T + 1

    G = FlowNetwork(V)

    # S -> crianca (cap 1) e crianca -> brinquedos aceitos (cap 1)
    for j in range(1, n + 1):
        G.add_edge(FlowEdge(S, child(j), 1))
        k = nxt()
        for _ in range(k):
            i = nxt()
            G.add_edge(FlowEdge(child(j), toy(i), 1))

    # categorias: brinquedo -> categoria (cap 1), categoria -> T (cap r)
    toy_has_category = [False] * (m + 1)
    for j in range(1, p + 1):
        l = nxt()
        toys_in_cat = [nxt() for _ in range(l)]
        r = nxt()
        for i in toys_in_cat:
            toy_has_category[i] = True
            G.add_edge(FlowEdge(toy(i), category(j), 1))
        G.add_edge(FlowEdge(category(j), T, r))

    # brinquedos sem categoria -> T (cap 1)
    for i in range(1, m + 1):
        if not toy_has_category[i]:
            G.add_edge(FlowEdge(toy(i), T, 1))

    print(FordFulkerson(G, S, T).value())


if __name__ == "__main__":
    main()
