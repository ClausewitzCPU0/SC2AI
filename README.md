# SC2 AI

本文作者 @PolestarX **转载请注明出处** 

**禁止百家号使用本文任何内容**

程序基于deepmind开源 py-sc2

https://github.com/deepmind/pysc2

教程来自youtube [sentdex](https://www.youtube.com/channel/UCfzlCWGWYyIQ0aLC5w48gBQ) ，修复了一些原教程在当前版本可能出现的BUG

https://www.youtube.com/watch?v=v3LJ6VvpfgI&list=PLQVvvaa0QuDcT3tPehHdisGMc8TInNqdq&index=2&t=0s

单位名称查阅

https://liquipedia.net/starcraft2/Protoss_Units_(Legacy_of_the_Void)

## 前言

本教程为简略的星际2 AI编写**入门**demo,属于**娱乐**性质。玩家观看此教程之后开发出的谐星AI（比如XieStar），与作者无关，希望能起到抛砖引玉的效果。

使用者有一点Python基础和对星际2的粗略了解即可完成本教程。

本人不是深度学习从业人员，也没有强大的硬件支持，因此暂时不涉及深度学习相关内容。

感谢deepmind为开源社区做出的贡献，也向youtube的sentdex致敬。

------

**以下内容可略过不看，直接跳到教程部分。**  

从围棋到DOTA2，AI似乎无往不利。Alphastar对战人类10:1的战绩被广泛传播，甚至有无良营销号打出AI 10:0完胜人类的标题。然而在Mana唯一获胜的那场直播中，正面操作无懈可击的Alphastar被一个棱镜耍得晕头转向，变成了F2 AI。星际2作为RTS游戏的代表，其拥有的战争迷雾机制和巨大的策略空间，对AI来说是从未有过的挑战。几百年的训练时间培养出了正面、多线操作和运营方面的怪物，然而与训练时间不相匹配的是孱弱的大局观。演示局结束后，deepmind的研发人员接受现场采访，他们并没有沉浸在巨大比分优势的喜悦中，而是很清楚地认识到，人类玩家在这11盘中都没有使用早期战术，而且最后一盘的反击则让AI的劣势显露无疑。Alphastar还有很多需要完善的地方。

最近Alphastar开始在欧服天梯上匿名训练，让星际玩家又多了几分期待。~~AI小儿只敢隐姓埋名，定是畏惧我谐星战术，真懦夫也。~~感谢暴雪创造了这个伟大的RTS游戏，感谢deepmind为我们揭示了这款游戏的别样魅力，感谢星际2的玩家们成就了电子竞技！

星际2是否是人类在游戏方面与AI抗衡的最后一个堡垒？我们拭目以待。

I don't see why a game needs to be big for someone to love playing it. ——Naniwa

#### GL HF !



## 教程

### **Ch1. 开发环境简介以及简单的采矿操作**

第一节教程旨在了解星际2 API和pysc2的基本安装、使用方法，并编写一个可以自动采矿的AI。

我的开发环境：

```
软件：Win10、Python3.6、星际2 4.9.3版本  
硬件：E3 1231v3、20GB DDR3、GTX 970M
# 必须先装好python开发环境，过程此处不再赘述
```

1. Mac或者Win平台安装星际2游戏，linux平台暂无（我用的win平台。不用linux的原因是linux没有完整的游戏界面）

2. https://github.com/deepmind/pysc2    clone仓库或

   直接pip安装（我用的pip）：执行`pip install pysc2` 版本号2.0.2

3. https://github.com/Blizzard/s2client-proto#downloads 下载地图包，我下载了19年第一赛季的地图

4. 解压地图包到游戏目录的Maps文件夹下，如果没有就新建（密码： iagreetotheeula）注意保留地图包文件夹，不要直接把rep文件放到Maps文件夹中。

5. 修改sc2包中的paths.py 修改对应平台的游戏路径（此处修改win平台）

   ```python
   BASEDIR = {
       "Windows": "F:\Games\StarCraft II", # 修改此处
       "Darwin": "/Applications/StarCraft II",
       "Linux": "~/StarCraftII",
       "WineLinux": "~/.wine/drive_c/Program Files (x86)/StarCraft II",
   }
   ```

6. 编写代码并运行，可以看到游戏界面（可能会遇到错误，解决方法看本节最后）

   ```python
   """
   一个简单的入门程序 星际2 4.9.3版本测试通过
   PvP 对手简单电脑 我方AI只采矿 地图为AutomatonLE
   """
   import sc2
   from sc2 import run_game, maps, Race, Difficulty
   from sc2.player import Bot, Computer
   
   
   class SentdeBot(sc2.BotAI):
       async def on_step(self, iteration: int):
           await self.distribute_workers() # 分配农民采矿
   
   
   run_game(maps.get("AutomatonLE"), [
       Bot(Race.Protoss, SentdeBot()),
       Computer(Race.Protoss, Difficulty.Easy)], realtime=True)
   ```

   如果游戏放在固态硬盘里，启动会快很多。效果图如下：

   ![1563176821707](assets/1563176821707.png)

#### 错误记录：

ValueError: 3794 is not a valid AbilityId

版本问题引起。星际2现版本为4.9.3（19年7月）

https://www.bountysource.com/issues/74655708-valueerror-3794-is-not-a-valid-abilityid

ocnuybear commented on this issue 10 days ago.

1. Browse to c:\program files (x86)\microsoft visual studio\shared\python37_64\lib\site-packages\sc2 (I'm using Python in Visual Studio 2019 environment)
2. Edit game_data.py and comment out 'assert self.id != 0' with # in front, save changes.
3. Edit pixel_map.py and comment out 'assert self.bits_per_pixel % 8 == 0, "Unsupported pixel density"' with # in front, save changes.

Run again and game should work now fully updated on 4 Jul 2019



### **Ch2. 建造探机和水晶**

本节为AI增加了有余钱时自动建造水晶和探机的AI。不足之处是AI会一直建造探机，哪怕超过采矿效率上限。有概率一次补两个水晶，造成资源浪费。

**部分代码**如下：（完全版代码见文件夹内 ch2_Workers_and_Pylons.py ）

```python
"""
造农民和水晶
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from sc2.constants import NEXUS, PROBE, PYLON
# 如果IDE报错，你需要这么写
# from sc2.ids.unit_typeid import UnitTypeId as uid
# NEXUS = uid.NEXUS
# PROBE = uid.PROBE

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()

    async def build_workers(self):
        """
        选择空闲基地建造农民
        noqueue意味着当前建造列表为空
        """
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
                    await  self.build(PYLON, near=nexuses.first) # near表示建造地点。后期可以用深度学习优化
                            
        """
        此处略去部分内容
        """
```

效果如下：

![1563188660358](assets/1563188660358.png)

#### 错误记录：

"from sc2.constants import PROBE" not working 

某些IDE造成的问题，直接用IDLE可以运行。

https://github.com/Dentosal/python-sc2/issues/58

https://github.com/Dentosal/python-sc2/issues/104

You can avoid it by doing:

```
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.effect_id import EffectId
```

This is probably the better choice because **VScode and pycharm** both mark the enums red if you dont have a `UnitTypeId.` in front of the name, unless you disabled that warning.

Also, see [#58](https://github.com/Dentosal/python-sc2/issues/58) and [#55](https://github.com/Dentosal/python-sc2/issues/55)

Sidenote:
There isn't anything we can do since these are the names directly from the SC2 API.



### Ch3.  采气及扩张

这一节为AI增加了采气和关键的扩张逻辑。但是，AI会直接扩张（雅典娜的惊叹），**没有任何战斗单位防御**，并且还是会一直补农民。run_game函数的realtime参数设为False可以加速游戏进程，方便获取结果。

部分代码

```python
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        
        """
        此处略去部分内容
        """
        
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


run_game(maps.get("AutomatonLE"), [
    Bot(Race.Protoss, SentdeBot()),
    Computer(Race.Protoss, Difficulty.Easy)], realtime=False)  # realtime设为False可以加速

```

效果如下，AI已经学会采气，并开始开三矿：

![1563203983259](assets/1563203983259.png)



### Ch4 建造战斗单位

这一节中为AI增加建造战斗单位及其前置建筑的能力。缺点是AI只会单兵营出追猎。追猎没有主动进攻能力，不会保护己方单位。不过既然AI已经有能力生产战斗单位，那么离胜利也就更进一步了。

部分代码如下：

```python
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
    CYBERNETICSCORE, STALKER
    
class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration: int):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()

        """
        此处略去部分内容
        """

    async def offensive_force_buildings(self):
        """
        建造产兵建筑
        """
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(GATEWAY).ready.exists:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
            else:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

    async def build_offensive_force(self):
        """
        建造战斗单位
        """
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.do(gw.train(STALKER))
```

![1563203612444](assets/1563203612444.png)