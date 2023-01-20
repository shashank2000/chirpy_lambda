from .. import BaseIntegrationTest
import pytest


class TestStartup(BaseIntegrationTest):
    def test_startup(self):
        bot = self.startup_bot(launch_script=True)
        assert bot.text

    def test_name_recognized(self):
        bot = self.startup_bot(launch_script=True)
        assert bot.text

    @pytest.mark.parametrize("stop_word", ["stop", "stop talking"])
    def test_stop_means_stop(self, stop_word):
        bot = self.startup_bot(launch_script=True)
        bot.run(stop_word)
        assert bot.stop

    @pytest.mark.parametrize("stop_word", ["stop", "stop talking"])
    def test_stop_on_launch(self, stop_word):
        bot = self.startup_bot()
        bot.run(stop_word)
        assert bot.stop
