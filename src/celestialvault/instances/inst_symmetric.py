class SymmetricMap:
    def __init__(self):
        self.pairs = {}    # a -> b
        self.reverse = {}  # b -> a

    def __setitem__(self, a, b):
        # 如果 a 或 b 已经存在于映射中，先删除原映射
        if a in self:
            self.__delitem__(a)
        if b in self:
            self.__delitem__(b)
        self.pairs[a] = b
        self.reverse[b] = a

    def __getitem__(self, x):
        if x in self.pairs:
            return self.pairs[x]
        elif x in self.reverse:
            return self.reverse[x]
        else:
            raise KeyError(f"{x} not found")

    def __delitem__(self, x):
        y = self[x]  # uses __getitem__
        if x in self.pairs:
            del self.pairs[x]
            del self.reverse[y]
        else:
            del self.reverse[x]
            del self.pairs[y]

    def __contains__(self, x):
        return x in self.pairs or x in self.reverse

    def __len__(self):
        return len(self.pairs)

    def __repr__(self):
        items = []
        visited = set()
        for a, b in self.pairs.items():
            if a not in visited and b not in visited:
                items.append(f"{repr(a)} <-> {repr(b)}")
                visited.add(a)
                visited.add(b)
        return f"SymmetricMap({', '.join(items)})"
