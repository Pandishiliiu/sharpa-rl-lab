"""Load selected functions from project source without importing hardware SDKs."""

from __future__ import annotations

import ast
import copy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "rl_isaaclab").is_dir() and (ROOT / "code/rl_isaaclab").is_dir():
    ROOT = ROOT / "code"
ENV_SOURCE = ROOT / "rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env.py"
DEPLOY_SOURCE = ROOT / "rl_isaaclab/scripts/deploy.py"


class _StripAnnotations(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node = self.generic_visit(node)
        node.returns = None
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            arg.annotation = None
        if node.args.vararg:
            node.args.vararg.annotation = None
        if node.args.kwarg:
            node.args.kwarg.annotation = None
        node.decorator_list = []
        return node


def _compile_function(node, globals_dict):
    function_node = _StripAnnotations().visit(copy.deepcopy(node))
    module = ast.fix_missing_locations(ast.Module(body=[function_node], type_ignores=[]))
    namespace = dict(globals_dict)
    exec(compile(module, "<offline-method>", "exec"), namespace)
    return namespace[function_node.name]


def load_env_method(name, **globals_dict):
    tree = ast.parse(ENV_SOURCE.read_text(encoding="utf-8"))
    cls = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "SharpaWaveInhandRotateDeployEnv"
    )
    method = next(
        node
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )
    return _compile_function(method, globals_dict)


def load_deploy_function(name, **globals_dict):
    tree = ast.parse(DEPLOY_SOURCE.read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )
    return _compile_function(function, globals_dict)
