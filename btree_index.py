from bisect import bisect_left, bisect_right
from typing import Any, List, Set

class BTreeIndex:
    def __init__(self):
        self.keys: List[Any] = []
        self.rows: List[Set[int]] = []

    def insert(self, key: Any, row_id: int):
        i = bisect_left(self.keys, key)
        if i < len(self.keys) and self.keys[i] == key:
            self.rows[i].add(row_id)
        else:
            self.keys.insert(i, key)
            self.rows.insert(i, {row_id})

    def remove(self, key: Any, row_id: int):
        i = bisect_left(self.keys, key)
        if i < len(self.keys) and self.keys[i] == key:
            s = self.rows[i]
            if row_id in s:
                s.remove(row_id)
                if not s:
                    del self.keys[i]
                    del self.rows[i]

    def update(self, old_key: Any, new_key: Any, row_id: int):
        if old_key == new_key:
            return
        self.remove(old_key, row_id)
        self.insert(new_key, row_id)

    def query(self, operator: str, value: Any) -> Set[int]:
        if operator == '=':
            i = bisect_left(self.keys, value)
            if i < len(self.keys) and self.keys[i] == value:
                return set(self.rows[i])
            return set()
        if operator == '!=':
            result: Set[int] = set()
            i = bisect_left(self.keys, value)
            for idx in range(0, i):
                result.update(self.rows[idx])
            for idx in range(i, len(self.keys)):
                if idx < len(self.keys) and self.keys[idx] == value:
                    continue
                result.update(self.rows[idx])
            return result
        if operator == '<':
            i = bisect_left(self.keys, value)
            result: Set[int] = set()
            for idx in range(0, i):
                result.update(self.rows[idx])
            return result
        if operator == '>':
            j = bisect_right(self.keys, value)
            result: Set[int] = set()
            for idx in range(j, len(self.keys)):
                result.update(self.rows[idx])
            return result
        if operator == '<=':
            j = bisect_right(self.keys, value)
            result: Set[int] = set()
            for idx in range(0, j):
                result.update(self.rows[idx])
            return result
        if operator == '>=':
            i = bisect_left(self.keys, value)
            result: Set[int] = set()
            for idx in range(i, len(self.keys)):
                result.update(self.rows[idx])
            return result
        return set()
