"""
 SOURCE: https://github.com/Dentosal/python-sc2/blob/master/examples/protoss/cannon_rush.py
 MODIFIED BY: PolestarX
 修电脑炮台并发表情嘲讽
"""
import random

import sc2
from sc2 import Race, Difficulty
from sc2.constants import NEXUS, PROBE, PYLON, FORGE, PHOTONCANNON
from sc2.player import Bot, Computer


class CannonRushBot(sc2.BotAI):
    async def on_step(self, iteration):
        """
        繁杂的条件判断自行优化
        :param iteration: iteration可以看作是游戏内时钟，大概每分钟165个迭代。
        """
        if iteration == 0:
            await self.chat_send("(probe)(pylon)(cannon)(cannon)(gg)")  # 此处表示游戏刚开始的时候发消息。()是游戏内发表情的语法

        if not self.units(NEXUS).exists:
            for worker in self.workers:
                await self.do(worker.attack(self.enemy_start_locations[0]))
            return
        else:
            nexus = self.units(NEXUS).first

        if self.workers.amount < 16 and nexus.noqueue:  # 少于16农民且基地不在生产时，建造农民
            if self.can_afford(PROBE):
                await self.do(nexus.train(PROBE))

        elif not self.units(PYLON).exists and not self.already_pending(PYLON):  # 补第一根水晶
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexus)

        elif not self.units(FORGE).exists:  # 水晶造好后下BF
            pylon = self.units(PYLON).ready
            if pylon.exists:
                if self.can_afford(FORGE):
                    await self.build(FORGE, near=pylon.closest_to(nexus))

        elif self.units(PYLON).amount < 2:  # 直接在敌方主矿附近点下第二根水晶
            if self.can_afford(PYLON):
                pos = self.enemy_start_locations[0].towards(self.game_info.map_center, random.randrange(8, 15))
                await self.build(PYLON, near=pos)

        elif not self.units(PHOTONCANNON).exists:  # 敌方家里下炮台
            if self.units(PYLON).ready.amount >= 2 and self.can_afford(PHOTONCANNON):
                pylon = self.units(PYLON).closer_than(20, self.enemy_start_locations[0]).random
                await self.build(PHOTONCANNON, near=pylon)

        else:  # 在敌方主矿范围内随机下水晶和炮台，保证炮台射程覆盖面积
            if self.can_afford(PYLON) and self.can_afford(PHOTONCANNON):  # ensure "fair" decision
                for _ in range(20):
                    pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
                    building = PHOTONCANNON if self.state.psionic_matrix.covers(pos) else PYLON
                    r = await self.build(building, near=pos)
                    if not r:  # success
                        break


def main():
    sc2.run_game(sc2.maps.get("AutomatonLE"), [
        Bot(Race.Protoss, CannonRushBot(), name="CheeseCannon"),
        Computer(Race.Protoss, Difficulty.Medium)
    ], realtime=False)


if __name__ == '__main__':
    main()
