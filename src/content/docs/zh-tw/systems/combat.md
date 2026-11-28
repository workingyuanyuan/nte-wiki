---
title: 戰鬥數值
description: 《異環》如何計算傷害、暴擊、傾陷與終結能量。
aliases:
  - Combat formulas
  - 战斗数值
  - 戦闘の計算式
  - 전투 공식
appliesTo: 1.5 版，遊戲資料 1.5.4
lastVerified: 2026-11-21
caveat: 傾陷不會讓敵人承受更高傷害，而是使敵人暫時無法行動並觸發一次傾陷傷害，由全隊四名角色共同計算。
sources:
  - title: nanoka.cc 遊戲資料 1.5.4，角色檔案（英文：基礎暴擊、終結能量消耗、角色標籤）
    url: https://static.nanoka.cc/nte/1.5.4/en/character/1003.json
  - title: nanoka.cc 遊戲資料 1.5.4，角色檔案（中文）
    url: https://static.nanoka.cc/nte/1.5.4/zh/character/1003.json
  - title: nanoka.cc 遊戲資料 1.5.4，角色檔案（日文：基礎暴擊、終結能量消耗、角色標籤）
    url: https://static.nanoka.cc/nte/1.5.4/ja/character/1003.json
  - title: nanoka.cc 遊戲資料 1.5.4，角色檔案（韓文：基礎暴擊、終結能量消耗、角色標籤）
    url: https://static.nanoka.cc/nte/1.5.4/ko/character/1003.json
  - title: 零号攻略组，傷害乘區解析影片，Bilibili（簡體中文，2026-06-21）
    url: https://www.bilibili.com/video/BV13ijt6gEF4/
  - title: NGA 論壇玩家分析：傷害與異能環合機制（簡體中文，2026-11-21 讀取）
    url: https://bbs.nga.cn/read.php?tid=46659382
  - title: GameWith 的傾陷值指南（英文）
    url: https://gamewith.net/nte/74130
  - title: 零号攻略组，環合結算機制影片，Bilibili（簡體中文，2026-06-25）
    url: https://www.bilibili.com/video/BV1E97868EJ7/
  - title: 叫我棉被、零號攻略組，殘虹攻略影片，Bilibili（簡體中文，2026-08-13）
    url: https://www.bilibili.com/video/BV1ksg76LETE/
  - title: 叫我棉被，娜娜莉攻略影片，Bilibili（簡體中文，2026-04-23）
    url: https://www.bilibili.com/video/BV1ybo8BPEpx/
  - title: 叫我棉被、零號攻略組，安魂曲攻略影片，Bilibili（簡體中文，2026-05-28）
    url: https://www.bilibili.com/video/BV1BNGS6KEXm/
  - title: 叫我棉被、零號攻略組，靈可攻略影片，Bilibili（簡體中文，2026-09-03）
    url: https://www.bilibili.com/video/BV19rtS6vEg7/
---

## 傷害

傷害 = 倍率 × 對應屬性 × 增傷區 × 暴擊區 × 防禦區 × 抗性區 × 獨立乘區。

同一乘區內的加成相加，不同乘區之間相乘。

| 乘區 | 計算方式 |
| --- | --- |
| 倍率 × 對應屬性 | 多數技能依攻擊力計算；部分依生命值或防禦力計算，技能說明會註明。攻擊力 = (角色基礎攻擊力 + 弧盤基礎攻擊力) × (1 + 攻擊力百分比) + 固定攻擊力 |
| 增傷區 | 1 + 所有適用的傷害加成：通用增傷、屬性增傷、技能類型增傷等 |
| 暴擊區 | 每名角色基礎暴擊率為 5%、基礎暴擊傷害為 50%。暴擊時傷害乘以 1 + 暴擊傷害 |
| 防禦區 | (600 + 6 × 攻擊者等級) ÷ (目標防禦力 + 600 + 6 × 攻擊者等級)。敵人身上的防禦力降低效果相加，再與攻擊者的無視防禦力相乘 |
| 抗性區 | 1 − 抗性，適用於 0 至 60% 的抗性。抗性可降至 0 以下：抗性為 −x% 時，傷害倍率為 1 + x ÷ (100 + x)，越往負值邊際效益越低 |
| 獨立乘區 | 各自獨立相乘的效果：兩個 10% 效果合計為 1.1 × 1.1 = 1.21，而非 1.2 |

在「軌外之境」中，敵人的防禦力為 540 + 6 × 敵人等級，因此 80 級角色攻擊 90 級敵人時，防禦區會讓傷害剩下一半。防禦力規則範例：20% 防禦力降低與 30% 無視防禦力疊加後，敵人剩餘 0.8 × 0.7 = 56% 防禦力。

遊戲資料中有四名角色帶有「持續傷害」角色標籤：[阿德勒](/zh-tw/characters/adler/)、[白藏](/zh-tw/characters/baicang/)、[安魂曲](/zh-tw/characters/lacrimosa/)與[殘虹](/zh-tw/characters/zankou/)。只有遊戲判定為持續傷害的傷害才能吃到持續傷害加成（例如[早霧](/zh-tw/characters/sakiri/)的被動），而角色標籤是實際辨別的依據：技能每秒造成傷害本身不代表它屬於持續傷害。[^1]

[^1]: [零号攻略组，傷害乘區解析影片，Bilibili（簡體中文，2026-06-21）](https://www.bilibili.com/video/BV13ijt6gEF4/)

敵人身上的抗性降低與攻擊者的無視抗性相加，且遊戲內未標註哪些效果屬於獨立乘區。[^1]心靈傷害無視防禦力，「軌外之境」以外多數敵人的防禦力為 600 + 6 × 敵人等級，抗性高於 60% 時則改用另一條更陡的曲線。[^2]心靈傷害不會無視抗性：敵人另有心靈抗性，通常與其他屬性抗性相同。[^3][法帝婭](/zh-tw/characters/fadia/)造成的心靈傷害可受傷害加成影響，通用增傷與心靈傷害加成皆然；黯星則不受影響，因為所有異能環合都不受傷害加成影響。

[^2]: [NGA 論壇玩家分析：傷害與異能環合機制（簡體中文，2026-11-21 讀取）](https://bbs.nga.cn/read.php?tid=46659382)
[^3]: [零号攻略组，環合結算機制影片，Bilibili（簡體中文，2026-06-25）](https://www.bilibili.com/video/BV1E97868EJ7/)

「濁燃」等持續傷害的暴擊率固定為 50%，再提高暴擊率也沒有收益。[^4]

[^4]: [叫我棉被、零號攻略組，殘虹攻略影片，Bilibili（簡體中文，2026-08-13），10:36](https://www.bilibili.com/video/BV1ksg76LETE/?t=636)

## 傾陷

敵人血條下方的白色條即為傾陷值。每次行動都會扣除固定數值的傾陷值，與該次行動造成的傷害無關。極限反擊能扣除大量傾陷值，屬性符合敵人弱點的援護技則比其他援護技扣除更多。[達芙蒂爾](/zh-tw/characters/daffodill/)的「同振」層數提高攻擊方扣除的量，[阿德勒](/zh-tw/characters/adler/)的「濁燃」強化讓敵人損失更多，兩者互相乘算。

傾陷值歸零時，敵人會暫時無法移動或攻擊，並承受一次傾陷傷害。隨後傾陷值重新填滿；傾陷不會提高敵人承受的傷害。

傾陷傷害會分別計算隊伍中四名角色各自的份額後相加。每名角色的份額為：

傾陷傷害 = 等級基礎值 × (1 + 傾陷強度 ÷ 300 + 傾陷傷害加成) × (敵人傾陷值上限 ÷ 3) × 防禦區 × 抗性區

等級基礎值隨角色等級成長，80 級時為 3,603。[^1]傾陷傷害加成來自達芙蒂爾的技能。降低敵人的傾陷值上限（例如達芙蒂爾的「失諧」強化）會讓傾陷更早觸發，但不會降低此公式中的傾陷值上限項。後台角色也會參與計算，已陣亡的角色則不會。[^2]

## 終結能量

多數角色的極軌終結消耗 100 或 120 點終結能量（遊戲資料 1.5.4）。[潯](/zh-tw/characters/hotori/)的極軌終結不需要終結能量，也沒有冷卻時間；[真紅](/zh-tw/characters/shinku/)的極軌終結改為消耗「桀驁鬥志」。

| 消耗 | 角色 |
| --- | --- |
| 100 | [明音凜](/zh-tw/characters/akane-rin/)、[黑羽](/zh-tw/characters/blackbird/)、[卡厄斯](/zh-tw/characters/chaos/)、[小吱](/zh-tw/characters/chiz/)、[埃德嘉](/zh-tw/characters/edgar/)、[異能者·零](/zh-tw/characters/zero/)、[哈索爾](/zh-tw/characters/hathor/)、[伊洛伊](/zh-tw/characters/iroi/)、[九原](/zh-tw/characters/jiuyuan/)、[靈可](/zh-tw/characters/linko/)、[薄荷](/zh-tw/characters/mint/)、[娜娜莉](/zh-tw/characters/nanally/)、[翳](/zh-tw/characters/skia/) |
| 120 | [阿德勒](/zh-tw/characters/adler/)、[海月](/zh-tw/characters/aurelia/)、[白藏](/zh-tw/characters/baicang/)、[達芙蒂爾](/zh-tw/characters/daffodill/)、[法帝婭](/zh-tw/characters/fadia/)、[哈尼婭](/zh-tw/characters/haniel/)、[安魂曲](/zh-tw/characters/lacrimosa/)、[早霧](/zh-tw/characters/sakiri/)、[殘虹](/zh-tw/characters/zankou/) |

有消耗的角色中，光、靈、相屬性角色消耗 100 點；咒、暗、魂屬性角色消耗 120 點，唯獨黑羽為 100 點。

每個動作有固定的基礎能量，不隨攻擊力、傷害或暴擊改變。命中時，攻擊者獲得其 100%，其餘每名隊友各獲得 60%，不論隊伍人數多寡。每名角色的充能效率只提高自己獲得的能量。來自「盈蓄」的能量只給予觸發效果的角色，且不受充能效率影響；覺醒給予的能量也是如此。[^2]

## 連線與粉爪大劫案

| 情境 | 規則[^2] |
| --- | --- |
| 1、2、3 或 4 人連線 | 敵人生命值 ×1、×1.75、×2.5、×3.25；敵人攻擊力 ×1、×1.2、×1.4、×1.6；傾陷值 ×1、×2、×3、×4 |
| 粉爪大劫案 | 開啟劇情平衡模式：每次命中造成該技能設定的固定傷害，角色數值不會影響傷害；提升技能倍率的效果以及「覆紋」與「浸染」仍會生效 |

## 極軌終結動畫

極軌終結動畫播放期間，敵人的行動、計時器、增益持續時間與技能冷卻都會停止；隊員已經打出的動作則照常打完，剛切到後台的角色也一樣。[^5][^6][^7]

[^5]: [叫我棉被，娜娜莉攻略影片，Bilibili（簡體中文，2026-04-23），12:36](https://www.bilibili.com/video/BV1ybo8BPEpx/?t=756)
[^6]: [叫我棉被、零號攻略組，安魂曲攻略影片，Bilibili（簡體中文，2026-05-28），1:35](https://www.bilibili.com/video/BV1BNGS6KEXm/?t=95)
[^7]: [叫我棉被、零號攻略組，靈可攻略影片，Bilibili（簡體中文，2026-09-03），15:11](https://www.bilibili.com/video/BV19rtS6vEg7/?t=911)
