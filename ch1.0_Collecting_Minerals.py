"""
一个简单的入门程序 星际2 4.9.3版本测试通过
PvP 对手简单电脑 我方AI只采矿 地图为AutomatonLE
"""
import sc2
# run_game用于启动游戏并指定各项启动参数
# maps指定游戏在哪张地图上运行。Race选择种族，Difficulty选择电脑难度。
from sc2 import run_game, maps, Race, Difficulty
# Bot和Computer分别指你自己写的AI和游戏内置的电脑
from sc2.player import Bot, Computer


class SentdeBot(sc2.BotAI):
    """
    这个类就是你要写的AI类，必须要继承sc2.BotAI，很多内置方法都在其中
    """

    async def on_step(self, iteration: int):
        """
        on_step这个异步方法必须被重写，再此将会调用你设置的每一步指令。
        """
        # distribute_workers是内置方法，代表自动让农民采矿
        await self.distribute_workers()


def main():
    run_game(maps.get("AutomatonLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Protoss, Difficulty.Easy)], realtime=True)


if __name__ == '__main__':
    main()
