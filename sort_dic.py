x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
c = {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=True)}

print(c)