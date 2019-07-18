"""
和你创建的AI对战
"""
from sc2 import run_game, maps, Race
from sc2.player import Bot, Human
# Import the library
import sc2


# All bots inherit from sc2.BotAI
class WorkerRushBot(sc2.BotAI):

    # The on_step function is called for every game step
    # It is defined as async because it calls await functions
    # It takes current game state and current iteration
    async def on_step(self, iteration):

        if iteration == 0:  # If this is the first frame

            for worker in self.workers:
                # Attack to the enemy base with this worker
                # (Assumes that there is only one possible starting location
                # for the opponent, which depends on the map)
                await self.do(worker.attack(self.enemy_start_locations[0]))


run_game(maps.get("AutomatonLE"), [
    Human(Race.Terran),
    Bot(Race.Zerg, WorkerRushBot())
], realtime=True)
