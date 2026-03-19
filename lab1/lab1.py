import random
import time
from collections import defaultdict
import threading
import json
from  queue import Queue

def generate_graph(vertices, edges):
    graph = defaultdict(list)
    for _ in range(edges):
        u = random.randint(0, vertices - 1)
        v = random.randint(0, vertices - 1)
        if u != v:
            graph[u].append(v)
            graph[v].append(u)
    return graph

def dfs(graph, v, visited, component):
    visited[v] = True
    component.append(v)
    for neighbor in graph[v]:
        if not visited[neighbor]:
            dfs(graph, neighbor, visited, component)

def find_connected_components(graph, vertices):
    visited = {v: False for v in graph}
    components = []

    for v in graph:
        if not visited[v]:
            component = []
            dfs(graph, v, visited, component)
            components.append(component)

    return components

def parallel_find_components(graph, num):
    visited = {v: False for v in graph}
    components = []   
    lock = threading.Lock()
    q = Queue()

    for v in graph:
        q.put(v)

    def worker():
        while True:
            try:
                v = q.get_nowait()
            except:
                return

            with lock:
                if visited[v]:
                    continue
                visited[v] = True

            component = []
            dfs(graph, v, visited, component)

            with lock:
                components.append(component)


    threads = []
    if num>len(graph):
        num=len(graph)
    for _ in range(num):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return components

if __name__ == "__main__":
    num=int(input("Скільки потоків ви хочете використати (1 - для значення за замовчуванням)"))
    graph = defaultdict(list)
    vertices = 4
    if  input("Зчитати ребра з файлу (y/n)? ") == "y":
        edges = []
        with open("edges.txt", "r") as f:
            for line in f:
                u, v = map(int, line.strip().split())
                edges.append((u, v))
        graph = defaultdict(list)
        for u,v in edges:
                graph[u].append(v)
                graph[v].append(u)
    else:
        if input("Ви хочете ввсети свій граф? (y/n) ") == "y":
            vertices = int(input("Скільки вершин графу? "))
            edges_count = int(input("Скільки ребер графу? "))
            for _ in range(edges_count):
                u, v = map(int, input("Введіть ребро (u v): ").split())
                graph[u].append(v)
                graph[v].append(u)
        else:
            graph = generate_graph(vertices, 3)
    with open("edges.txt","w") as file:
        for u in graph:
            for v in graph[u]:
                if u < v:
                    file.write(f"{u} {v}\n")

    print("Граф:", dict(graph))
    for k in graph:
        graph[k] = list(set(graph[k]))
    vertices = len(graph)
    start = time.time()
    components_seq = find_connected_components(graph, vertices)
    end = time.time()
    r = "\nПослідовні зв’язні компоненти:\n"
    print("\nПослідовні зв’язні компоненти:")
    for i, comp in enumerate(components_seq, 1):
        r += f"Компонента {i}: {comp}\n"
        print(f"Компонента {i}: {comp}")
    print("Час:", end - start)
    start = time.time()
    components_par = parallel_find_components(graph,num)
    end = time.time()
    r += "\nПаралельні зв’язні компоненти:\n"
    print("\nПаралельні зв’язні компоненти:")
    for i, comp in enumerate(components_par, 1):
        print(f"Компонента {i}: {comp}")
        r += f"Компонента {i}: {comp}\n"
    print("Час:", end - start)
    if input("Записати результат(y/n)")=="y":
        with open("result.txt","w") as file:
            file.write(r)
        print("Успішно записано")