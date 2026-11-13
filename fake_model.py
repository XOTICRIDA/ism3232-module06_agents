# fake_model.py
# Author: [River Sookralli]


class FakeModel:
    """A model for tests. It plays back a list of decisions, one per call."""

    def __init__(self, decisions):
        """Store the decisions to play back, in order."""
        self.decisions = decisions
        self.calls = 0

    def decide(self, instructions, history, tools):
        """Return the next decision in the list."""
        decision = self.decisions[self.calls]
        self.calls += 1
        return decision
