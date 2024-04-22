# ЗАДАЧА 1 ТУТ ПРО ОЦЕНКИ
# n = int(input())
# m = list(map(int, input().split()))
# l = []
#
# start = 0
# end = 7
# counter_ud = 0
# counter_neg = 0
#
# for i in range(n):
#     if start + 7 <= n:
#         temp = m[start:end:1]
#         start += 1
#         end += 1
#
#         l.append(temp)
#
# more = 0
# temp = 0
#
# for i in l:
#     for j in i:
#         if j == 3 or j == 2:
#             l[l.index(i)] = []
#
# for i in l:
#     temp = i.count(5)
#
#     if temp >= more:
#         more = temp
#
# if more == 0:
#     more = -1
#
# print(more)
#
#
# ЗАДАЧА 2 ПЕРЕВЕРНУТЬ МАТРИЦУ
# n, m = map(int, input().split())
# matrix = [list(map(int, input().split())) for _ in range(n)]
#
# l = len(matrix)
# k = len(matrix[0])
# rotated = [[0] * l for _ in range(k)]
# for i in range(l):
#     for j in range(k):
#         rotated[j][l - i - 1] = matrix[i][j]
# for row in rotated:
#     print(*row)


# ЗАДАЧА 4 ПЕРЕВЕРНУТЬ МАТРИЦУ СЛОЖНЕЕ
# def swap_diagonal_elements():
#     n = len(matrix)
#     m = len(matrix[0])
#     for i in range(n):
#         j = i + 1
#         while j < n:
#             print(f'{i} {j} {j} {i}')
#             j += 1
#
#
# def swap_vert():
#     n = len(matrix)
#
#     for j in range(n // 2):
#         for i in range(n):
#             print(f'{i} {j} {i} {n - 1 - j}')
#
# def swap_horiz():
#     n = len(matrix)
#
#     for i in range(n // 2):
#         for j in range(n):
#             print(f'{i} {j} {n - 1 - i} {j}')
#
# n, m = map(str, input().split())
# n = int(n)
# matrix = [list(map(int, input().split())) for _ in range(int(n))]
# if n == 1:
#     print(0)
# else:
#     print(int(n * (n / 2) + (n * (n - 1)) / 2))
#     swap_diagonal_elements()
#
#     if m == 'R':
#         swap_vert()
#     else:
#         swap_horiz()


# n = int(input())
# m = [list(map(str, input().split('/'))) for _ in range(n)]
#
# print(m)

# ЗАДАЧА 3 ПРО ИЕРАРХИЮ ФАЙЛОВ
# class TreeNode:
#     def __init__(self, name):
#         self.name = name
#         self.children = {}
#
#
# def build_hierarchy(paths):
#     root_name = paths[0].split('/')[0]
#     root = TreeNode(root_name)
#     for path in paths:
#         folders = path.split('/')[1:]
#         current_node = root
#         for folder in folders:
#             if folder not in current_node.children:
#                 current_node.children[folder] = TreeNode(folder)
#             current_node = current_node.children[folder]
#
#     return root
#
#
# def print_hierarchy(node, indent=0):
#     print('  ' * indent + node.name)
#     for child in node.children.values():
#         print_hierarchy(child, indent + 1)
#
#
# n = int(input())
# m = []
#
# for _ in range(n):
#     line = input()
#     m.append(line)
#
# root_node = build_hierarchy(m)
# print_hierarchy(root_node)

# n = int(input())
#
# m = []
# for _ in range(n):
#     line = input().strip()[:3]
#     m.append(list(line))
#
# ЗАДАЧА 5 ПРО ЛЕСНИКА
# a = 0
# c = 1
# b = 2
#
# count_a_new = 0
# count_a_old = 0
# count_b_new = 0
# count_b_old = 0
# count_c = 0
#
# bool_a = True
# bool_b = True
# bool_c = True
#
# i = 0
#
# while i < n:
#     if m[i][a] == 'W' and m[i][b] == 'W' and m[i][c] == 'W':
#         break
#
#     if m[i][a] != 'W':
#         if count_c > count_a_old:
#             count_a_old = count_c
#             count_a_new = count_c
#         if m[i][a] == 'C':
#             count_a_new += 1
#
#     if m[i][b] != 'W':
#         if count_c > count_b_old:
#             count_b_old = count_c
#             count_b_new = count_c
#         if m[i][b] == 'C':
#             count_b_new += 1
#
#     if m[i][c] != 'W':
#         if count_a_old > count_c:
#             count_c = count_a_old
#         if count_b_old > count_c:
#             count_c = count_b_old
#         if m[i][c] == 'C':
#             count_c += 1
#
#     i += 1
#     count_b_old = count_b_new
#     count_a_old = count_a_new
#
# print(max(count_c, count_a_new, count_b_new))

# ЗАДАЧА 6 ПРО КОНЯ

from collections import deque

def is_valid(x, y, n):
    return 0 <= x < n and 0 <= y < n

def knight_moves(x, y, n):
    moves = [(-1, -2), (-2, -1), (-2, 1), (-1, 2),
             (1, -2), (2, -1), (2, 1), (1, 2)]
    possible_moves = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny, n):
            possible_moves.append((nx, ny))
    return possible_moves

def king_moves(x, y, n):
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (-1, 1), (1, -1), (-1, -1)]
    possible_moves = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny, n):
            possible_moves.append((nx, ny))
    return possible_moves

def shortest_path(board, n, start_x, start_y, end_x, end_y):
    visited = set()
    queue = deque([(start_x, start_y, 0, 'K', [])])

    while queue:
        x, y, steps, figure, path = queue.popleft()

        if (x, y, figure) in visited:
            continue

        visited.add((x, y, figure))

        if (x, y) == (end_x, end_y):
            path.append((x, y))
            return steps, path

        if figure == 'K':
            moves = knight_moves(x, y, n)
        else:
            moves = king_moves(x, y, n)

        for nx, ny in moves:
            if board[nx][ny] == 'K':
                queue.append((nx, ny, steps + 1, 'K', path + [(x, y)]))
            elif board[nx][ny] == 'G':
                queue.append((nx, ny, steps + 1, 'G', path + [(x, y)]))
            else:
                queue.append((nx, ny, steps + 1, figure, path + [(x, y)]))

    return -1, []

n = int(input())
board = [list(input()) for _ in range(n)]

start_x, start_y = None, None
end_x, end_y = None, None
for i in range(n):
    for j in range(n):
        if board[i][j] == 'S':
            start_x, start_y = i, j
        elif board[i][j] == 'F':
            end_x, end_y = i, j

steps, path = shortest_path(board, n, start_x, start_y, end_x, end_y)
if steps == -1:
    print(steps)
else:
    print(steps)
    print("Путь:")
    for x, y in path:
        print(x, y)

