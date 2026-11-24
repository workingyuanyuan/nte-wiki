---
title: Combat formulas
description: How NTE calculates damage, critical hits, Break and Ultimate Energy.
aliases:
  - 戰鬥數值
  - 战斗数值
  - 戦闘の計算式
  - 전투 공식
appliesTo: Version 1.5, game data 1.5.4
lastVerified: 2026-11-21
caveat: Break does not make the enemy take more damage. It stops the enemy for a while and deals one Break Damage hit, worked out from all four party members.
sources:
  - title: nanoka.cc game data 1.5.4, character files in English (base Crit, Ultimate Energy cost, role tags)
    url: https://static.nanoka.cc/nte/1.5.4/en/character/1003.json
  - title: nanoka.cc game data 1.5.4, character files in Chinese
    url: https://static.nanoka.cc/nte/1.5.4/zh/character/1003.json
  - title: nanoka.cc game data 1.5.4, character files in Japanese (base Crit, Ultimate Energy cost, role tags)
    url: https://static.nanoka.cc/nte/1.5.4/ja/character/1003.json
  - title: nanoka.cc game data 1.5.4, character files in Korean (base Crit, Ultimate Energy cost, role tags)
    url: https://static.nanoka.cc/nte/1.5.4/ko/character/1003.json
  - title: 零号攻略组, video on damage multipliers, Bilibili, in Simplified Chinese (2026-06-21)
    url: https://www.bilibili.com/video/BV13ijt6gEF4/
  - title: NGA forum, player analysis of damage and Esper Cycle mechanics, in Simplified Chinese (read 2026-11-21)
    url: https://bbs.nga.cn/read.php?tid=46659382
  - title: GameWith, Break Gauge guide
    url: https://gamewith.net/nte/74130
---

## Damage

Damage = skill multiplier × scaling stat × DMG Bonus × Crit × DEF × RES × independent multipliers.

Bonuses inside one multiplier add up; separate multipliers multiply.

| Multiplier | How it works |
| --- | --- |
| Skill multiplier × stat | Most skills scale with ATK; some scale with HP or DEF, and the skill text says so. ATK = (character base ATK + Arc base ATK) × (1 + ATK%) + flat ATK |
| DMG Bonus | 1 + every damage bonus that applies: general, attribute, skill type and so on |
| Crit | Every character starts with 5% Crit Rate and 50% Crit DMG. A critical hit multiplies damage by 1 + Crit DMG |
| DEF | (600 + 6 × attacker level) ÷ (target DEF + 600 + 6 × attacker level). DEF reduction on the enemy adds up; DEF ignore on the attacker multiplies with it |
| RES | 1 − resistance, for resistance from 0 to 60%. Resistance can go below 0: at −x%, damage is 1 + x ÷ (100 + x), so each further point gives less |
| Independent | Effects that multiply on their own: two 10% effects give 1.1 × 1.1 = 1.21, not 1.2 |

In Beyond the Rails an enemy's DEF is 540 + 6 × its level, so a level 80 character hitting a level 90 enemy keeps half its damage after the DEF multiplier. Example of the DEF rule: 20% DEF reduction and 30% DEF ignore leave 0.8 × 0.7 = 56% of the enemy's DEF.

Four characters carry the role tag "DoT" in the game data: [Adler](/characters/adler/), [Baicang](/characters/baicang/), [Lacrimosa](/characters/lacrimosa/) and [Zankou](/characters/zankou/). 零号攻略组 says only damage the game classes as DoT gains DoT bonuses such as [Sakiri](/characters/sakiri/)'s passive, and the role tag is the practical way to tell: a skill that hurts every second is not DoT by that alone.

零号攻略组 adds that RES reduction on the enemy and RES ignore on the attacker add up, and that the game does not mark which effects are independent multipliers. The NGA analysis adds that Mental damage ignores DEF, that most enemies outside Beyond the Rails have 600 + 6 × level DEF, and that resistance above 60% follows a different, steeper curve.

## Break

The white bar under an enemy's HP is its Break gauge. Each action removes a fixed amount from it, whatever damage the action deals. A Critical Riposte removes a large amount, and a Support Skill whose attribute matches the enemy's weakness removes more than other Support Skills. [Daffodill](/characters/daffodill/)'s Resonance stacks raise how much the attacker removes and [Adler](/characters/adler/)'s Scorch enhancement makes the enemy lose more; the two multiply.

When the gauge empties, the enemy cannot move or attack for a while and takes one hit of Break Damage. The gauge then refills; Break does not raise the damage the enemy takes.

Break Damage is worked out for each of the four party members and the results are added. Each member's share is:

Break Damage = level base × (1 + Break Intensity ÷ 300 + Break DMG bonus) × (enemy's Break gauge maximum ÷ 3) × DEF × RES

The level base grows with character level; 零号攻略组 gives 3,603 at level 80. Break DMG bonuses come from Daffodill's kit. Lowering an enemy's Break gauge maximum, as Daffodill's Discord enhancement does, makes Break come sooner but does not lower the gauge term in this formula. The NGA analysis adds that characters off the field contribute too, and defeated ones do not.

## Ultimate Energy

Most Ultimates cost 100 or 120 Ultimate Energy (game data 1.5.4). [Hotori](/characters/hotori/)'s Ultimate needs no Ultimate Energy and has no cooldown; [Shinku](/characters/shinku/)'s Ultimate spends Defiant Spirit instead.

| Cost | Characters |
| --- | --- |
| 100 | [Akane Rin](/characters/akane-rin/), [Blackbird](/characters/blackbird/), [Chaos](/characters/chaos/), [Chiz](/characters/chiz/), [Edgar](/characters/edgar/), [Esper Zero](/characters/zero/), [Hathor](/characters/hathor/), [Iroi](/characters/iroi/), [Jiuyuan](/characters/jiuyuan/), [Linko](/characters/linko/), [Mint](/characters/mint/), [Nanally](/characters/nanally/), [Skia](/characters/skia/) |
| 120 | [Adler](/characters/adler/), [Aurelia](/characters/aurelia/), [Baicang](/characters/baicang/), [Daffodill](/characters/daffodill/), [Fadia](/characters/fadia/), [Haniel](/characters/haniel/), [Lacrimosa](/characters/lacrimosa/), [Sakiri](/characters/sakiri/), [Zankou](/characters/zankou/) |

Of the characters with a cost, Cosmos, Anima and Lakshana characters cost 100; Incantation, Chaos and Psyche characters cost 120, except Blackbird at 100.

The NGA analysis gives how energy is shared: a hit fills 100% of its energy for the attacker and 60% for every other party member, whatever the party size, and both scale with Charge Efficiency. Energy from Charge and from Awakenings goes only to the character that triggers it and ignores Charge Efficiency.

## Co-op and Pink Paws Heist

| Situation | Rule, from the NGA analysis |
| --- | --- |
| Co-op with 1, 2, 3 or 4 players | Enemy HP ×1, ×1.75, ×2.5, ×3.25; enemy ATK ×1, ×1.2, ×1.4, ×1.6; Break gauge ×1, ×2, ×3, ×4 |
| Pink Paws Heist | The story balance mode is on: each hit deals a fixed amount set for that skill, so the character's stats do not change it. Effects that raise a skill's multiplier still do, and so do Hexed and Stain |
