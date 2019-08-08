import sc2
from sc2.player import Bot, Computer
from sc2 import run_game, maps, Race, Difficulty
from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2, Point3
from sc2.constants import *
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.ids.ability_id import AbilityId
from sc2.helpers import ControlGroup
from typing import List, Dict, Set, Tuple, Any, Optional, Union  # mypy type checking

"""
将散机枪操作和运营加入到同一个AI中
前置5BB
击败最高难度虫族电脑

可优化的地方：
通过侦查改变策略
降低攻击虫卵优先级
攻击建筑时无需走A
消灭敌方主力之后优先进攻主矿
"""


class LittleByuN(sc2.BotAI):
    def __init__(self):
        self.attack_groups = set()

    async def on_step(self, iteration):
        if iteration == 0:
            await self.on_first_iteration()

        actions = []

        await self.build_Barracks(iteration)
        await self.marine_micro(actions)

    async def build_Barracks(self, iteration):
        cc = self.units(COMMANDCENTER)
        if not cc.exists:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            for unit in self.workers | self.units(MARINE):
                await self.do(unit.attack(target))
            return
        else:
            cc = cc.first

        if self.units(MARINE).idle.amount > 15 and iteration % 50 == 1:
            cg = ControlGroup(self.units(MARINE).idle)
            self.attack_groups.add(cg)

        if self.can_afford(SCV) and self.workers.amount < 16 and cc.noqueue:
            await self.do(cc.train(SCV))

        elif self.supply_left < (2 if self.units(BARRACKS).amount < 3 else 4):
            if self.can_afford(SUPPLYDEPOT) and self.already_pending(SUPPLYDEPOT) < 2:
                await self.build(SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 5))

        elif self.units(BARRACKS).amount < 3 or (self.minerals > 400 and self.units(BARRACKS).amount < 5):
            if self.can_afford(BARRACKS):
                p = self.game_info.map_center.towards(self.enemy_start_locations[0], 25)
                await self.build(BARRACKS, near=p)

        for rax in self.units(BARRACKS).ready.noqueue:
            if not self.can_afford(MARINE):
                break
            await self.do(rax.train(MARINE))

        for scv in self.units(SCV).idle:
            await self.do(scv.gather(self.state.mineral_field.closest_to(cc)))

        for ac in list(self.attack_groups):
            alive_units = ac.select_units(self.units)
            if alive_units.exists and alive_units.idle.exists:
                target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
                for marine in ac.select_units(self.units):
                    await self.do(marine.attack(target))
            else:
                self.attack_groups.remove(ac)

    async def marine_micro(self, actions):

        # do marine micro vs zerglings
        for unit in self.units(UnitTypeId.MARINE):

            if self.known_enemy_units:  # 如果视野中有敌方单位

                # attack (or move towards) zerglings / banelings
                if unit.weapon_cooldown <= self._client.game_step / 2:
                    enemies_in_range = self.known_enemy_units.filter(lambda u: unit.target_in_range(u))

                    # attack lowest hp enemy if any enemy is in range
                    if enemies_in_range:
                        # Use stimpack
                        if self.already_pending_upgrade(UpgradeId.STIMPACK) == 1 and not unit.has_buff(
                                BuffId.STIMPACK) and unit.health > 10:
                            actions.append(unit(AbilityId.EFFECT_STIM))

                        # attack baneling first
                        filtered_enemies_in_range = enemies_in_range.of_type(UnitTypeId.BANELING)

                        if not filtered_enemies_in_range:
                            closest_enemy = self.known_enemy_units.closest_to(unit)
                            actions.append(unit.attack(closest_enemy))
                        else:
                            actions.append(unit.attack(filtered_enemies_in_range))

                    # no enemy is in attack-range, so give attack command to closest instead
                    else:
                        closest_enemy = self.known_enemy_units.closest_to(unit)
                        actions.append(unit.attack(closest_enemy))


                # move away from zergling / banelings
                else:
                    stutter_step_positions = self.position_around_unit(unit, distance=4)

                    # filter in pathing grid
                    stutter_step_positions = {p for p in stutter_step_positions if self.in_pathing_grid(p)}

                    # find position furthest away from enemies and closest to unit
                    enemies_in_range = self.known_enemy_units.filter(lambda u: unit.target_in_range(u, -0.5))

                    if stutter_step_positions and enemies_in_range:
                        retreat_position = max(stutter_step_positions,
                                               key=lambda x: x.distance_to(enemies_in_range.center) - x.distance_to(
                                                   unit))
                        actions.append(unit.move(retreat_position))

                    else:
                        print("No retreat positions detected for unit {} at {}.".format(unit, unit.position.rounded))

        await self.do_actions(actions)

    async def on_first_iteration(self):
        await self.chat_send("(glhf)")  # 要发送的消息
        self._client.game_step = 4  # 每4帧执行一次动作。默认值为8帧。这个数值越小，电脑APM越高。

    def position_around_unit(self, pos: Union[Unit, Point2, Point3], distance: int = 1, step_size: int = 1,
                             exclude_out_of_bounds: bool = True):
        pos = pos.position.to2.rounded
        positions = {pos.offset(Point2((x, y)))
                     for x in range(-distance, distance + 1, step_size)
                     for y in range(-distance, distance + 1, step_size)
                     if (x, y) != (0, 0)}
        # filter positions outside map size
        if exclude_out_of_bounds:
            positions = {p for p in positions if 0 <= p[0] < self._game_info.pathing_grid.width and 0 <= p[
                1] < self._game_info.pathing_grid.height}
        return positions


def main():
    sc2.run_game(sc2.maps.get("AutomatonLE"), [
        Bot(Race.Terran, LittleByuN()),
        Computer(Race.Zerg, Difficulty.CheatInsane)
    ], realtime=True, save_replay_as="Example.SC2Replay")


if __name__ == '__main__':
    main()
