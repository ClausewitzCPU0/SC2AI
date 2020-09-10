"""
应用深度学习 导言篇
将游戏内单位可视化
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
    CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY
import random
import cv2
import numpy as np


class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 80  # 限制最大农民数

    async def on_step(self, iteration: int):  # iteration类似游戏时钟 每分钟165个迭代(待确认)
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()
        await self.intel()

    async def intel(self):
        """
        原作者随便起的名字，你也可以起名为amd
        该函数将游戏运行过程可视化
        """
        print('dir:', dir(self))  # 你总是可以使用dir命令来获取帮助，也可以直接看源码
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)  # 反转图片像素
        # 画出每个基地的位置
        for nexus in self.units(NEXUS):
            nex_pos = nexus.position
            cv2.circle(game_data, (int(nex_pos[0]), int(nex_pos[1])),
                       10, (0, 255, 0), -1)  # 10代表尺寸,元组代表BGR颜色格式(注意不是RGB的排列顺序),-1代表描边线宽

        # 转换坐标
        flipped = cv2.flip(game_data, 0)  # 翻转
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
        cv2.imshow('Intel', resized)
        cv2.waitKey(1)  # 1ms

    async def build_workers(self):
        """
        选择空闲基地建造农民
        noqueue意味着当前建造列表为空
        """
        if len(self.units(NEXUS)) * 24 > len(self.units(PROBE)):  # 每矿农民补满就不补了
            if len(self.units(PROBE)) < self.MAX_WORKERS:
                for nexus in self.units(NEXUS).ready.noqueue:
                    if self.can_afford(PROBE):
                        await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        """
        人口空余不足5时造水晶。
        """
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await  self.build(PYLON, near=nexuses.first)  # near表示建造地点。后期可以用深度学习优化

    async def build_assimilators(self):
        """
        建造气矿
        """
        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(25.0, nexus)
            for vespene in vespenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene))

    async def expand(self):
        """
        何时扩张 简化版
        基地数量少于3个就立即扩张
        """
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()

    async def offensive_force_buildings(self):
        """
        建造产兵/科技建筑
        """
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            # 建造BY
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)
            # 建造1个BG解锁科技即可
            elif len(self.units(GATEWAY)) < 1:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)
            # 这个VS放的早啊
            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < (self.iteration / self.ITERATIONS_PER_MINUTE):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)

    async def build_offensive_force(self):
        """
        建造战斗单位（只要虚空）
        """
        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))

    def find_target(self, state):
        """
        寻找敌方单位
        注意这个函数不是异步的，不用加async
        """
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        """
        控制单位攻击视野内敌方单位
        """
        # {UNIT: [n to fight, n to defend] } 也是粗略计算
        aggressive_units = {STALKER: [15, 5],
                            VOIDRAY: [8, 3]}

        for UNIT in aggressive_units:
            # 如果数量比预定攻击单位数量多，那就主动出击，否则防守（此处疑似代码冗余）
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][
                1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))


def main():
    run_game(maps.get("AutomatonLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Protoss, Difficulty.Hard)], realtime=False)  # realtime设为False可以加速


if __name__ == '__main__':
    main()
