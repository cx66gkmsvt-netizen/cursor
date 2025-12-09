"""
Prototype orchestration script for a controlled, multi-model speech-drafting
workflow tailored to government scenarios. This is a **logic skeleton** rather
than a production-ready system; it shows how to structure roles, checkpoints,
and debate/synthesis cycles while keeping a human in the loop.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional


# ----- Data models -----


class Role(Enum):
    POLICY_EXPERT = auto()
    DATA_ADVISOR = auto()
    LOGIC_ARCHITECT = auto()
    STYLIST = auto()
    RISK_REVIEWER = auto()


@dataclass
class UploadedSource:
    name: str
    content: str
    kind: str  # e.g., "policy", "data", "briefing"


@dataclass
class SpeechRequest:
    occasion: str
    audience: str
    keywords: List[str]
    tone: str
    duration_minutes: int
    must_quote: List[str] = field(default_factory=list)
    forbidden_terms: List[str] = field(default_factory=list)
    references: List[UploadedSource] = field(default_factory=list)


@dataclass
class Draft:
    text: str
    rationale: Dict[Role, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)  # e.g., speaker notes


# ----- Model plumbing (stubs) -----


ModelFn = Callable[[SpeechRequest, Draft], str]


def stub_model(role: Role) -> ModelFn:
    """Return a stub model callable for the given role."""

    def _run(request: SpeechRequest, draft: Draft) -> str:
        # In production, this would call a specific model with strict prompts.
        return f"[{role.name}] suggestion based on {request.occasion} / {request.audience}"

    return _run


ROLE_MODELS: Dict[Role, ModelFn] = {role: stub_model(role) for role in Role}


# ----- Orchestration -----


class HumanDecisionRequired(Exception):
    """Raised when the workflow must pause for human input."""


class Orchestrator:
    def __init__(self, request: SpeechRequest):
        self.request = request
        self.history: List[Draft] = []
        self.current = Draft(text="")

    def _checkpoint(self, reason: str) -> None:
        """Trigger a human-in-the-loop checkpoint."""
        raise HumanDecisionRequired(reason)

    def initial_briefing(self) -> None:
        """Create an initial outline informed by policy/data roles."""
        contributions = {
            Role.POLICY_EXPERT: ROLE_MODELS[Role.POLICY_EXPERT](self.request, self.current),
            Role.DATA_ADVISOR: ROLE_MODELS[Role.DATA_ADVISOR](self.request, self.current),
            Role.LOGIC_ARCHITECT: ROLE_MODELS[Role.LOGIC_ARCHITECT](self.request, self.current),
        }
        outline = "\n".join(contributions.values())
        self.current = Draft(text=outline, rationale=contributions)
        self.history.append(self.current)
        self._checkpoint("Review and approve the initial outline.")

    def debate_round(self) -> None:
        """Collect critiques and revisions from all roles."""
        feedback = {}
        for role in Role:
            feedback[role] = ROLE_MODELS[role](self.request, self.current)
        merged = self.current.text + "\n" + "\n".join(feedback.values())
        self.current = Draft(text=merged, rationale=feedback)
        self.history.append(self.current)
        self._checkpoint("Resolve disagreements and select direction.")

    def polish_and_risk_check(self) -> None:
        """Apply stylistic polish and run risk review."""
        stylist = ROLE_MODELS[Role.STYLIST](self.request, self.current)
        risk = ROLE_MODELS[Role.RISK_REVIEWER](self.request, self.current)
        merged = f"{self.current.text}\n\n[Stylist]\n{stylist}\n\n[Risk]\n{risk}"
        self.current = Draft(text=merged, rationale=self.current.rationale)
        self.history.append(self.current)
        self._checkpoint("Finalize wording and risk findings.")

    def generate_speaker_notes(self) -> Draft:
        """Produce speaker notes; in production, use dedicated prompt/model."""
        notes = [
            "Pause for emphasis after the core policy statement.",
            "Cite the specific policy document when mentioning achievements.",
        ]
        self.current.notes = notes
        self.history.append(self.current)
        return self.current


# ----- Example CLI flow (simulated) -----


def run_demo() -> None:
    """Simulate the workflow with stubbed checkpoints."""
    request = SpeechRequest(
        occasion="科技创新大会",
        audience="部委领导与市级代表",
        keywords=["自主创新", "安全可信", "高质量发展"],
        tone="庄重而鼓舞人心",
        duration_minutes=15,
        must_quote=["政府工作报告"],
        forbidden_terms=["市场过度化承诺"],
    )

    orchestrator = Orchestrator(request)
    steps = [
        orchestrator.initial_briefing,
        orchestrator.debate_round,
        orchestrator.polish_and_risk_check,
        orchestrator.generate_speaker_notes,
    ]

    for step in steps:
        try:
            step()
        except HumanDecisionRequired as pause:
            # In real use, persist state and surface decision to the user UI.
            print(f"[HUMAN ACTION NEEDED] {pause}")
            # For demo purposes, auto-continue.
            continue

    print("--- Latest draft ---")
    print(orchestrator.current.text)
    print("--- Speaker notes ---")
    for note in orchestrator.current.notes:
        print(f"- {note}")


if __name__ == "__main__":
    run_demo()

