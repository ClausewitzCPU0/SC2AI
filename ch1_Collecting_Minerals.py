"""
一个简单的入门程序 星际2 4.9.3版本测试通过
PvP 对手简单电脑 我方AI只采矿 地图为AutomatonLE
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer


class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()


def main():
    run_game(maps.get("AutomatonLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Protoss, Difficulty.Easy)], realtime=True)


if __name__ == '__main__':
    main()
