---
title: Esper Cycles
description: Esper Cycles are reactions between adjacent attributes, triggered when the party switches characters.
aliases:
  - 異能環合
  - 异能环合
appliesTo: Version 1.5, game data 1.5.4
lastVerified: 2026-11-19
caveat: Charge and Discord are not set off by a switch of their own. They happen when a target already carries two reactions, Blossom on a target in Remora, or Nova and Scorch together.
sources:
  - title: Prydwen, Esper Cycles guide
    url: https://www.prydwen.gg/neverness-to-everness/guides/esper-cycles
  - title: mysqil (环世全鉴), Esper Cycles page in Simplified Chinese
    url: https://wiki.mysqil.com/esper-cycles
  - title: nanoka.cc game data 1.5.4, character files (passive texts in English)
    url: https://static.nanoka.cc/nte/1.5.4/en/character/1003.json
  - title: nanoka.cc game data 1.5.4, character files (passive texts in Chinese)
    url: https://static.nanoka.cc/nte/1.5.4/zh/character/1003.json
---

## The cycle

The six attributes sit on a ring in this order: Cosmos, Anima, Incantation, Chaos, Psyche, Lakshana, and back to Cosmos. Two neighbours on the ring make a two-attribute reaction. Charge and Discord combine three neighbours.

Prydwen describes the trigger: when the Cycle gauge is full and the player switches to a character whose attribute borders the one on the field, the incoming character's entry skill sets off the reaction. Esper Cycle damage scales with the Cycle Intensity of the characters who took part.

## Reactions

| Reaction | Attributes | Effect |
| --- | --- | --- |
| Blossom | Cosmos, Anima | A Vita Bud grows near the target and blooms 5 Vita Pistils; every 2 s a Pistil flies at a target in range and explodes for area damage. Up to 3 Vita Buds at once |
| Hexed | Anima, Incantation | For 12 s, Anima or Incantation damage taken by the target adds a follow-up attack worth 20% of that damage |
| Scorch | Incantation, Chaos | The target takes damage over time for 15 s |
| Nova | Chaos, Psyche | The target is in Nova for 5 s; when it ends, the target takes heavy Mental damage |
| Stain | Psyche, Lakshana | For 12 s the target takes 20% more Psyche and Lakshana damage |
| Remora | Lakshana, Cosmos | For 5 s the target moves and attacks more slowly, recovering over time; repeated Remora wears off faster |
| Charge | Lakshana, Cosmos, Anima | When Vita Pistils hit a target in Remora, the active character gains 10 extra Ultimate Energy |
| Discord | Incantation, Chaos, Psyche | A target in Nova and Scorch at the same time loses part of its Break gauge |

## Character enhancements

Every playable character has a passive that strengthens one or two reactions. The texts below are the in-game passive texts of game data 1.5.4.

| Reaction | Character | Enhancement |
| --- | --- | --- |
| Blossom | [Nanally](/characters/nanally/) | Fires 10 Vita Pistils with Vita Bud, reducing the interval between each shot to 1s. |
| Blossom | [Mint](/characters/mint/) | Expands Vita Pistils' damage area on hit. |
| Blossom | [Hotori](/characters/hotori/) | Prevents Vita Bud attacks from pausing during Time Stop. |
| Blossom | [Jiuyuan](/characters/jiuyuan/) | Spawns 1 additional Vita Bud and increases Vita Bud limit on field to 6. |
| Blossom | [Iroi](/characters/iroi/) | Generates a Vita Bud Copy when the current Vita Bud has existed for 3s. This copy cannot duplicate and does not count toward the Vita Bud limit. The copy produces 20 Copied Vita Pistils. Every 0.5s, one Copied Vita Pistil flies toward a target within range and explodes, dealing 37.5% of the original Vita Pistil's DMG. |
| Remora | [Skia](/characters/skia/) | Inflicts an additional Remora on a target when Fang Thrust locks onto them in Remora state. |
| Remora | [Hathor](/characters/hathor/) | Extends the target's Remora duration to 12s and increases Crit Rate by 10% when the whole team attack a target affected by Remora. |
| Remora | [Akane Rin](/characters/akane-rin/) | Grants Akane Rin an enhancement that lasts until she leaves combat after the team triggers Remora for the first time. Applies Remora to the target affected by Overtone and to all enemies within Reverb Field every 3s. Deals Lakshana DMG (counts as Redirect Skill DMG) equal to 150% of Akane Rin's ATK whenever the team reapplies Remora to an affected target. Increases this DMG by 20% for each 1s of Remora duration remaining on the target, up to 160%. Calculates each target's remaining Remora duration independently. Triggers this DMG no more than once per target every 1s. |
| Remora | [Chaos](/characters/chaos/) | Deals Lakshana DMG equal to 800% of ATK to the target when Remora ends, based on Remora's duration. Each second beyond the base 5s duration increases total DMG by 45%, up to 300%. Resets Remora's duration when reapplied. |
| Remora | [Elyms](/characters/elyms/) | Causes Elyms to reapply Remora to the same target after 7.5s whenever an ally applies Remora. Triggers at most once every 7s. Remora applied this way cannot trigger this effect again. |
| Charge | [Edgar](/characters/edgar/) | Grants 120 Ultimate Energy instantly when a character triggers Charge using a Support Skill. Disables Ultimate Energy gain from Vita Pistils when hitting Slowed targets afterward. Cooldown: 30s. |
| Charge | [Esper Zero](/characters/zero/) | Restores HP equal to 50% of Zero's Base ATK when the active character gains Ultimate Energy. |
| Charge | [Chiz](/characters/chiz/) | Grants active characters 4 additional Ultimate Energy. |
| Charge | [Shinku](/characters/shinku/) | Grants off-field characters the same amount of Charge when the active character gains Ultimate Energy. While Shinku is active and in Charge state, each trigger deals AoE DMG equal to 400% of ATK (scales with Basic Attack level, reaching 863.6% at level 11), and increases her ATK by 5% for 30s, up to 10 stacks. Cooldown: 1s. |
| Charge | [Elyms](/characters/elyms/) | Increases the whole team's Cosmos DMG by 3.75% for 30s whenever the active character gains Ultimate Energy, up to 8 stacks. Resets the duration when triggered again. |
| Hexed | [Linko](/characters/linko/) | Increases the base DMG of additional Follow-up Attacks from Hexed to 30% while Linko is on the team. Targets affected by Hexed take 10% more Follow-up Attack DMG. |
| Scorch | [Sakiri](/characters/sakiri/) | Increases DoT taken by the target by 25% for each type of DoT effect while in Scorch state, up to 100%. |
| Scorch | [Baicang](/characters/baicang/) | Inflicts another instance of Scorch with the same effect as the existing one when a Power Word is generated on a target affected by Scorch. |
| Scorch | [Adler](/characters/adler/) | Applies one of three random debuffs whenever Scorch is inflicted on a target: -20% ATK, -10% Esper Resistance, or +10% Break Efficiency, lasting for 15s. The same effect cannot stack. |
| Scorch | [Zankou](/characters/zankou/) | Scorch can be stacked up to 3 times. For each DoT effect allies inflict on a target afflicted with Scorch, Zankou inflicts 1 stack of Scorch on them, replacing the DMG, type, and duration of existing Scorch on the target with those of the newly inflicted effect. Scorch inflicted by this effect cannot trigger it again. |
| Nova | [Haniel](/characters/haniel/) | Allows all allies to drain ATK from the target when Nova ends. The target loses ATK equal to 4% of Haniel's Base ATK, and each ally gains ATK equal to 8% of Haniel's Base ATK. The total drain is capped at 16% of Haniel's Base ATK, and the target cannot lose more than 20% of their initial ATK. Restores both parties' stats upon exiting combat. |
| Nova | [Fadia](/characters/fadia/) | Allows all allies to drain Max HP from the target when Nova ends. The target loses Max HP equal to 200% of Fadia's base Max HP, and each ally gains Max HP equal to 10% of Fadia's base Max HP. Total drained cannot exceed 50% of Fadia's base Max HP. Restores both parties' stats upon exiting combat. |
| Nova | [Blackbird](/characters/blackbird/) | When Nova ends, deals additional Mental DMG equal to 20% of the actual total DMG taken by the target while Nova was active (excluding DMG dealt by the Support Skill that triggered Nova and by Nova itself), up to 1,000× Blackbird's Base ATK. This additional DMG is not affected by any other DMG Buffs or Debuffs. Inflicts Nova on the target once afterward. Prevents Nova inflicted by this effect from triggering the Nova reapplication effect again. |
| Nova | [Aurelia](/characters/aurelia/) | Deals 3 instances of Psyche DMG to the target after their Nova status ends, each equal to 50% of ATK. |
| Discord | [Lacrimosa](/characters/lacrimosa/) | Deals additional DMG equal to 400% of ATK to the target when Discord is triggered, if the target is already Broken. |
| Discord | [Daffodill](/characters/daffodill/) | Further reduces the target's Break cap by 10% for 30s while affected by Discord and restores it to normal upon leaving combat. Stacks Discord Enhancement effects up to a maximum reduction of 20% of the target's initial Break cap. |
| Stain | [Blackbird](/characters/blackbird/) | Increases Stain's base DMG Bonus to 30% and extends its duration to 20s. |
