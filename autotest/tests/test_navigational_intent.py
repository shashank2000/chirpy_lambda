from .. import BaseIntegrationTest
import pytest


class TestPrioritizeSupernode(BaseIntegrationTest):
    @pytest.mark.parametrize("prioritized_supernode", ["FOOD__intro", "OPINION__intro", "CELEB__intro"])
    def test_prioritize_supernode(self, prioritized_supernode):
        """This test sets the score of the supernode to +1e10 so that it has a ~1e-10 chance of failing."""
        bot = self.startup_bot(launch_script=True, prioritized_supernode=prioritized_supernode)
        assert prioritized_supernode in bot.supernodes and bot.supernodes[prioritized_supernode]["chosen"] != False
