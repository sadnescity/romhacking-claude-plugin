import roles
import romhack_state


def test_the_director_knows_every_phase():
    text = roles.skill_text("romhacking")
    for phase in romhack_state.PHASES:
        assert phase in text, f"the director does not name the phase {phase}"


def test_the_director_refuses_to_skip_ahead():
    text = roles.skill_text("romhacking").lower()
    assert "refuse" in text or "do not" in text, \
        "missing the explicit instruction to refuse skipping ahead to translation"
    assert "romhack.md" in text


def test_the_director_orders_the_phases_as_the_flow_does():
    """Order is measured in the phase table, not the whole document: the
    frontmatter description names 'translation' much earlier."""
    text = roles.skill_text("romhacking")
    section = text.split("## The seven phases", 1)[1].split("## Routing", 1)[0]
    positions = [section.index(p) for p in romhack_state.PHASES]
    assert positions == sorted(positions), \
        "the phases appear in a different order from the flow"


def test_the_director_routes_every_phase():
    """Every phase must have a row in the routing table."""
    text = roles.skill_text("romhacking")
    routing = text.split("## Routing", 1)[1].split("## The refusal rule", 1)[0]
    missing = [p for p in romhack_state.PHASES if p not in routing]
    assert not missing, f"phases without routing: {missing}"
