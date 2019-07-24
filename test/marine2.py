import sc2
from sc2 import Race
from sc2.player import Bot

from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2, Point3

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.ids.ability_id import AbilityId

from typing import List, Dict, Set, Tuple, Any, Optional, Union  # mypy type checking

"""
SOURCE: Dentosal
MODIFTED BY: PolestarX

第二个版本的枪兵操作
机枪兵在散的同时优先点毒爆和残血单位。

原程序需要在美服用地图编辑器下载“Marine Split Challenge-LOTV”的一张散枪兵练习图。
我没法登陆美服的编辑器，就在国服找了一张练习图，效果一样。
地图名为Marine Control  v1.4(作者：Morrow)，我把它放在resource文件夹中。
值得一提的是，国服还有一张散枪兵演示图，使用银河编辑器的触发器实现甩枪兵，有兴趣的可以看一看。
"""


class MarineSplitChallenge(sc2.BotAI):
    async def on_step(self, iteration):
        if iteration == 0:
            await self.on_first_iteration()

        actions = []

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
                            filtered_enemies_in_range = enemies_in_range.of_type(UnitTypeId.ZERGLING)
                        # attack lowest hp unit
                        lowest_hp_enemy_in_range = min(filtered_enemies_in_range, key=lambda u: u.health)
                        actions.append(unit.attack(lowest_hp_enemy_in_range))

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
    sc2.run_game(sc2.maps.get("Marine Control v1.4"), [
        Bot(Race.Terran, MarineSplitChallenge()),
    ], realtime=True, save_replay_as="Example.SC2Replay")


if __name__ == '__main__':
    main()
