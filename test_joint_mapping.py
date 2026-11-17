import ast
from pathlib import Path

path = Path("rl_isaaclab/utils/misc.py")
tree = ast.parse(path.read_text(encoding="utf-8"))

names = {
    "_ISAACLAB2SHARPA_IDX",
    "_SHARPA2ISAACLAB_IDX"
}

mappings = {}

# 从真正的 Sharpa 源代码提取关节映射表
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                mappings[target.id] = ast.literal_eval(
                    node.value.args[0]
                )

forward = mappings["_ISAACLAB2SHARPA_IDX"]
backward = mappings["_SHARPA2ISAACLAB_IDX"]

# 构造22维关节测试向量
original = list(range(22))

# Isaac Lab -> Sharpa
converted = [original[i] for i in forward]

# Sharpa -> Isaac Lab
restored = [converted[i] for i in backward]

print("原始关节顺序:", original)
print("转换后的顺序:", converted)
print("恢复后的顺序:", restored)

assert sorted(forward) == list(range(22))
assert sorted(backward) == list(range(22))
assert restored == original

print("\nPASS：22维关节映射可逆！")