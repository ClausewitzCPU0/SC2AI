# Using a edited version of python-sc2

import sc2
from sc2 import run_game, maps, Race, Difficulty, position, Result
from sc2.player import Bot, Computer, Human
from sc2.constants import *
import random
import cv2
import numpy as np
import time
import multiprocessing
import os

HEADLESS = False


class ProtossBot(sc2.BotAI):
    def __init__(self):
        # Setup for the game, establishing some constants used for this build
        self.ITERATIONS_PER_MINUTE = 260
        self.MAX_WORKERS = 22
        self.do_something_after = 0
        self.train_data = []
        self.warpgate_started = False
        self.blink_started = False
        self.proxy_built = False
        self.warpgate_done = False

    # Requires modification of python-sc2 package
    def on_end(self, game_result):

        if game_result == Result.Victory:
            np.save(os.path.dirname(os.path.realpath(__file__)) + "/train_data/{}.npy".format(str(int(time.time()))),
                    np.array(self.train_data))

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.scout()
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.intel()
        await self.attack()
        await self.warp_units()
        await self.build_proxy_pylon()
        await self.morph_gates()
        await self.chronoboost()
        await self.blink()

    # Mix up the scouting pattern
    def random_location_variance(self, enemy_start_location):
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-20, 20)) / 100) * enemy_start_location[0]
        y += ((random.randrange(-20, 20)) / 100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.game_info.map_size[0]:
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            y = self.game_info.map_size[1]

        # Have to convert the position to Point2 from pointlike
        go_to = position.Point2(position.Pointlike((x, y)))
        return go_to

    # Use our adepts to locate the enemy
    async def scout(self):
        if len(self.units(ADEPT)) > 0:
            scout = self.units(ADEPT)[0]
            if scout.is_idle:
                enemy_location = self.enemy_start_locations[0]
                move_to = self.random_location_variance(enemy_location)
                await self.do(scout.attack(move_to))

    # Visualizes the game from the bots perspective, especially useful for linux users
    async def intel(self):
        # setup up the data type
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)

        # Prefixed colours for our buildings and units
        unit_colours = {
            NEXUS: [15, (0, 255, 0)],
            PYLON: [3, (20, 235, 0)],
            PROBE: [1, (55, 200, 0)],
            STALKER: [2, (67, 200, 43)],
            ASSIMILATOR: [2, (55, 200, 0)],
            GATEWAY: [3, (200, 100, 0)],
            CYBERNETICSCORE: [3, (150, 150, 0)],
            TWILIGHTCOUNCIL: [5, (255, 0, 0)],
        }

        # Loop over our buildings and draw them
        for unit_type in unit_colours:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), unit_colours[unit_type][0],
                           unit_colours[unit_type][1], -1)

        main_bases = ["nexus", "commandcenter", "hatchery"]

        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() not in main_bases:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
        for enemy_building in self.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() in main_bases:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)

        for enemy_unit in self.known_enemy_units:

            if not enemy_unit.is_structure:
                worker_names = ["probe",
                                "scv",
                                "drone"]

                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)

        # Establishing bars, that represent the game state, into our imagine
        line_max = 50
        mineral_ratio = self.minerals / 1500
        if mineral_ratio > 1.0:
            mineral_ratio = 1.0

        vespene_ratio = self.vespene / 1500
        if vespene_ratio > 1.0:
            vespene_ratio = 1.0

        population_ratio = self.supply_left / self.supply_cap
        if population_ratio > 1.0:
            population_ratio = 1.0

        plausible_supply = self.supply_cap / 200.0

        military_weight = len(self.units(STALKER)) / (self.supply_cap - self.supply_left)
        if military_weight > 1.0:
            military_weight = 1.0

        cv2.line(game_data, (0, 19), (int(line_max * military_weight), 19), (250, 250, 200), 3)  # worker/supply ratio
        cv2.line(game_data, (0, 15), (int(line_max * plausible_supply), 15), (220, 200, 200),
                 3)  # plausible supply (supply/200.0)
        cv2.line(game_data, (0, 11), (int(line_max * population_ratio), 11), (150, 150, 150),
                 3)  # population ratio (supply_left/supply)
        cv2.line(game_data, (0, 7), (int(line_max * vespene_ratio), 7), (210, 200, 0), 3)  # gas / 1500
        cv2.line(game_data, (0, 3), (int(line_max * mineral_ratio), 3), (0, 255, 25), 3)  # minerals minerals/1500

        # flip horizontally to fix visual representation
        self.flipped = cv2.flip(game_data, 0)

        # show the imagine
        if not HEADLESS:
            resized = cv2.resize(self.flipped, dsize=None, fx=2, fy=2)
            cv2.imshow('Intel', resized)
            cv2.waitKey(1)

    # These functions just build buildings or units
    async def build_workers(self):
        if len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near=nexuses.first.position.towards(self.game_info.map_center, 10))

    async def build_assimilators(self):
        if ((self.units(ASSIMILATOR).amount < 2 and self.supply_used > 15) or self.supply_used > 120):
            for nexus in self.units(NEXUS).ready:
                vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
                for vaspene in vaspenes:
                    if not self.can_afford(ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.supply_used < 33 and self.can_afford(NEXUS):
            await self.expand_now()

    async def warp_new_units(self, proxy):
        for warpgate in self.units(WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)
            # Lets warp in stalkers :)
            if AbilityId.WARPGATETRAIN_STALKER in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    return
                await self.do(warpgate.warp_in(STALKER, placement))

    async def offensive_force_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif self.supply_used == 15 or self.supply_used == 19 or (
                    self.supply_used == 36 and len(self.units(GATEWAY)) < 4) or (
                    len(self.units(WARPGATE)) < 6 and self.warpgate_done):
                if self.can_afford(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(TWILIGHTCOUNCIL)) < 1:
                    if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                        await self.build(TWILIGHTCOUNCIL, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(
                    RESEARCH_WARPGATE) and not self.warpgate_started:
                ccore = self.units(CYBERNETICSCORE).ready.first
                await self.do(ccore(RESEARCH_WARPGATE))
                self.warpgate_started = True

            if self.units(TWILIGHTCOUNCIL).ready.exists:
                if self.can_afford(RESEARCH_BLINK) and not self.blink_started:
                    twc = self.units(TWILIGHTCOUNCIL).ready.first
                    await self.do(twc(RESEARCH_BLINK))
                    blink_started = True

    async def build_offensive_force(self):
        if self.supply_used < 28:
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.can_afford(ADEPT) and self.supply_left > 0:
                    await self.do(gw.train(ADEPT))
        elif self.supply_used >= 28 and self.supply_used < 31:
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    # This functon is used for attacking. Consists of 4 options:
    # 1. Do nothing
    # 2. Attack enemy units
    # 3. Attack enemy buildings
    # 4. Attack the enemy starting location
    async def attack(self):
        if len(self.units(STALKER).idle) > 8:
            choice = random.randrange(0, 4)
            target = False
            if self.iteration > self.do_something_after:
                if choice == 0:
                    # no attack
                    wait = random.randrange(20, 165)
                    self.do_something_after = self.iteration + wait

                elif choice == 1:
                    # attack the unit closest to the nexuses
                    if len(self.known_enemy_units) > 0:
                        target = self.known_enemy_units.closest_to(random.choice(self.units(NEXUS)))
                    # attack enemy buildings
                elif choice == 2:
                    if len(self.known_enemy_structures) > 0:
                        target = random.choice(self.known_enemy_structures)
                    # attack enemy staring position
                elif choice == 3:
                    target = self.enemy_start_locations[0]

                # Loop over idle stalkers and attack the position
                if target:
                    for st in self.units(STALKER).idle:
                        await self.do(st.attack(target))

                # save the choice to an array used in our machine learning
                y = np.zeros(4)
                y[choice] = 1
                # We have to flip it again to get the size properly
                self.train_data.append([y, self.flipped])

    async def warp_units(self):
        if self.proxy_built and self.units(WARPGATE).ready:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            await self.warp_new_units(proxy)

    async def build_proxy_pylon(self):
        if self.units(CYBERNETICSCORE).amount >= 1 and not self.proxy_built and self.can_afford(PYLON):
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 20)
            await self.build(PYLON, near=p)
            self.proxy_built = True

    async def morph_gates(self):
        for gateway in self.units(GATEWAY).ready:
            abilities = await self.get_available_abilities(gateway)
            if AbilityId.MORPH_WARPGATE in abilities and self.can_afford(AbilityId.MORPH_WARPGATE):
                await self.do(gateway(MORPH_WARPGATE))
                warpgate_done = True

    # Used for chronoboost
    async def chronoboost(self):
        if self.units(CYBERNETICSCORE).ready.exists and not self.units(WARPGATE).exists:
            ccore = self.units(CYBERNETICSCORE).ready.first
            if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                for nexus in self.units(NEXUS).ready:
                    abilities = await self.get_available_abilities(nexus)
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                        for nexus in self.units(NEXUS).ready:
                            await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))
        elif self.units(TWILIGHTCOUNCIL).ready.exists:
            twlc = self.units(TWILIGHTCOUNCIL).ready.first
            if not twlc.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                for nexus in self.units(NEXUS).ready:
                    abilities = await self.get_available_abilities(nexus)
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                        for nexus in self.units(NEXUS).ready:
                            await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, twlc))

    # check if we have an ability
    async def has_ability(self, ability, unit):
        abilities = await self.get_available_abilities(unit)
        if ability in abilities:
            return True
        else:
            return False

    # Sexy blink micro time
    async def blink(self):
        for stalker in self.units(STALKER):
            has_blink = await self.has_ability(EFFECT_BLINK_STALKER, stalker)
            threatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(5, stalker)
            if threatsClose and stalker.shield < 20:
                escape_location = stalker.position.towards(self.game_info.map_center, 4)
                if has_blink:
                    await self.do(stalker(EFFECT_BLINK_STALKER, escape_location))


# Final method to launch the game with our bot
def game():
    run_game(maps.get("AutomatonLE"), [
        Bot(Race.Protoss, ProtossBot()),
        Computer(Race.Zerg, Difficulty.Hard)
    ], realtime=True)


# Lets run it multithread to get more data.
while (True):
    # if __name__ == '__main__':
    #     thread1 = multiprocessing.Process(target=game, args=())
    #     thread2 = multiprocessing.Process(target=game, args=())
    #     thread3 = multiprocessing.Process(target=game, args=())
    #     thread1.start()
    #     thread2.start()
    #     thread3.start()
    #     thread1.join()
    #     thread2.join()
    #     thread3.join()
    game()
