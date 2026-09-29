"""Every structured output an agent must return is a valid, strict JSON schema: an invalid one (a key required twice, a
required key with no definition) makes the CLI refuse the run before it starts — on 29-sep that broke every Framer turn."""
import jsonschema

from caseos import commands, cos, research, story
from caseos.agents import briefer, framer, planner


def _walk(schema, path="$"):
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            req, props = schema.get("required") or [], schema.get("properties") or {}
            yield path, req, props, schema.get("additionalProperties")
        for k, v in schema.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(schema, list):
        for i, v in enumerate(schema):
            yield from _walk(v, f"{path}[{i}]")


def test_every_agent_schema_is_strict_and_well_formed():
    schemas = {"framer": framer.SCHEMA, "planner": planner.SCHEMA, "briefer": briefer.SCHEMA, "story": story.SCHEMA,
               "router": research.ROUTE_SCHEMA, "cos_ask": cos.ASK_SCHEMA, "cos_impact": cos.IMPACT_SCHEMA,
               "classify": commands.CLASSIFY_SCHEMA, "dossier": research.DOSSIER, "peer": research.PEER,
               **{f"research:{k}": research.result_schema(k) for k in ("business", "measurement", "data_engineering")}}
    problems = []
    for name, sch in schemas.items():
        try:
            jsonschema.Draft202012Validator.check_schema(sch)
        except jsonschema.SchemaError as e:
            problems.append(f"{name}: esquema inválido — {e.message}")
        for path, req, props, extra in _walk(sch):
            if len(req) != len(set(req)):
                problems.append(f"{name} {path}: required repetido {sorted(k for k in set(req) if req.count(k) > 1)}")
            missing = [k for k in req if k not in props]
            if missing:
                problems.append(f"{name} {path}: required sin definir {missing}")
            if extra is not False:
                problems.append(f"{name} {path}: additionalProperties debe ser false")
    assert problems == []
