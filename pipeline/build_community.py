"""Write the community section (社群攻略, /community/) in every language from records/community/.

  python3 pipeline/build_community.py
  python3 pipeline/build_community.py --check draft.json   # validate draft claims, write nothing

Pages: community/index, community/teams, community/builds, in en, zh-tw, zh-cn, ja and ko. Run it
after scripts/to-zh-cn.py, which leaves community/ alone: this script writes zh-cn itself, with the
game's Simplified names.

records/community/sources.json holds one record per guide video; records/community/claims.json one
record per team and per character card of a guide's summary picture (一图流), with the id of the
creator's comment under the video that carries the picture (`reply`) or the second of the video
(`at`). A claim keeps the creator's own text in Simplified Chinese (arcs, stats, skill order, with the
creator's operators > ≈ = ≥ /), and every name in it must resolve here against the site's records:
characters against the character pages, Arcs against records/arcs.json, cartridge sets and Exe
(no page yet) against records/community/names.json. An unknown name stops the build.

The site never merges or ranks: each card is shown as its source gives it, and rows follow the
order of the character list. Cards that two videos of one creator give identically share a column.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'src', 'content', 'docs')
REC = os.path.join(ROOT, 'records')
LANGS = ['en', 'zh-tw', 'zh-cn', 'ja', 'ko']
PREFIX = {'en': '', 'zh-tw': 'zh-tw/', 'zh-cn': 'zh-cn/', 'ja': 'ja/', 'ko': 'ko/'}
ZH = ('zh-tw', 'zh-cn', 'ja')  # languages written without spaces around the joiners

# ---------------------------------------------------------------- vocabulary

ELEMENTS = {  # the creator's element word -> the game's words for "<element> DMG" (cartridge 2-piece text)
    '光': {'en': 'Cosmos DMG', 'zh-tw': '光屬性異能傷害', 'zh-cn': '光属性异能伤害', 'ja': '光異能ダメージ', 'ko': '빛속성 이능력 피해'},
    '暗': {'en': 'Chaos DMG', 'zh-tw': '暗屬性異能傷害', 'zh-cn': '暗属性异能伤害', 'ja': '闇異能ダメージ', 'ko': '암속성 이능력 피해'},
    '咒': {'en': 'Incantation DMG', 'zh-tw': '咒屬性異能傷害', 'zh-cn': '咒属性异能伤害', 'ja': '呪異能ダメージ', 'ko': '주속성 이능력 피해'},
    '相': {'en': 'Lakshana DMG', 'zh-tw': '相屬性異能傷害', 'zh-cn': '相属性异能伤害', 'ja': '相異能ダメージ', 'ko': '상속성 이능력 피해'},
    '灵': {'en': 'Anima DMG', 'zh-tw': '靈屬性異能傷害', 'zh-cn': '灵属性异能伤害', 'ja': '霊異能ダメージ', 'ko': '령속성 이능력 피해'},
    '魂': {'en': 'Psyche DMG', 'zh-tw': '魂屬性異能傷害', 'zh-cn': '魂属性异能伤害', 'ja': '魂異能ダメージ', 'ko': '혼속성 이능력 피해'},
}
STATS = {  # the game's stat names (nanoka.cc 1.5.4 id_stats names; the site's pages for the rest)
    'crit': {'en': 'CRIT Rate', 'zh-tw': '暴擊率', 'zh-cn': '暴击率', 'ja': 'クリティカル率', 'ko': '치명 확률'},
    'critdmg': {'en': 'CRIT DMG', 'zh-tw': '暴擊傷害', 'zh-cn': '暴击伤害', 'ja': 'クリティカルダメージ', 'ko': '치명 피해'},
    'both': {'en': 'CRIT Rate and CRIT DMG', 'zh-tw': '暴擊率與暴擊傷害', 'zh-cn': '暴击率与暴击伤害', 'ja': 'クリティカル率とクリティカルダメージ', 'ko': '치명 확률과 치명 피해'},
    'atk_pct': {'en': 'ATK Bonus', 'zh-tw': '攻擊力百分比', 'zh-cn': '攻击力百分比', 'ja': '攻撃力％', 'ko': '공격력%'},
    'def': {'en': 'DEF', 'zh-tw': '防禦力', 'zh-cn': '防御力', 'ja': '防御力', 'ko': '방어력'},
    'hp': {'en': 'HP', 'zh-tw': '生命值', 'zh-cn': '生命值', 'ja': 'HP', 'ko': 'HP'},
    'atk': {'en': 'ATK', 'zh-tw': '攻擊力', 'zh-cn': '攻击力', 'ja': '攻撃力', 'ko': '공격력'},
    'cycle': {'en': 'Cycle Intensity', 'zh-tw': '環合強度', 'zh-cn': '环合强度', 'ja': '連環パワー', 'ko': '사이클 강도'},
    'break': {'en': 'Break Intensity', 'zh-tw': '傾陷強度', 'zh-cn': '倾陷强度', 'ja': 'ブレイクパワー', 'ko': '붕괴 강도'},
    # The guides' word for the bonus to the character's own element, element not named.
    'dmg_elem': {'en': 'element DMG bonus', 'zh-tw': '屬性增傷', 'zh-cn': '属性增伤', 'ja': '属性ダメージアップ', 'ko': '속성 피해 증가'},
    'heal': {'en': 'Healing Bonus', 'zh-tw': '治療效率', 'zh-cn': '治疗效率', 'ja': '治療効率', 'ko': '치료 효율'},
    # Not a stat of the game: the guides' word for every bonus to damage dealt.
    'dmg_all': {'en': 'DMG bonus of any kind', 'zh-tw': '通用增傷', 'zh-cn': '通用增伤', 'ja': '汎用のダメージアップ', 'ko': '범용 피해 증가'},
    'rest': {'en': 'the others', 'zh-tw': '其他', 'zh-cn': '其他', 'ja': 'その他', 'ko': '나머지'},
    'any': {'en': 'any', 'zh-tw': '任意', 'zh-cn': '任意', 'ja': '任意', 'ko': '무관'},
}
STAT_WORDS = {  # the guides' words -> STATS keys
    '暴击': 'crit', '暴击率': 'crit', '暴伤': 'critdmg', '爆伤': 'critdmg', '暴击伤害': 'critdmg', '双暴': 'both', '双爆': 'both', '其他': 'rest',
    '攻击力%': 'atk_pct', '百分比攻击力': 'atk_pct', '攻击%': 'atk_pct', '攻击力百分比': 'atk_pct', '攻击力': 'atk',
    '环合强度': 'cycle', '环和强度': 'cycle', '治疗加成': 'heal', '倾陷强度': 'break', '属性增伤': 'dmg_elem', '固定攻击': 'atk', '防御力': 'def', '生命': 'hp', '治疗效率': 'heal',
    '通用增伤': 'dmg_all', '增伤': 'dmg_all', '伤害增加': 'dmg_all', '任意': 'any',
}
SLOTS = {  # the guides' words for the four skill slots -> the slot labels of the character pages
    'basic': {'en': 'Basic Attack', 'zh-tw': '普通攻擊', 'zh-cn': '普通攻击', 'ja': '通常攻撃', 'ko': '일반 공격'},
    'skill': {'en': 'Skill', 'zh-tw': '技能', 'zh-cn': '技能', 'ja': 'バイレールスキル', 'ko': '바이레일 스킬'},
    'ult': {'en': 'Ultimate', 'zh-tw': '極軌終結', 'zh-cn': '极轨终结', 'ja': 'EXレール終結', 'ko': '울티메이트'},
    'rest': {'en': 'the others', 'zh-tw': '其他', 'zh-cn': '其他', 'ja': 'その他', 'ko': '나머지'},
    'support': {'en': 'Support Skill', 'zh-tw': '支援技能', 'zh-cn': '支援技能', 'ja': 'サポートスキル', 'ko': '서포트 스킬'},
}
SLOT_WORDS = {'普攻': 'basic', '技能': 'skill', '小技能': 'skill', '大招': 'ult', '援护技': 'support', '援护攻击': 'support', '其他': 'rest'}
CONDITIONS = {  # the guides' conditions on a skill order: with or without swap combos (合轴)
    '不合轴': {'en': 'without swap combos', 'zh-tw': '不合軸', 'zh-cn': '不合轴', 'ja': '合軸なし', 'ko': '합축 미사용'},
    '合轴': {'en': 'with swap combos', 'zh-tw': '合軸', 'zh-cn': '合轴', 'ja': '合軸あり', 'ko': '합축 사용'},
}
LABELS = {  # team names that are not an Esper Cycle or a character's main or sub-DPS team
    '盈蓄大招队': {'en': 'Charge Ultimate team', 'zh-tw': '盈蓄大招隊', 'zh-cn': '盈蓄大招队', 'ja': '充蓄必殺チーム', 'ko': '차지 울티메이트 파티'},
    '低配版盈蓄大招队': {'en': 'Charge Ultimate team, budget version', 'zh-tw': '低配版盈蓄大招隊', 'zh-cn': '低配版盈蓄大招队', 'ja': '充蓄必殺チーム（低コスト版）', 'ko': '차지 울티메이트 파티(저비용판)'},
    '延滞环合队': {'en': 'Remora Cycle team', 'zh-tw': '延滯環合隊', 'zh-cn': '延滞环合队', 'ja': '延滞連環チーム', 'ko': '레모라 사이클 파티'},
    '高上限爆发': {'en': 'High-ceiling burst team', 'zh-tw': '高上限爆發隊', 'zh-cn': '高上限爆发队', 'ja': '高上限バーストチーム', 'ko': '고점 버스트 파티'},
    '通用直伤队': {'en': 'General direct-damage team', 'zh-tw': '通用直傷隊', 'zh-cn': '通用直伤队', 'ja': '汎用直撃ダメージチーム', 'ko': '범용 직접 피해 파티'},
    '即插即用队': {'en': 'Plug-and-play team', 'zh-tw': '即插即用隊', 'zh-cn': '即插即用队', 'ja': 'プラグアンドプレイ編成', 'ko': '플러그 앤 플레이 파티'},
}
CYCLES = {  # Esper Cycle names as the site's esper-cycles page writes them
    '创生': {'en': 'Blossom', 'zh-tw': '創生', 'zh-cn': '创生', 'ja': '創生', 'ko': '블라썸'},
    '覆纹': {'en': 'Hexed', 'zh-tw': '覆紋', 'zh-cn': '覆纹', 'ja': '覆紋', 'ko': '헥스'},
    '浊燃': {'en': 'Scorch', 'zh-tw': '濁燃', 'zh-cn': '浊燃', 'ja': '濁燃', 'ko': '스코치'},
    '黯星': {'en': 'Nova', 'zh-tw': '黯星', 'zh-cn': '黯星', 'ja': '暗星', 'ko': '노바'},
    '浸染': {'en': 'Stain', 'zh-tw': '浸染', 'zh-cn': '浸染', 'ja': '浸染', 'ko': '스테인'},
    '延滞': {'en': 'Remora', 'zh-tw': '延滯', 'zh-cn': '延滞', 'ja': '延滞', 'ko': '레모라'},
    '盈蓄': {'en': 'Charge', 'zh-tw': '盈蓄', 'zh-cn': '盈蓄', 'ja': '充蓄', 'ko': '차지'},
}
ROLES = {
    '主力输出': {'en': 'Main DPS', 'zh-tw': '主力輸出', 'zh-cn': '主力输出', 'ja': 'メインアタッカー', 'ko': '메인 딜러'},
    '爆发输出': {'en': 'Burst DPS', 'zh-tw': '爆發輸出', 'zh-cn': '爆发输出', 'ja': 'バーストアタッカー', 'ko': '버스트 딜러'},
    '主C': {'en': 'Main DPS', 'zh-tw': '主力輸出', 'zh-cn': '主力输出', 'ja': 'メインアタッカー', 'ko': '메인 딜러'},
    '副C': {'en': 'Sub-DPS', 'zh-tw': '副輸出', 'zh-cn': '副输出', 'ja': 'サブアタッカー', 'ko': '서브 딜러'},
    '输出': {'en': 'DPS', 'zh-tw': '輸出', 'zh-cn': '输出', 'ja': 'アタッカー', 'ko': '딜러'},
    '辅助玩法': {'en': 'Support build', 'zh-tw': '輔助玩法', 'zh-cn': '辅助玩法', 'ja': 'サポート型', 'ko': '서포터형'},
    '输出玩法': {'en': 'DPS build', 'zh-tw': '輸出玩法', 'zh-cn': '输出玩法', 'ja': 'アタッカー型', 'ko': '딜러형'},
    '?': {'en': '—', 'zh-tw': '—', 'zh-cn': '—', 'ja': '—', 'ko': '—'},  # covered on the source
    '回血': {'en': 'Healer', 'zh-tw': '回血', 'zh-cn': '回血', 'ja': '回復', 'ko': '회복'},
    '分摊伤害': {'en': 'Damage share', 'zh-tw': '分攤傷害', 'zh-cn': '分摊伤害', 'ja': 'ダメージ分担', 'ko': '피해 분담'},
    '护盾': {'en': 'Shield', 'zh-tw': '護盾', 'zh-cn': '护盾', 'ja': 'シールド', 'ko': '보호막'},
    '辅助': {'en': 'Support', 'zh-tw': '輔助', 'zh-cn': '辅助', 'ja': 'サポート', 'ko': '서포터'},
}

T = {
    'en': dict(
        section='Community guides', teams='Teams', builds='Character builds', topic='Topic', holds='What it holds',
        creator='Creator', video='Video', published='Published', server='Server', version='Version', covers='Characters',
        source='Source', team='Team', members='Members', note='Note',
        role='Role', arcs='Arcs', cart='Cartridge set', cart_main='Cartridge main stat', sub='Sub-stats', talents='Passives',
        skills='Skill levels', in_team='Team', passive='Passive {n}', any_one=' or ', sep=', ', and_=' and ',
        guide='{name} guide', cn='CN server',
        team_of='{name} team', main_team='{name} as main DPS', sub_team='{name} as sub-DPS {n}', cycle_team='{cycle} team',
        idx_title='Community guides', idx_desc='NTE player guides: teams and builds for {n} characters from {v} Bilibili guide videos.',
        idx_caveat='Every team and build is a named creator\'s recommendation for the version and server the creator played, not game data.',
        teams_desc='NTE teams that Bilibili guide creators recommend for {n} characters.',
        teams_caveat='In a team, characters joined by "or" fill one slot: any one of them.',
        builds_desc='NTE character builds from Bilibili guides: Arcs, cartridge sets, stats and skill order for {n} characters.',
        builds_caveat='Operators are the creator\'s: > ranks before, ≈ and = rank about equal, / means either; Arcs listed with commas are not ranked.',
        applies='{versions}, {server}; {n} Bilibili video{s} ({first} to {last}, read {read})',
        applies1='{versions}, {server}; {n} Bilibili video{s} (published {first}, read {read})',
        teams_row='[{creator}]({url})', idx_teams='Teams that {creators} recommend for {n} characters',
        idx_builds='Arcs, cartridge sets, main stats, sub-stats, passives and skill order for {n} characters',
        src_title='{title} (Bilibili, {creator}, {date})'),
    'zh-tw': dict(
        section='社群攻略', teams='配隊', builds='角色養成', topic='主題', holds='內容',
        creator='創作者', video='影片', published='發布日期', server='伺服器', version='遊戲版本', covers='角色',
        source='來源', team='隊伍', members='成員', note='備註',
        role='定位', arcs='弧盤', cart='卡帶套裝', cart_main='卡帶主詞條', sub='副詞條', talents='被動技能',
        skills='技能升級', in_team='所在隊伍', passive='被動 {n}', any_one='或', sep='、', and_='與',
        guide='{name}攻略', cn='國服',
        team_of='{name}隊', main_team='{name}主輸出隊', sub_team='{name}副輸出隊 {n}', cycle_team='{cycle}隊',
        idx_title='社群攻略', idx_desc='《異環》玩家攻略：{v} 部 Bilibili 攻略影片為 {n} 名角色排的配隊與養成。',
        idx_caveat='每支隊伍與每份養成都是具名創作者對其所玩版本與伺服器的推薦，不是遊戲資料。',
        teams_desc='《異環》Bilibili 攻略創作者為 {n} 名角色推薦的配隊。',
        teams_caveat='隊伍中以「或」相連的角色只需其中一名。',
        builds_desc='《異環》Bilibili 攻略的角色養成：{n} 名角色的弧盤、卡帶、詞條與技能升級順序。',
        builds_caveat='符號照創作者的寫法：> 表示優先，≈ 與 = 表示相近，/ 表示擇一；以頓號並列的弧盤不分先後。',
        applies='{versions}，{server}；{n} 部 Bilibili 影片（{first} 至 {last} 發布，{read} 讀取）',
        applies1='{versions}，{server}；{n} 部 Bilibili 影片（{first} 發布，{read} 讀取）',
        idx_teams='{creators}為 {n} 名角色推薦的隊伍',
        idx_builds='{n} 名角色的弧盤、卡帶套裝、主詞條、副詞條、被動技能與技能升級順序',
        src_title='{title}（Bilibili，{creator}，{date}）'),
    'zh-cn': dict(
        section='社群攻略', teams='配队', builds='角色养成', topic='主题', holds='内容',
        creator='创作者', video='视频', published='发布日期', server='服务器', version='游戏版本', covers='角色',
        source='来源', team='队伍', members='成员', note='备注',
        role='定位', arcs='弧盘', cart='卡带套装', cart_main='卡带主词条', sub='副词条', talents='被动技能',
        skills='技能升级', in_team='所在队伍', passive='被动 {n}', any_one='或', sep='、', and_='与',
        guide='{name}攻略', cn='国服',
        team_of='{name}队', main_team='{name}主输出队', sub_team='{name}副输出队 {n}', cycle_team='{cycle}队',
        idx_title='社群攻略', idx_desc='《异环》玩家攻略：{v} 部 Bilibili 攻略视频为 {n} 名角色排的配队与养成。',
        idx_caveat='每支队伍与每份养成都是具名创作者对其所玩版本与服务器的推荐，不是游戏数据。',
        teams_desc='《异环》Bilibili 攻略创作者为 {n} 名角色推荐的配队。',
        teams_caveat='队伍中以「或」相连的角色只需其中一名。',
        builds_desc='《异环》Bilibili 攻略的角色养成：{n} 名角色的弧盘、卡带、词条与技能升级顺序。',
        builds_caveat='符号照创作者的写法：> 表示优先，≈ 与 = 表示相近，/ 表示择一；以顿号并列的弧盘不分先后。',
        applies='{versions}，{server}；{n} 部 Bilibili 视频（{first} 至 {last} 发布，{read} 读取）',
        applies1='{versions}，{server}；{n} 部 Bilibili 视频（{first} 发布，{read} 读取）',
        idx_teams='{creators}为 {n} 名角色推荐的队伍',
        idx_builds='{n} 名角色的弧盘、卡带套装、主词条、副词条、被动技能与技能升级顺序',
        src_title='{title}（Bilibili，{creator}，{date}）'),
    'ja': dict(
        section='コミュニティ攻略', teams='編成', builds='キャラクター育成', topic='項目', holds='内容',
        creator='投稿者', video='動画', published='投稿日', server='サーバー', version='ゲームバージョン', covers='キャラクター',
        source='出典', team='チーム', members='メンバー', note='注記',
        role='役割', arcs='弧盤', cart='カートリッジセット', cart_main='カートリッジのメインステータス', sub='サブステータス', talents='パッシブ',
        skills='スキルレベル', in_team='チーム', passive='パッシブ {n}', any_one='または', sep='、', and_='と',
        guide='{name}攻略', cn='中国サーバー',
        team_of='{name}チーム', main_team='{name}メインアタッカー編成', sub_team='{name}サブアタッカー編成 {n}', cycle_team='{cycle}チーム',
        idx_title='コミュニティ攻略', idx_desc='NTE（異環）のプレイヤー攻略：Bilibili の攻略動画 {v} 本による {n} キャラクターの編成と育成。',
        idx_caveat='どの編成と育成も、名前のある投稿者がプレイしたバージョンとサーバーでの推奨であり、ゲームデータではない。',
        teams_desc='NTE（異環）の Bilibili 攻略投稿者が {n} キャラクターに推奨する編成。',
        teams_caveat='チームで「または」でつないだキャラクターは、どれか一人でよい。',
        builds_desc='NTE（異環）の Bilibili 攻略によるキャラクター育成：{n} キャラクターの弧盤、カートリッジ、ステータス、スキル順。',
        builds_caveat='記号は投稿者の書き方のまま：> は優先、≈ と = はほぼ同等、/ はいずれか。読点で並べた弧盤は順位なし。',
        applies='{versions}、{server}；Bilibili の動画 {n} 本（{first}〜{last} 投稿、{read} 確認）',
        applies1='{versions}、{server}；Bilibili の動画 {n} 本（{first} 投稿、{read} 確認）',
        idx_teams='{creators}が {n} キャラクターに推奨するチーム',
        idx_builds='{n} キャラクターの弧盤、カートリッジセット、メインステータス、サブステータス、パッシブ、スキル順',
        src_title='{title}（Bilibili、{creator}、{date}）'),
    'ko': dict(
        section='커뮤니티 공략', teams='파티 구성', builds='캐릭터 육성', topic='항목', holds='내용',
        creator='제작자', video='영상', published='게시일', server='서버', version='게임 버전', covers='캐릭터',
        source='출처', team='파티', members='멤버', note='비고',
        role='역할', arcs='아크', cart='카트리지 세트', cart_main='카트리지 주 능력치', sub='부 능력치', talents='패시브',
        skills='스킬 레벨', in_team='파티', passive='패시브 {n}', any_one=' 또는 ', sep=', ', and_='와 ',
        guide='{name} 공략', cn='중국 서버',
        team_of='{name} 파티', main_team='{name} 메인 딜러 파티', sub_team='{name} 서브 딜러 파티 {n}', cycle_team='{cycle} 파티',
        idx_title='커뮤니티 공략', idx_desc='이환(NTE) 플레이어 공략: Bilibili 공략 영상 {v}편이 정리한 캐릭터 {n}명의 파티 구성과 육성.',
        idx_caveat='모든 파티와 육성은 이름이 밝혀진 제작자가 자신이 플레이한 버전과 서버에서 추천한 것이며 게임 데이터가 아니다.',
        teams_desc='이환(NTE) Bilibili 공략 제작자가 캐릭터 {n}명에게 추천하는 파티 구성.',
        teams_caveat='파티에서 「또는」으로 이은 캐릭터는 그중 한 명만 있으면 된다.',
        builds_desc='이환(NTE) Bilibili 공략의 캐릭터 육성: 캐릭터 {n}명의 아크, 카트리지, 능력치, 스킬 순서.',
        builds_caveat='기호는 제작자의 표기 그대로: > 는 우선, ≈ 와 = 는 비슷함, / 는 둘 중 하나. 쉼표로 나열한 아크는 순서가 없다.',
        applies='{versions}, {server}; Bilibili 영상 {n}편({first}~{last} 게시, {read} 확인)',
        applies1='{versions}, {server}; Bilibili 영상 {n}편({first} 게시, {read} 확인)',
        idx_teams='{creators}이(가) 캐릭터 {n}명에게 추천한 파티',
        idx_builds='캐릭터 {n}명의 아크, 카트리지 세트, 주 능력치, 부 능력치, 패시브, 스킬 순서',
        src_title='{title} (Bilibili, {creator}, {date})'),
}
# Title and aliases name the same set of strings in every language: every language's title plus these.
EXTRA_ALIASES = {
    'idx_title': ['NTE guides', '異環攻略', '异环攻略'],
    'teams': ['NTE teams', '異環配隊', '异环配队'],
    'builds': ['NTE builds', '異環養成', '异环养成'],
}


def aliases(kind, lang):
    return [x for x in dict.fromkeys([T[l][kind] for l in LANGS] + EXTRA_ALIASES[kind]) if x != T[lang][kind]]


VERSION_WORD = {'en': 'Version {v}', 'zh-tw': '{v} 版', 'zh-cn': '{v} 版', 'ja': 'バージョン {v}', 'ko': '{v} 버전'}
CREATORS = {  # creators' names, as their channels write them; zh-tw converts the characters only
    '叫我棉被': {'zh-tw': '叫我棉被'},
    '零号攻略组': {'zh-tw': '零號攻略組'},
}


def creator(name, lang):
    return CREATORS.get(name, {}).get(lang, name)


# ---------------------------------------------------------------- names

def load(rel):
    return json.load(open(os.path.join(REC, rel), encoding='utf-8'))


def page_title(path):
    for line in open(path, encoding='utf-8'):
        if line.startswith('title: '):
            return line[7:].strip().strip('\'"')
    raise SystemExit(f'no title in {path}')


def passives(path):
    """The two passive names from a character page's skill table (rows 'Passive 1', 'Passive 2')."""
    out = {}
    for line in open(path, encoding='utf-8'):
        m = re.match(r'\| (?:Passive|被動|被动|パッシブ|패시브) ([12]) \| ([^|]+) \|', line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def character_names():
    """slug -> {lang: {name, passives, page}} for every character page, plus the extra names."""
    chars = {}
    order = []
    for line in open(os.path.join(DOCS, 'characters', 'index.md'), encoding='utf-8'):
        m = re.match(r'\| \[[^\]]+\]\(/characters/([a-z0-9-]+)/\)', line)
        if m:
            order.append(m.group(1))
    for slug in order + sorted(s[:-3] for s in os.listdir(os.path.join(DOCS, 'characters')) if s.endswith('.md')):
        if slug in chars or slug in ('index', 'archives', 'voices'):
            continue
        chars[slug] = {}
        for lang in LANGS:
            p = os.path.join(DOCS, PREFIX[lang] + 'characters', slug + '.md')
            chars[slug][lang] = {'name': page_title(p), 'passives': passives(p), 'page': True, 'awakenings': awakenings(p, lang)}
    for slug, rec in load('community/names.json')['characters'].items():
        chars[slug] = {lang: {'name': rec['name'][lang], 'passives': {int(k): v[lang] for k, v in rec['passives'].items()}, 'page': False, 'awakenings': []} for lang in LANGS}
    return chars


def resolver(chars):
    """The creator's spelling of a character -> slug: the zh-cn page title, plus the aliases in names.json."""
    by = {norm(v['zh-cn']['name']): s for s, v in chars.items()}
    by.update({norm(k): v for k, v in load('community/names.json')['aliases'].items()})
    return by


def arc_names():
    arcs = {k: {lang: v[lang]['name'] for lang in LANGS} for k, v in load('arcs.json')['arcs'].items()}
    arcs.update(load('community/names.json')['arcs'])
    return arcs, {norm(v['zh-cn']): k for k, v in arcs.items()}


def norm(s):
    return re.sub(r'[「」\s！!：:·]', '', s)


# ---------------------------------------------------------------- the creator's text, rendered

OPS = r'(>|≈|=|≥|/)'


ACTS = {  # the guides' words for one action in a rotation, beyond the four skill slots
    '长按普攻': {'en': 'hold Basic Attack', 'zh-tw': '長按普通攻擊', 'zh-cn': '长按普通攻击', 'ja': '通常攻撃長押し', 'ko': '일반 공격 길게 누르기'},
    '强化技能': {'en': 'Enhanced Skill', 'zh-tw': '強化技能', 'zh-cn': '强化技能', 'ja': '強化スキル', 'ko': '강화 스킬'},
    '怪物技能': {'en': 'copied monster skill', 'zh-tw': '複製的怪物技能', 'zh-cn': '复制的怪物技能', 'ja': 'コピーした怪物スキル', 'ko': '복제한 괴물 스킬'},
    '闪避': {'en': 'dodge', 'zh-tw': '閃避', 'zh-cn': '闪避', 'ja': '回避', 'ko': '회피'},
}

G = {  # strings of the character guide pages
    'en': dict(title='{name} guide', pull='Pulls and Awakenings', teams='Teams and rotations', build='Arcs and cartridges', play='Playing tips',
               awak='Awakening {n}', res='Resonance {n}', gain='Gain ({who})', cond='Conditions', at='Video', item='Item',
               advice='Advice ({who})', rotation='Rotation', reason='Reason', tip='Tip', then=' → ', step='{who}: {acts}',
               desc='Bilibili creators\' advice on {name}: pulls, Awakening gains, team rotations, Arcs, cartridges and tips.',
               caveat='Every gain is the creator\'s own estimate under the conditions in its row, for the game version the creator played.'),
    'zh-tw': dict(title='{name}攻略', pull='抽取與覺醒', teams='配隊與出招順序', build='弧盤與卡帶', play='操作技巧',
                  awak='覺醒 {n}', res='共鳴 {n}', gain='收益（{who}）', cond='條件', at='影片', item='項目',
                  advice='建議（{who}）', rotation='出招順序', reason='理由', tip='技巧', then=' → ', step='{who}：{acts}',
                  desc='Bilibili 攻略創作者的{name}攻略：抽取與覺醒收益、配隊出招順序、弧盤與卡帶、操作技巧。',
                  caveat='每項收益都是創作者在該列條件下、於其所玩版本的估算。'),
    'zh-cn': dict(title='{name}攻略', pull='抽取与觉醒', teams='配队与出招顺序', build='弧盘与卡带', play='操作技巧',
                  awak='觉醒 {n}', res='共鸣 {n}', gain='收益（{who}）', cond='条件', at='视频', item='项目',
                  advice='建议（{who}）', rotation='出招顺序', reason='理由', tip='技巧', then=' → ', step='{who}：{acts}',
                  desc='Bilibili 攻略创作者的{name}攻略：抽取与觉醒收益、配队出招顺序、弧盘与卡带、操作技巧。',
                  caveat='每项收益都是创作者在该行条件下、于其所玩版本的估算。'),
    'ja': dict(title='{name}攻略', pull='入手と覚醒', teams='編成と立ち回り', build='弧盤とカートリッジ', play='操作のコツ',
               awak='覚醒{n}', res='共振{n}', gain='効果（{who}）', cond='条件', at='動画', item='項目',
               advice='推奨（{who}）', rotation='立ち回り', reason='理由', tip='コツ', then=' → ', step='{who}：{acts}',
               desc='Bilibiliの攻略投稿者による{name}の攻略：入手と覚醒の効果、編成の立ち回り、弧盤とカートリッジ、操作のコツ。',
               caveat='各効果は投稿者がその行の条件で、プレイしたバージョンについて見積もった値である。'),
    'ko': dict(title='{name} 공략', pull='획득과 각성', teams='파티와 로테이션', build='아크와 카트리지', play='조작 팁',
               awak='각성 {n}', res='공명 {n}', gain='효과({who})', cond='조건', at='영상', item='항목',
               advice='추천({who})', rotation='로테이션', reason='이유', tip='팁', then=' → ', step='{who}: {acts}',
               desc='Bilibili 공략 제작자의 {name} 공략: 획득과 각성 효과, 파티 로테이션, 아크와 카트리지, 조작 팁.',
               caveat='각 효과는 제작자가 해당 행의 조건에서, 자신이 플레이한 버전을 기준으로 추정한 값이다.'),
}
GUIDE_KINDS = ('pull', 'gain', 'rotation', 'reason', 'tip')
AWAK_HEAD = {'en': 'Awakenings', 'zh-tw': '覺醒', 'zh-cn': '觉醒', 'ja': '覚醒', 'ko': '각성'}
TEXT_LANGS = ('en', 'zh-tw', 'zh-cn', 'ja', 'ko')


def awakenings(path, lang):
    """The first column of the Awakenings table of a character page: six Awakenings, then the Resonances."""
    rows, inside = [], False
    for line in open(path, encoding='utf-8'):
        if line.startswith('## '):
            inside = line[3:].strip() == AWAK_HEAD[lang]
        elif inside and line.startswith('| ') and not line.startswith('| ---'):
            rows.append(line.split('|')[1].strip())
    return rows[1:]  # without the header row


def split_ops(text):
    """'A > B≈C' -> ['A', '>', 'B', '≈', 'C']; a list with no operator (spaces only) -> joined by '、'."""
    text = text.replace('＞', '>').replace('＝', '=').replace('／', '/').replace('\\', '/').replace('、', ' ').strip()
    parts = []
    for p in (p.strip() for p in re.split(OPS, text) if p.strip()):
        words = p.split() if p not in ('>', '≈', '=', '≥', '/') else [p]
        parts += [x for w in words for x in (w, '、')][:-1]
    return parts


def render(parts, word, lang):
    out = []
    for p in parts:
        if p == '、':
            out.append(T[lang]['sep'].strip() if lang in ZH else ',')
        elif p in ('>', '≈', '=', '≥', '/'):
            out.append(f' {p} ')
        else:
            out.append(word(p, lang))
    s = ''.join(out)
    return s.replace(' ,', ',').replace(',', ', ') if lang not in ZH else s


def stat_word(w, lang):
    w = re.sub(r'^(?:主C|副C)\s*[:：]\s*', '', w)
    m = re.fullmatch(r'(.)属性增伤', w)
    if m and m.group(1) in ELEMENTS:
        return ELEMENTS[m.group(1)][lang]
    if w in STAT_WORDS:
        return STATS[STAT_WORDS[w]][lang]
    raise SystemExit(f'records/community/claims.json: unknown stat word {w!r}')


def slot_word(w, lang):
    w = re.sub(r'^(?:主C|副C)\s*[:：]\s*', '', w)
    if w in SLOT_WORDS:
        return SLOTS[SLOT_WORDS[w]][lang]
    raise SystemExit(f'records/community/claims.json: unknown skill word {w!r}')


# ---------------------------------------------------------------- pages

def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join('---' for _ in head) + ' |']
    out += ['| ' + ' | '.join(str(c).replace('|', '／') for c in r) + ' |' for r in rows]
    return '\n'.join(out) + '\n'


def at(s, c):
    """Where a claim is shown: the creator's comment under the video, or the video at the second."""
    return f"{s['url']}#reply{c['reply']}" if 'reply' in c else f"{s['url']}?t={c['at']}"


def main():
    sources = {s['id']: s for s in load('community/sources.json')['sources']}
    claims = load('community/claims.json')['claims']
    check = sys.argv[1:2] == ['--check']
    if check:  # drafts lack zh-cn, which pipeline/community_zh_cn.py adds; a copy of zh-tw stands in
        for path in sys.argv[2:]:
            for c in json.load(open(path, encoding='utf-8')):
                for v in [c] + c.get('steps', []):
                    for x in v.values():
                        if isinstance(x, dict) and 'zh-tw' in x and 'en' in x:
                            x.setdefault('zh-cn', x['zh-tw'])
                claims.append(c)
    chars = character_names()
    by_name = resolver(chars)
    arcs, arc_by = arc_names()
    carts = load('community/names.json')['cartridges']
    cart_by = {norm(v['zh-cn']): k for k, v in carts.items()}

    def slug_of(name):
        n = norm(name)
        if n in by_name:
            return by_name[n]
        raise SystemExit(f'records/community/claims.json: unknown character {name!r}')

    def fill(text, lang):
        """{char:X}, {arc:X} and {cart:X} in a claim's own sentence -> that name in the page's language."""
        def one(m):
            kind, w = m.group(1), m.group(2)
            if kind == 'char':
                return chars[slug_of(w)][lang]['name']
            table, by = (arcs, arc_by) if kind == 'arc' else (carts, cart_by)
            if norm(w) not in by:
                raise SystemExit(f'records/community/claims.json: unknown {kind} {w!r}')
            n = table[by[norm(w)]][lang]
            return n if lang == 'en' or n.startswith('「') else f'「{n}」'
        out = re.sub(r'\{(char|arc|cart):([^}]+)\}', one, text)
        if re.search(r'[{}]', out):
            raise SystemExit(f'records/community/claims.json: a brace left in {text!r}')
        return out

    def acts(do, lang):
        """'大招>技能>普攻*2' -> the actions in order, in the page's language."""
        out = []
        for w in do.split('>'):
            w = w.strip()
            m = re.fullmatch(r'(.+?)\*(\d+)', w)
            w, n = (m.group(1), m.group(2)) if m else (w, '')
            w = {'重击': '长按普攻'}.get(w, w)  # a heavy attack is Basic Attack held, for every character that has one
            out.append((ACTS[w][lang] if w in ACTS else slot_word(w, lang)) + (f' ×{n}' if n else ''))
        return G[lang]['then'].join(out)

    for c in claims:  # every name resolves, every claim has one place
        if c['source'] not in sources:
            raise SystemExit(f"records/community/claims.json: unknown source {c['source']}")
        if ('at' in c) == ('reply' in c):
            raise SystemExit(f'records/community/claims.json: a claim needs one of at, reply: {c}')
        if c['kind'] == 'team':
            c['slugs'] = [[slug_of(n) for n in m] for m in c['members']]
        elif c['kind'] == 'build':
            c['slug'] = slug_of(c['character'])
            for p in split_ops(c['arcs']):
                if p not in ('>', '≈', '=', '≥', '/', '、') and norm(p) not in arc_by:
                    raise SystemExit(f"records/community/claims.json: unknown Arc {p!r}")
            for x in c['cartridge'].split('/'):
                if norm(x) not in cart_by:
                    raise SystemExit(f"records/community/claims.json: unknown cartridge set {x!r}")
            if c['role'] not in ROLES:
                raise SystemExit(f"records/community/claims.json: unknown role {c['role']!r}")
            for lang in LANGS:  # stat, skill and passive words all resolve
                render(split_ops(c['main']), stat_word, lang)
                render(split_ops(c['sub']), stat_word, lang)
                for line in c['skills'].split('\n'):
                    render(split_ops(re.sub(r'^(?:不合轴|合轴)\s*[:：]\s*', '', line.strip())), slot_word, lang)
        elif c['kind'] in GUIDE_KINDS:
            for key in ('text', 'value', 'cond', 'note', 'variant'):
                if key in c and set(c[key]) != set(TEXT_LANGS):
                    raise SystemExit(f"records/community/claims.json: {key} needs {TEXT_LANGS}: {c}")
            for lang in LANGS:  # every name in the text and every action resolves
                for key in ('text', 'value', 'cond', 'note', 'variant'):
                    if key in c:
                        fill(c[key][lang], lang)
                for st in c.get('steps', []):
                    slug_of(st['who'])
                    acts(st['do'], lang)
                    if 'note' in st:
                        fill(st['note'][lang], lang)
            team = c.get('team') or (c['topic'][5:] if c.get('topic', '').startswith('team:') else None)
            if team is not None and team not in {(t['label'] or f"@{t.get('at')}") for t in claims if t['kind'] == 'team' and t['source'] == c['source']}:
                raise SystemExit(f"records/community/claims.json: {team!r} names no team of {c['source']} (an unnamed team is \"@<its at>\")")
            item = c.get('item', {})
            if 'arc' in item and norm(item['arc']) not in arc_by:
                raise SystemExit(f"records/community/claims.json: unknown Arc {item['arc']!r}")
            if 'cartridge' in item and norm(item['cartridge']) not in cart_by:
                raise SystemExit(f"records/community/claims.json: unknown cartridge set {item['cartridge']!r}")
        else:
            raise SystemExit(f"records/community/claims.json: unknown kind {c['kind']!r}")
    if check:
        print(f'claims valid: {len(claims)}')
        return
    order = list(chars)

    # Each character and each main shows the guides of the newest game version that covers it;
    # older claims stay in the records only (../COMMUNITY.md: one page for the newest version).
    def vkey(c):
        return tuple(int(x) for x in sources[c['source']]['version'].split('.'))

    def newest(cs):
        top = max(map(vkey, cs), default=None)
        return [c for c in cs if vkey(c) == top]

    for lang in LANGS:
        t, p = T[lang], PREFIX[lang]

        def name(slug):
            n = chars[slug][lang]['name']
            return f'[{n}](/{p}characters/{slug}/)' if chars[slug][lang]['page'] else n

        def plain(slug):
            return chars[slug][lang]['name']

        def guide(s):
            return t['guide'].format(name=plain(s['subject']))

        def who(s):
            names = [creator(s['creator'], lang)] + [creator(x, lang) for x in s.get('with', [])]
            return t['sep'].join(names)

        def team_label(lab):
            if not lab:
                return '—'
            if lab in LABELS:
                return LABELS[lab][lang]
            m = re.fullmatch(r'(.+?)(主C|副C)队(\d*)', lab)
            if m:
                who_ = plain(slug_of(m.group(1)))
                return t['main_team'].format(name=who_) if m.group(2) == '主C' else t['sub_team'].format(name=who_, n=m.group(3)).strip()
            m = re.fullmatch(r'(.+?)单C', lab)
            if m:
                return {'en': '{n} as the only DPS', 'zh-tw': '{n}單輸出隊', 'zh-cn': '{n}单输出队', 'ja': '{n}単独アタッカー編成', 'ko': '{n} 단독 딜러 파티'}[lang].format(n=plain(slug_of(m.group(1))))
            m = re.fullmatch(r'(.+?)dot队', lab, re.I)
            if m:
                return {'en': '{n} DoT team', 'zh-tw': '{n} DoT 隊', 'zh-cn': '{n} DoT 队', 'ja': '{n}DoTチーム', 'ko': '{n} DoT 파티'}[lang].format(n=plain(slug_of(m.group(1))))
            m = re.fullmatch(r'(.+?)(' + '|'.join(CYCLES) + r')队', lab)
            if m:
                return t['cycle_team'].format(cycle=CYCLES[m.group(2)][lang]) + (' (' if lang not in ZH else '（') + plain(slug_of(m.group(1))) + (')' if lang not in ZH else '）')
            m = re.fullmatch(r'(.+?)队', lab)
            if m and m.group(1) in CYCLES:
                return t['cycle_team'].format(cycle=CYCLES[m.group(1)][lang])
            raise SystemExit(f'records/community/claims.json: no rendering for the team label {lab!r}')

        def arc_word(w, lang_=lang):
            return arcs[arc_by[norm(w)]][lang_]

        def talents(c):
            parts = split_ops(c['talents'])
            out = []
            for x in parts:
                m = re.fullmatch(r'天赋\s*([12])', x)
                if m:
                    n = int(m.group(1))
                    pas = chars[c['slug']][lang]['passives'].get(n)
                    label = t['passive'].format(n=n)
                    out.append(f'{label}（{pas}）' if lang in ZH else f'{label} ({pas})')
                elif x in ('>', '≈', '=', '/'):
                    out.append(f' {x} ')
                else:
                    raise SystemExit(f'records/community/claims.json: unknown passive word {x!r}')
            return ''.join(out)

        def skill_order(text):
            out = []
            for line in text.split('\n'):
                m = re.match(r'(不合轴|合轴)\s*[:：]\s*(.*)', line.strip())
                if m:
                    out.append(f"{CONDITIONS[m.group(1)][lang]}{'：' if lang in ZH else ': '}{render(split_ops(m.group(2)), slot_word, lang)}")
                else:
                    out.append(render(split_ops(line), slot_word, lang))
            return ('；' if lang in ZH else '; ').join(out)

        def write(rel, title, desc, applies, caveat, srcs, aliases, body):
            fm = ['---', f'title: {yaml_str(title)}', f'description: {yaml_str(desc)}']
            if aliases:
                fm += ['aliases:', *[f'  - {yaml_str(a)}' for a in aliases if a != title]]
            fm += [f'appliesTo: {yaml_str(applies)}', f"lastVerified: {max(s['read'] for s in srcs)}", f'caveat: {yaml_str(caveat)}', 'sources:']
            for s in srcs:
                fm += [f"  - title: {yaml_str(t['src_title'].format(title=s['title'], creator=who(s), date=s['published']))}", f"    url: {s['url']}"]
            path = os.path.join(DOCS, p + 'community', rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'w', encoding='utf-8').write('\n'.join(fm + ['---', '', body.rstrip('\n'), '']))

        def applies(srcs):
            vs = sorted({s['version'] for s in srcs})
            dates = sorted(s['published'] for s in srcs)
            servers = sorted({s['server'] for s in srcs})
            return t['applies' if dates[0] != dates[-1] else 'applies1'].format(versions=t['sep'].join(VERSION_WORD[lang].format(v=v) for v in vs),
                                       server=t['sep'].join(t[x] for x in servers), n=len(srcs), s='' if len(srcs) == 1 else 's',
                                       first=dates[0], last=dates[-1], read=t['sep'].join(sorted({s['read'] for s in srcs})))

        # ---- teams
        teams = [c for c in claims if c['kind'] == 'team']
        mains = [s for s in order if any(c['slugs'][0][0] == s for c in teams)]
        shown = [c for m in mains for c in newest([c for c in teams if c['slugs'][0][0] == m])]
        team_srcs = [s for s in sources.values() if any(c['source'] == s['id'] for c in shown)]
        body = []
        for m in mains:
            body += [f'## {plain(m)}', '']
            cs = sorted(newest([c for c in teams if c['slugs'][0][0] == m]), key=lambda c: sources[c['source']]['published'], reverse=True)
            # One table per source: its header names the creator, so every row and note is attributed.
            for sid in dict.fromkeys(c['source'] for c in cs):
                s = sources[sid]
                rows = []
                notes = any(c.get('note') for c in cs if c['source'] == sid)
                for c in (c for c in cs if c['source'] == sid):
                    members = ' + '.join(t['any_one'].join(name(x) for x in alt) if len(alt) > 1 else name(alt[0]) for alt in c['slugs'])
                    label = team_label(c['label']) if c['label'] else t['team']
                    rows.append([f'[{label}]({at(s, c)})', members] + ([c.get('note', {}).get(lang, '')] if notes else []))
                head = [f"[{who(s)}，{guide(s)}]({s['url']})" if lang in ZH else f"[{who(s)}, {guide(s)}]({s['url']})", t['members']] + ([t['note']] if notes else [])
                body += [table(head, rows)]
        n_teams = len(mains)
        write('teams.md', t['teams'], t['teams_desc'].format(n=n_teams), applies(team_srcs), t['teams_caveat'], team_srcs, aliases('teams', lang), '\n'.join(body))

        # ---- builds: one table per character, one column per distinct card
        builds = [c for c in claims if c['kind'] == 'build']
        subjects = [s for s in order if any(c['slug'] == s for c in builds)]
        shown_b = [c for x in subjects for c in newest([c for c in builds if c['slug'] == x])]
        build_srcs = [s for s in sources.values() if any(c['source'] == s['id'] for c in shown_b)]
        fields = ['role', 'arcs', 'cartridge', 'main', 'sub', 'talents', 'skills']
        body = []
        for subj in subjects:
            cols = []  # [key, [claims]]
            for c in sorted(newest([c for c in builds if c['slug'] == subj]), key=lambda c: sources[c['source']]['published'], reverse=True):
                key = tuple(norm(c[f]) for f in fields)
                same = next((col for col in cols if col[0] == key and sources[col[1][0]['source']]['creator'] == sources[c['source']]['creator']), None)
                if same:
                    if c['source'] not in [x['source'] for x in same[1]]:
                        same[1].append(c)
                    same[2].append(c)
                else:
                    cols.append([key, [c], [c]])
            heads = []
            for _, cs, _all in cols:
                s0 = sources[cs[0]['source']]
                links = t['sep'].join(f"[{guide(sources[c['source']])}]({at(sources[c['source']], c)})" for c in cs)
                heads.append(f"{who(s0)}（{links}）" if lang in ZH else f"{who(s0)} ({links})")
            rows = []
            labels = [t['in_team'], t['role'], t['arcs'], t['cart'], t['cart_main'], t['sub'], t['talents'], t['skills']]
            if any(c.get('note') for _, cs, _a in cols for c in cs):
                labels.append(t['note'])
            for i, lab in enumerate(labels):
                row = [lab]
                for _, cs, allc in cols:
                    c = cs[0]
                    if i == 0:
                        row.append(t['sep'].join(dict.fromkeys(team_label(x['team']) for x in allc if x.get('team'))) or '—')
                    elif i == 1:
                        row.append(ROLES[c['role']][lang])
                    elif i == 2:
                        row.append(render(split_ops(c['arcs']), arc_word, lang))
                    elif i == 3:
                        row.append(' / '.join(carts[cart_by[norm(x)]][lang] for x in c['cartridge'].split('/')))
                    elif i == 4:
                        row.append(render(split_ops(c['main']), stat_word, lang))
                    elif i == 5:
                        row.append(render(split_ops(c['sub']), stat_word, lang))
                    elif i == 6:
                        row.append(talents(c))
                    elif i == 7:
                        row.append(skill_order(c['skills']))
                    else:
                        row.append(c.get('note', {}).get(lang, ''))
                rows.append(row)
            body += [f'## {plain(subj)}', '', table(['', *heads], rows)]
        write('builds.md', t['builds'], t['builds_desc'].format(n=len(subjects)), applies(build_srcs), t['builds_caveat'], build_srcs, aliases('builds', lang), '\n'.join(body))

        # ---- one guide page per character a guide is about: pulls and Awakenings, teams, Arcs, tips
        g = G[lang]
        guided = [c for c in claims if c['kind'] in GUIDE_KINDS]
        guide_pages = []
        for subj in sorted({sources[c['source']]['subject'] for c in guided}, key=order.index):
            cs = newest([c for c in guided if sources[c['source']]['subject'] == subj])
            srcs_g = sorted({c['source']: sources[c['source']] for c in cs}.values(), key=lambda s: s['published'], reverse=True)
            awk = chars[subj][lang]['awakenings']

            def when(s, c):
                return f"[{c['at'] // 60}:{c['at'] % 60:02d}]({at(s, c)})"

            def item_label(item):
                if 'awakening' in item:
                    n = item['awakening']
                    lab = g['awak'].format(n=n)
                    return f'{lab}（{awk[n - 1]}）' if lang in ZH and awk else (f'{lab} ({awk[n - 1]})' if awk else lab)
                if 'resonance' in item:
                    n = item['resonance']
                    hit = [r for r in awk[6:] if re.search(rf'\b{n}\b|{n}[：:]', r)]
                    return hit[0] if hit else g['res'].format(n=n)
                if 'arc' in item:
                    return fill('{arc:' + item['arc'] + '}', lang)
                return fill('{cart:' + item['cartridge'] + '}', lang)

            def row_text(c):
                if c['kind'] == 'rotation':
                    steps = ('；' if lang in ZH else '; ').join(
                        g['step'].format(who=plain(slug_of(st['who'])), acts=acts(st['do'], lang))
                        + ((f"（{fill(st['note'][lang], lang)}）" if lang in ZH else f" ({fill(st['note'][lang], lang)})") if 'note' in st else '')
                        for st in c['steps'])
                    head = (fill(c['variant'][lang], lang) + ('：' if lang in ZH else ': ')) if 'variant' in c else ''
                    tail = (('。' if lang in ZH else '. ') + fill(c['note'][lang], lang)) if 'note' in c else ''
                    return head + steps + tail
                return fill(c['text'][lang], lang)

            body = []
            for s in srcs_g:
                mine = [c for c in cs if c['source'] == s['id']]
                who_ = f"[{who(s)}]({s['url']})"
                kinds = {'rotation': g['rotation'], 'reason': g['reason'], 'tip': g['tip'], 'pull': g['tip']}
                # pulls and Awakenings
                pulls = [c for c in mine if c['kind'] == 'pull']
                gains = [c for c in mine if c['kind'] == 'gain' and ({'awakening', 'resonance'} & set(c['item']))]
                if pulls or gains:
                    body += [f"## {g['pull']}", '']
                    if pulls:
                        body += [table([g['advice'].format(who=who_), g['at']], [[row_text(c), when(s, c)] for c in pulls])]
                    if gains:
                        gains.sort(key=lambda c: (c['item'].get('awakening', 0) + 10 * c['item'].get('resonance', 0) // 3))
                        body += [table([g['item'], g['gain'].format(who=who_), g['cond'], g['at']],
                                       [[item_label(c['item']), fill(c['value'][lang], lang), fill(c['cond'][lang], lang), when(s, c)] for c in gains])]
                # teams, in the order of the guide's own team list
                # A team the guide leaves unnamed is keyed "@<second>" and headed by its members.
                teams_s = {(c['label'] or f"@{c['at']}"): c for c in claims if c['kind'] == 'team' and c['source'] == s['id']}
                labels = list(dict.fromkeys(list(teams_s)
                                            + [c['team'] for c in mine if c['kind'] == 'rotation']
                                            + [c['topic'][5:] for c in mine if c.get('topic', '').startswith('team:')]))
                team_rows = {lab: [c for c in mine if c.get('team') == lab or c.get('topic') == 'team:' + lab] for lab in labels}
                if any(team_rows.values()):
                    body += [f"## {g['teams']}", '']
                    for lab in labels:
                        if not team_rows[lab]:
                            continue
                        rows = sorted(team_rows[lab], key=lambda c: (c['kind'] != 'rotation', c['at']))
                        if lab.startswith('@'):
                            sep = '、' if lang in ZH else ', '
                            head_ = sep.join('/'.join(plain(slug_of(n)) for n in m) for m in teams_s[lab]['members'])
                        else:
                            head_ = team_label(lab)
                        body += [f'### {head_}', '', table(['', who_, g['at']], [[kinds[c['kind']], row_text(c), when(s, c)] for c in rows])]
                # Arcs and cartridges
                bgains = [c for c in mine if c['kind'] == 'gain' and ({'arc', 'cartridge'} & set(c['item']))]
                breasons = [c for c in mine if c.get('topic') == 'build']
                if bgains or breasons:
                    body += [f"## {g['build']}", '']
                    if bgains:
                        body += [table([g['item'], g['gain'].format(who=who_), g['cond'], g['at']],
                                       [[item_label(c['item']), fill(c['value'][lang], lang), fill(c['cond'][lang], lang), when(s, c)] for c in sorted(bgains, key=lambda c: c['at'])])]
                    if breasons:
                        body += [table(['', who_, g['at']], [[kinds[c['kind']], row_text(c), when(s, c)] for c in sorted(breasons, key=lambda c: c['at'])])]
                play = [c for c in mine if c.get('topic') == 'play']
                if play:
                    body += [f"## {g['play']}", '', table(['', who_, g['at']], [[kinds[c['kind']], row_text(c), when(s, c)] for c in sorted(play, key=lambda c: c['at'])])]
            name_ = plain(subj)
            others = [G[x]['title'].format(name=chars[subj][x]['name']) for x in LANGS if x != lang]
            write(f'{subj}.md', g['title'].format(name=name_), g['desc'].format(name=name_), applies(srcs_g), g['caveat'], srcs_g,
                  list(dict.fromkeys(others)), '\n'.join(body))
            guide_pages.append(subj)

        # ---- index
        srcs = sorted({s['id']: s for s in team_srcs + build_srcs}.values(), key=lambda s: s['published'], reverse=True)
        covered = sorted({x for c in shown for alt in c['slugs'] for x in alt} | set(subjects), key=order.index)
        creators_ = t['sep'].join(dict.fromkeys(who(s) for s in team_srcs))
        topics = [f'- [{t["teams"]}](/{p}community/teams/)', f'- [{t["builds"]}](/{p}community/builds/)']
        topics += [f"- [{G[lang]['title'].format(name=plain(x))}](/{p}community/{x}/)" for x in guide_pages]
        rows = [[who(s), f"[{s['title']}]({s['url']})", s['published'], t[s['server']], VERSION_WORD[lang].format(v=s['version']), plain(s['subject'])] for s in srcs]
        body = [f"## {t['topic']}", '', *topics, '',
                f"## {t['source']}", '', table([t['creator'], t['video'], t['published'], t['server'], t['version'], t['covers']], rows)]
        write('index.md', t['idx_title'], t['idx_desc'].format(n=len(covered), v=len(srcs)), applies(srcs), t['idx_caveat'], srcs, aliases('idx_title', lang), '\n'.join(body))
    # The sidebar lists the guide pages after teams and builds (astro.config.mjs reads this file).
    open(os.path.join(ROOT, 'src', 'community-guides.json'), 'w', encoding='utf-8').write(json.dumps(guide_pages) + '\n')
    print('community pages written:', len(LANGS), 'languages,', len(sources), 'sources,', len(claims), 'claims')


if __name__ == '__main__':
    main()
