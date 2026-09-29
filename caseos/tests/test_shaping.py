"""Framing & Shaping: the structured document (problem, storyline guide, research plan) built from proposals Hugo
approves, the move of a storyline out of the brief, research tasks launched with their agent, and the guide reaching
the Story Package and the Visual Storyteller."""
import pytest

from caseos import briefing, config, research, shaping, story, storyteller


def test_proposals_wait_for_hugo_and_approved_content_is_his(case):
    assert shaping.propose(case, "problem", {"statement": "Separar lo afirmable de lo posible ante el CFO.",
                                             "out_of_scope": ["Atribuir ventas al gasto de marketing"]})
    assert shaping.propose(case, "guion:S1", {"title": "Overview", "slides": [{"title": "Clientes vs ingreso", "question": "¿Qué pasó?"}]})
    assert shaping.propose(case, "plan:RT-001", {"question": "¿Cambió el ticket de entrada?", "kind": "data"})
    st = shaping.state(case)
    assert st["problem"]["approved"] is None and st["pending"] == 3                      # nothing approved by an agent
    with pytest.raises(ValueError):
        shaping.approve(case, "problem", actor="framer")
    shaping.approve(case, "problem")
    shaping.approve_all(case)
    fr = case.read_data("framing/current.yaml")
    assert fr["problem"]["out_of_scope"] == ["Atribuir ventas al gasto de marketing"]
    assert fr["storyline_guide"][0]["slides"][0]["id"] == "S1.1"
    assert fr["research_plan"][0] == {**fr["research_plan"][0], "kind": "data", "agent": "analytics", "intensity": "analytics", "status": "approved"}
    assert "Separar lo afirmable" in case.read_text("framing/current.md")


def test_revision_of_an_approved_section_does_not_overwrite_it(case):
    shaping.set_section(case, "guion:new", {"title": "Growth", "slides": [{"title": "Entradas por segmento"}]})
    assert not shaping.propose(case, "guion:S1", {"title": "Growth", "slides": [{"title": "Entradas por segmento"}]})  # nothing new
    assert shaping.propose(case, "guion:S1", {"title": "Growth", "slides": [{"title": "Entradas por segmento"}, {"title": "Funnel no lineal"}]})
    fr = case.read_data("framing/current.yaml")
    assert len(fr["storyline_guide"][0]["slides"]) == 1 and fr["pending"]["guion:S1"]["revises"]
    shaping.discard(case, "guion:S1")
    assert "guion:S1" not in case.read_data("framing/current.yaml")["pending"]


def test_an_approved_task_launches_with_its_agent(case, monkeypatch):
    monkeypatch.setattr(config, "AUTO_COS", False)
    h = case.create("hypothesis", {"statement": "La calidad de los leads bajó", "falsifier": "…", "status": "open"}, actor="framer")
    shaping.set_section(case, "plan:new", {"question": "¿Qué eventos mínimos medirían el funnel no lineal?", "kind": "measurement",
                                           "intensity": "L2", "links": [h["id"]], "slides": ["S2.3"]})
    launched = []
    monkeypatch.setattr(research, "launch_job", lambda store, rid: launched.append(rid) or type("J", (), {"id": "JOB-x"})())
    out = shaping.send_task(case, "RT-001")
    r = case.get(out["research_id"])
    assert (r["specialty"], r["intensity"], r["route"]["source"]) == ("measurement", "L2", "hugo")
    assert h["id"] in r["links"] and r["shaping_task"] == "RT-001" and r["slides"] == ["S2.3"] and launched
    task = case.read_data("framing/current.yaml")["research_plan"][0]
    assert task["status"] == "sent" and task["research_id"] == r["id"]
    with pytest.raises(ValueError):
        shaping.remove(case, "plan:RT-001")                                                    # already in Research


STRUCTURE = ["Presentación ejecutiva ≤ 5 min", "Material de soporte · 1 Overview — observaciones generales del negocio.",
             "Material de soporte · 2 Growth — L1: las relaciones que comentó Hugo. L2: cómo definir y medir el funnel si no todos lo recorren igual (self-serve).",
             "Nota corta"]


def test_storyline_moves_out_of_the_brief_as_proposals(case):
    briefing.set_section(case, "deliverables", STRUCTURE)
    fr = case.read_data("framing/current.yaml")
    fr["research_needed"] = [{"id": "RN-1", "question": "¿Qué eventos y métricas necesitamos para medir el funnel?", "status": "pending",
                              "links": [], "why": "Caso CRO"}]
    case.write_data("framing/current.yaml", fr)
    made = shaping.migrate(case)
    assert made["guion"] == ["S1", "S2"] and made["plan"] == ["RT-001"] and made["deliverables"]
    fr = case.read_data("framing/current.yaml")
    growth = fr["pending"]["guion:S2"]["value"]
    assert [s["id"] for s in growth["slides"]] == ["S2.1", "S2.2"]
    assert growth["slides"][1]["question"].startswith("¿Cómo definir y medir el funnel")
    assert fr["pending"]["plan:RT-001"]["value"]["kind"] == "measurement"
    b = briefing.get(case)
    assert len(b["deliverables"]) == 4                                                          # approved brief untouched
    assert not any("L1:" in d for d in b["pending"]["deliverables"]["value"])                  # the clean version waits for Hugo
    assert shaping.migrate(case) == {"guion": [], "plan": [], "deliverables": True}            # idempotent on the guion/plan


def test_guide_reaches_story_package_and_storyteller(case):
    from tests.test_handoffs import _accepted_evidence, _package
    shaping.set_section(case, "guion:new", {"title": "Overview", "slides": [{"title": "Entradas vs monto", "question": "¿Qué pasó?"},
                                                                            {"title": "Precio vs descuento", "question": "¿Se puede separar?"}]})
    f, t = _accepted_evidence(case)
    pkg = _package(f, t, key="entry")
    pkg["guion_map"] = [{"slide_id": "S1.1", "claim_keys": ["entry"], "coverage": "covered", "note": ""},
                        {"slide_id": "S1.2", "claim_keys": [], "coverage": "missing", "note": "sin datos de precio"}]
    res = story.apply_package(case, pkg, actor="cos")
    saved = case.read_data("story/package.yaml")
    assert saved["guion_map"][0]["claim_ids"] == res["claims"]
    assert any("S1.2" in w for w in res["warnings"])                                           # a missing slide is visible, not filled
    md = "\n".join(storyteller.guion_block(case, saved))
    assert "S1.1 Entradas vs monto" in md and "missing" in md and res["claims"][0] in md


def test_ids_are_never_reused(case):
    shaping.propose(case, "plan:RT-001", {"question": "¿Cambió el ticket de entrada?", "kind": "data"})
    shaping.discard(case, "plan:RT-001")
    shaping.set_section(case, "plan:new", {"question": "¿Qué descuentos usan otras SaaS B2B?", "kind": "research"})
    shaping.set_section(case, "guion:new", {"title": "Overview", "slides": [{"title": "Entradas vs monto"}]})
    shaping.remove(case, "guion:S1")
    shaping.set_section(case, "guion:new", {"title": "Growth", "slides": [{"title": "Funnel"}]})
    fr = case.read_data("framing/current.yaml")
    assert [t["id"] for t in fr["research_plan"]] == ["RT-002"]                        # RT-001 meant something else
    assert [s["id"] for s in fr["storyline_guide"]] == ["S2"]
