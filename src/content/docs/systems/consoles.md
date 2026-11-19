---
title: 'Consoles: Cartridges and Modules'
description: The Console is the gear of a character, a Cartridge with a set effect and Modules on a grid.
aliases:
  - 空幕
appliesTo: Version 1.5, game data 1.5.4
lastVerified: 2026-11-19
caveat: A Cartridge's set effect counts only Modules of the shapes that Cartridge asks for; four Modules of other shapes do not activate it.
sources:
  - title: nanoka.cc game data 1.5.4, Console file in English
    url: https://static.nanoka.cc/nte/1.5.4/en/console.json
  - title: nanoka.cc game data 1.5.4, Console file in Chinese
    url: https://static.nanoka.cc/nte/1.5.4/zh/console.json
  - title: Prydwen, Modules and Cartridges guide
    url: https://www.prydwen.gg/neverness-to-everness/guides/modules-generic
  - title: Prydwen, Cartridge sets
    url: https://www.prydwen.gg/neverness-to-everness/guides/modules-cartridge
  - title: mysqil (环世全鉴), Cartridges page in Simplified Chinese
    url: https://wiki.mysqil.com/cassettes
  - title: mysqil (环世全鉴), Modules page in Simplified Chinese
    url: https://wiki.mysqil.com/drivers
---

## How it works

| Part | What it does |
| --- | --- |
| Console | A grid board on each character; its layout and bonus differ per character |
| Cartridge | Sets the set effect; carries one main stat and four sub stats, rolled when it drops |
| Module | Fills the grid; one main stat and up to four sub stats. Sorted by type (cells taken) and shape |
| Set effect | 2 and 4 Modules of the shapes the Cartridge lists activate its 2-piece and 4-piece effects |
| Character bonus | Each character gains a stat for every Module of one type, listed below |

## Where they come from

| Item | Source |
| --- | --- |
| Cartridges | Rabbit Hole Anomaly Zone |
| Modules | Rewind on the Console page, paid with Carrota from the Rabbit Hole: Bronze Carrota for Easy, Silver for Normal, Gold for Hard Rewinds |
| Module upgrades | Manhole Thug, Manhole Crook and Manhole Boss, from the Rabbit Hole |
| Extra Modules | The Anomaly Furniture "Hamster Ball" in four [properties](/systems/properties/) |

## Module types

There are 12 Module shapes. Each comes in blue, purple and gold rarity.

| Module type | Cells | Shapes |
| --- | --- | --- |
| Type II | 2 | Horizontal, vertical |
| Type III | 3 | Horizontal, vertical, four L shapes |
| Type IV | 4 | Horizontal, vertical, two Z shapes |

## Cartridge sets

Six sets add damage of one attribute; six serve any character.

| Cartridge | 2 Modules | 4 Modules | Module shapes of the set |
| --- | --- | --- | --- |
| Lost Radiance | Cosmos DMG +10%. | Ignores 25% of enemies' DEF for 20s after the wearer casts Ultimate. Effect does not stack. | II horizontal, III L ×2, IV vertical |
| Diabolos | Chaos DMG +10%. | Ignores 12% of enemies' Chaos Resistance. Ignores 24% of enemies' Chaos Resistance for 20s after the wearer participates in Nova or Scorch reactions. | II vertical, III L ×2, IV horizontal |
| Fireflies and the Forest | Anima DMG +10%. | Increases wearer's CRIT DMG by 8% when a nearby enemy takes Anima DMG from the Team, up to 7 stacks. Each stack lasts 10s. Effect remains active when the character is off-field. | II horizontal, III vertical, III L, IV Z |
| Crimson: Twin Butterflies | Incantation DMG +10%. | Increases wearer's ATK by 6% when a nearby enemy takes Incantation DMG from the Team, up to 6 stacks. Each stack lasts 10s. Effect remains active when the character is off-field. | II vertical, III horizontal, III L, IV Z |
| Devil's Blood: Curse | Psyche DMG +10%. | Increases the wearer's DMG by 18%. The bonus becomes 36% against units affected by Nova or Stain. | II vertical, III vertical, III L, IV Z |
| Street Boxer | Lakshana DMG +10%. | Increases Crit Chance by 14%. After the team triggers Remora or Stain, increases Crit Chance by an extra 14% for 20s. | II horizontal, III horizontal, III L, IV Z |
| Kingdom's Guard | DEF +15%. | Increases wearer's shields by 20%. | III horizontal, III vertical, III L ×2 |
| Shadow Creed | ATK +10%. | Increases wearer's ATK by 25% for 20s after casting a Skill. | II horizontal, II vertical, IV horizontal, IV Z |
| Thea's Night Tavern | HP +10%. | Increases wearer's Healing Bonus by 20%. | III horizontal, III vertical, III L ×2 |
| Tiny Big Adventure | HP +10%. | Increases wearer's Max HP by 4% when taking damage, up to 10 stacks. Each stack lasts 10s. Casting Ultimate instantly grants 10 stacks. | II horizontal, II vertical, IV horizontal, IV Z |
| Speedy Hedgehog | Charge Efficiency +12%. | Increases all allies' ATK by 15% for 20s after the wearer casts Ultimate. Effect does not stack. | III L ×4 |
| Quiet Manor | Mental DMG +10%. | Grants wearer a 12% Mental DMG Bonus per Basic Attack, up to 3 stacks. Each stack lasts 6s. | II horizontal, II vertical, IV vertical, IV Z |

## Module type bonus per character

| Character | Module type | Bonus per Module of that type |
| --- | --- | --- |
| [Adler](/characters/adler/) | Type III | DEF Bonus +12% |
| [Akane Rin](/characters/akane-rin/) | Type III | ATK Bonus +10% |
| [Aurelia](/characters/aurelia/) | Type III | ATK Bonus +10% |
| [Baicang](/characters/baicang/) | Type III | CRIT Rate +7.5% |
| [Blackbird](/characters/blackbird/) | Type III | CRIT Rate +8% |
| [Chaos](/characters/chaos/) | Type III | CRIT DMG +16% |
| [Chiz](/characters/chiz/) | Type III | Cosmos DMG Bonus +10% |
| [Daffodill](/characters/daffodill/) | Type III | Chaos DMG Bonus +10% |
| [Edgar](/characters/edgar/) | Type III | HP Bonus +10% |
| [Elyms](/characters/elyms/) | Type III | CRIT Rate +8% |
| [Fadia](/characters/fadia/) | Type II | HP Bonus +6% |
| [Haniel](/characters/haniel/) | Type III | ATK Bonus +10% |
| [Hathor](/characters/hathor/) | Type III | ATK Bonus +10% |
| [Hotori](/characters/hotori/) | Type III | Cosmos DMG Bonus +10% |
| [Iroi](/characters/iroi/) | Type III | ATK Bonus +10% |
| [Jiuyuan](/characters/jiuyuan/) | Type II | CRIT Rate +6% |
| [Lacrimosa](/characters/lacrimosa/) | Type III | Chaos DMG Bonus +10% |
| [Linko](/characters/linko/) | Type III | CRIT Rate +8% |
| [Mint](/characters/mint/) | Type III | CRIT Rate +7.5% |
| [Nanally](/characters/nanally/) | Type II | CRIT Rate +6% |
| [Sakiri](/characters/sakiri/) | Type III | Incantation DMG Bonus +9% |
| [Shinku](/characters/shinku/) | Type III | CRIT DMG +16% |
| [Skia](/characters/skia/) | Type III | ATK Bonus +10% |
| [Zankou](/characters/zankou/) | Type III | CRIT DMG +16% |
| [Esper Zero](/characters/zero/) | Type III | ATK Bonus +10% |
