import os
import struct
from typing import Any, Dict, List, Tuple

TYPE_CODES = {"INT": 1, "VARCHAR": 2, "BOOLEAN": 3}
REVERSE_TYPES = {1: "INT", 2: "VARCHAR", 3: "BOOLEAN"}

class BinaryStorage:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}.bin")

    def save_table(self, table) -> None:
        path = self._path(table.name)
        header = b"TOPQLBIN" + struct.pack("B", 1)
        cols = table.columns
        rows = table.rows
        payload = bytearray()
        payload.extend(struct.pack("I", len(cols)))
        for col in cols:
            name_bytes = col["name"].encode("utf-8")
            payload.extend(struct.pack("H", len(name_bytes)))
            payload.extend(name_bytes)
            payload.extend(struct.pack("B", TYPE_CODES[col["type"]]))
        payload.extend(struct.pack("I", len(rows)))
        for row in rows:
            for col in cols:
                t = col["type"]
                val = row[col["name"]]
                if t == "INT":
                    payload.extend(struct.pack("q", int(val)))
                elif t == "BOOLEAN":
                    payload.extend(struct.pack("B", 1 if bool(val) else 0))
                elif t == "VARCHAR":
                    b = str(val).encode("utf-8")
                    payload.extend(struct.pack("I", len(b)))
                    payload.extend(b)
        with open(path, "wb") as f:
            f.write(header)
            f.write(payload)

    def load_table(self, table_name: str) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        path = self._path(table_name)
        with open(path, "rb") as f:
            magic = f.read(8)
            version = f.read(1)
            if magic != b"TOPQLBIN":
                raise ValueError("Invalid binary format")
            col_count = struct.unpack("I", f.read(4))[0]
            columns: List[Dict[str, str]] = []
            for _ in range(col_count):
                name_len = struct.unpack("H", f.read(2))[0]
                name = f.read(name_len).decode("utf-8")
                type_code = struct.unpack("B", f.read(1))[0]
                columns.append({"name": name, "type": REVERSE_TYPES[type_code]})
            row_count = struct.unpack("I", f.read(4))[0]
            rows: List[Dict[str, Any]] = []
            for _ in range(row_count):
                row: Dict[str, Any] = {}
                for col in columns:
                    t = col["type"]
                    if t == "INT":
                        val = struct.unpack("q", f.read(8))[0]
                    elif t == "BOOLEAN":
                        val = struct.unpack("B", f.read(1))[0] == 1
                    elif t == "VARCHAR":
                        l = struct.unpack("I", f.read(4))[0]
                        val = f.read(l).decode("utf-8")
                    row[col["name"]] = val
                rows.append(row)
        return columns, rows
