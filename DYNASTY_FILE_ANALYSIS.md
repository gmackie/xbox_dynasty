# NCAA Football Dynasty Save File Analysis

**File:** `OD-Avalanche36OD1_file`
**Timestamp:** 2012-12-02 20:45:07
**Format:** EA TDB binary database (MC02 container)
**Databases:** 2 (DB0 = dynasty metadata, DB1 = full game data)
**Total Tables:** 180 (3 in DB0, 177 in DB1)
**Non-Empty Tables:** 102 (3 in DB0, 99 in DB1)
**Empty Tables:** 78 (all in DB1)

---

## Dynasty Overview

This is a 12-user online dynasty in its **3rd season** (RYES=2, year index 0-based). The dynasty is named "Avalanche36OD1" and appears to be from NCAA Football 13 (based on conference alignment: Big East still exists, no CFP).

### Dynasty Users (DB0: DYUS -- 12 records)

| Gamertag | Team | Coach ID |
|----------|------|----------|
| Avalanche36 | Cal (DIGT=17) | 710 |
| RIDGE the BRIT | Rutgers (80) | 711 |
| Stay KLassy SD | Arizona State (5) | 712 |
| Andrizzle32 | Boston College (13) | 713 |
| BlackxScott | SMU (83) | 714 |
| cwheyer | Syracuse (88) | 715 |
| Hacksaw8 | Maryland (47) | 716 |
| B1GK4HUN4BURG3R | Miami (49) | 717 |
| csaber23 | Illinois (35) | 719 |
| ConnorvJJ | Virginia (107) | 720 |
| Wolandeeh | UCF (18) | 725 |
| TeenierCashew63 | Pittsburgh (77) | 734 |

---

## Table Categories

### 1. Player/Roster Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **PLAY** | 8,588 | 147 | **Main player table.** Every player in the game. Fields include DIGP (player ID), DIOP (original ID), ANFP (first name), ANLP (last name), TGWP (team ID), plus ~140 attribute/rating fields (speed, strength, awareness, throwing, catching, blocking, etc.). Key table for roster editing. |
| **PLST** | 970 | 131 | **Player snapshots/starters.** Similar schema to PLAY but for a subset of players (likely starters or featured players). Contains DIGP, DIOP, ANFP, ANLP, TGWP plus rating attributes. Some entries have no name (e.g., "RG #65", "DT #97") -- possibly generated/generic players. |
| **PLSU** | 48 | 5 | **Player suspensions/status.** DIGP, DIGT, IPFP, OFLP, OIFP -- tracks players with special status flags (injured/suspended/etc.). |
| **PPRO** | 640 | 3 | **Player progression.** DIGP, DIPR (progression type), DMYP -- tracks which players have progressed and how. |
| **INJY** | 8 | 7 | **Active injuries.** Current in-game injuries: DIGP, LJNI (length), TJNI (type), DIGT, RINI, RJNI. Only 8 active injuries at this point in the season. |
| **SINJ** | 389 | 7 | **Season injury history.** All injuries that occurred during seasons: DIGP, LJNI, MNGS (week), TJNI, GIII, RINI, RJNI. |
| **TRAN** | 237 | 4 | **Transfers.** Players who transferred: DIGP, CART (action type?), DITP (destination team?), RYRT (year). |
| **OSPA** | 208 | 4 | **Off-season player actions.** DIGP, RAOP (rating change?), RYES (year), TAOP (action type). |

### 2. Team Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **TEAM** | 128 | 195 | **Main team table.** All 128 FBS teams. String fields: ANDT (name, e.g., "Alabama"), ANLT (location name), ANMT (mascot, e.g., "Crimson Tide"), ANST (abbreviation, e.g., "Bama"), CCMT (description, e.g., "Established in 1831"), CNMT (nickname), TASC (6-char code, e.g., "ALBAMA"). Numeric fields cover uniform colors, prestige, rivalries, win/loss history, offensive/defensive ratings, conference/division IDs, and ~150 other attributes. |
| **STAD** | 185 | 117 | **Stadiums.** One per stadium: MANS (name), NNTS (team name), ANDT (location). Includes capacity fields (EUCS, LLCS, LUCS), coordinates (NOLS lat, TALS long), plus extensive visual/display configuration (70+ fields for rendering). |
| **CITY** | 224 | 21 | **Cities/locations for recruiting.** MNYC (city name, e.g., "Miami"), POPC (population), TSYC (state), WFYC (weather), DHCR (hash code). Used for recruit hometown mapping. |
| **LMTT** | 141 | 2 | **Team matchup table.** ATML, DTML -- appears to track pairings/matchups. |
| **TMCO** | 2 | 3 | **Team commissioner/settings.** Conference-level override settings. |
| **STTM** | 345 | 11 | **State-team mapping.** Links teams to states/conferences/divisions: DIGC (conference), DIGD (division), DIGT (team ID), DIOT (original team), NSID, PYTT (play type). |

### 3. Conference/Division Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **CONF** | 25 | 5 | **Conferences.** MANC (name): ACC, Big Ten, Big 12, Big East, C-USA, Independents, Ivy League, MAC, MEAC, MWC, Pac-12, SEC, SWAC, Sun Belt, WAC, Historic, Fantasy, Generic, Atlantic 10, Big Sky, Gateway, Southern, Southland, Ohio Valley, High School. DIGC = conference index, RPNC = something related to representation, DIGL = league level. |
| **DIVI** | 22 | 4 | **Divisions.** MAND (full name, e.g., "Pac-12 (North)"), MNDS (short name, e.g., "North"), DIGC (conference), DIGD (division index). All major conferences have 2 divisions. |
| **CNFR** | 180 | 4 | **Conference records/rivalries.** 1VRC, 2VRC (rival team pairs?), DIGC (conference), DIUR. 180 records suggest multiple rivalry/crossover matchups per conference. |
| **CSST** | 12 | 3 | **Conference schedule style.** ANTS describes the scheduling algorithm: "EvenDivsProtectedRivalsStyle", "EvenDivsOverlappingGamesStyle", "UnevenDivsStyle", "NoDivsAllConfOppsPlayedStyle". FPVR flag for protected rivals. |
| **LEAG** | 2 | 2 | **Leagues.** Just "1A" (FBS) and likely FCS. DIGL = league index. |

### 4. Schedule/Game Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **SCHD** | 788 | 20 | **Schedule.** All scheduled games: DOTG (date/time of game), DIGS (stadium), GTAG/GTHG (team A/team H IDs), MNGS (week number), CSAG/CSHG (scores away/home), TWES (season type?), NWES (week index), RYES (year). 788 games across the season. |
| **TSCH** | 1,845 | 5 | **Team schedule history.** AOHT (home/away), MNGS (week), DIGO (opponent), DIGT (team), NWES (week index). Multi-season schedule tracking across all teams. |
| **BOWL** | 45 | 17 | **Bowl games.** EMNB (name, e.g., "GoDaddy.com Bowl", "Las Vegas Bowl", "Kraft Fight Hunger Bowl"), DFMB (date), DIGS (stadium), 1ICB/2ICB (conference tie-ins), NOMB (bowl number). All 45 bowl games defined. |
| **SCRT** | 192 | 4 | **Schedule rotation.** DIGC, DIGT, RDIT, UNLS -- defines which teams play which in rotating conference schedules. |
| **SCWE** | 25 | 4 | **Schedule weeks.** Defines the 25-week season structure: DRPP (phase: 0=preseason, 1-4=regular season, 5=postseason), NWES (week index 0-20), RARP (end-of-phase flag). |
| **SGIN** | 58 | 58 | **Simulated game info.** Per-game simulation results: ECAP (efficiency), DOTG (date), GTAG/GTHG (teams), CSAG/CSHG (scores), IPAG/IPHG (stats), plus ~40 detailed game stat fields. 58 games played/simmed so far this season. |
| **GINF** | 1 | 56 | **Current game info.** Template/default for game setup -- most fields set to max/sentinel values (255, 4294967295, 999.99). |
| **SWQT** | 234 | 5 | **Schedule week/quarter tracking.** CSAG/CSHG (scores), MNGS (week), NWES, RTQG (quarter). |
| **WQSC** | 49 | 5 | **Week/quarter scores.** Similar to SWQT, likely for specific weeks. |
| **SCPR** | 2 | 2 | **Schedule presets.** Minimal -- 1SPS, POPS values. |

### 5. Stats Tables

#### 5a. Per-Season Player Stats (S-prefix = season-level)

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **SDEF** | 1,716 | 19 | **Season defensive stats.** Per-player: DIGP, MNGS (week), tackles (aslg, atdg), sacks (kslg), interceptions (nisg), forced fumbles (fflg), TFLs (tflg), pass deflections (dpdg), etc. |
| **SOFF** | 1,013 | 26 | **Season offensive stats.** Per-player: passing yards (aycg), rushing yards (ayug), receptions (Nlag), touchdowns (dtag, dtcg, dtug), completions (accg), etc. |
| **SKIC** | 176 | 26 | **Season kicking stats.** Per-player: FG attempts/makes (aekg, afkg), punt yards (aypg), kickoffs, blocked kicks, etc. |
| **SRET** | 259 | 10 | **Season return stats.** Kick/punt return yards and attempts per player. |
| **SOLN** | 570 | 4 | **Season O-line stats.** Per-player: DIGP, MNGS, pancakes (apog), sacks allowed (asog). |
| **SNGM** | 3,565 | 5 | **Season snap/game counts.** Per-player: games played (Pmgg), starts (Smgg), penalties (pdgg). |
| **SSUM** | 519 | 18 | **Season summary/standings.** Per-team per-week: points, wins, losses, team stats with DIGT and MNGS keys. |

#### 5b. Per-Season Team Stats (ST-prefix)

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **STST** | 116 | 74 | **Season team stats.** Per-team: total points (post), rushing yards (rost), passing yards (yost), total yards (yTst), 3rd-down conversions (c3st), 1st downs (d1st), turnovers (tost), penalties, sacks, etc. 74 stat categories. |
| **STTM** | 345 | 11 | **Season team meta.** Team-conference-division assignments per season. |
| **TSSE** | 20 | 37 | **Team season stats (extended).** Similar to STST with additional detail for fewer teams (likely user-controlled teams). |

#### 5c. Career/Cumulative Player Stats (PS-prefix)

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **PSDE** | 4,990 | 20 | **Career defensive stats.** DIGP, accumulated tackles/sacks/INTs/etc. across seasons. RYES (year), FKTS flags. |
| **PSOF** | 3,067 | 25 | **Career offensive stats.** Passing/rushing/receiving career totals. |
| **PSKI** | 333 | 28 | **Career kicking stats.** FG/punt career totals. |
| **PSKP** | 737 | 12 | **Career kick/punt return stats.** |
| **PSNG** | 8,532 | 7 | **Career snap/game counts.** Games played/started career totals. |
| **PSOL** | 1,858 | 6 | **Career O-line stats.** |
| **PSRA** | 1,178 | 4 | **Player-season-conference assignments.** DIGP, TSNI, DIGC, KNRP -- links players to their conference per season. |
| **PSRN** | 100 | 3 | **Player-season ranking.** Small subset of ranked players. |

#### 5d. Bowl/Postseason Game Stats (B-prefix)

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **BDEF** | 309 | 19 | **Bowl game defensive stats.** Same structure as SDEF but for bowl/postseason games. |
| **BOFF** | 169 | 27 | **Bowl game offensive stats.** |
| **BKIC** | 27 | 27 | **Bowl game kicking stats.** |
| **BKPR** | 37 | 11 | **Bowl game kick/punt return stats.** |
| **BOLN** | 87 | 5 | **Bowl game O-line stats.** |
| **BSCS** | 91 | 14 | **Bowl game scoring summary.** Per-game scoring plays with team/player refs. |
| **BTES** | 20 | 32 | **Bowl game team stats.** Full team stat lines for bowl games. |

### 6. Recruiting Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **RCPT** | 2,710 | 162 | **Recruit prospects.** Full player-like records for recruits: ISRP (recruit ID), ANFP/ANLP (name), TGWP (committed team?), plus all the same ~140 attribute fields as PLAY. Contains their physical/athletic ratings before they join a team. |
| **RCPR** | 2,710 | 37 | **Recruit preferences/profile.** Matching 1:1 with RCPT. Contains scouting point data at various stages (01SP, 10SP, 20SP...90SP with corresponding TP values), visit/recruiting progress info (1VRP...9VRP), max commitment threshold (MCTP), position (PGPR). |
| **RCST** | 52 | 11 | **Recruiting states.** One per state: BATS (abbreviation, e.g., "AL"), MNTS (full name, e.g., "Alabama"), NDPS (number of recruits), PUPS (population units?), pipeline info. |
| **RECB** | 4,279 | 7 | **Recruiting board.** Which teams are recruiting which prospects: ISRP (recruit), DIGT (team), LRTP (list rank), LESU (interest level), RORP (offer status), VPEP (visit priority). |
| **RECV** | 12 | 8 | **Recruiting visits.** Visit tracking for recruits: ISRP, 1ACR/2ACR/3ACR (visit slots?), DIGT. Only 12 active visits. |
| **PINT** | 1,623 | 51 | **Player/recruit interest.** Detailed interest levels from recruits toward schools: ISRP (recruit), DIGT (team), plus ~45 interest factor fields (SDTP, SFAP, SFPP, etc.) tracking how much each factor matters to the recruit. |
| **PINP** | 331 | 7 | **Player input/pipeline.** Recruit pipeline entries: LMSP (last modified), ISRP (recruit), DIGT (team), CSLP (class?), HMSP, VOUR (visit?). |
| **RPIF** | 85 | 7 | **Recruit position info.** IMTR, LIPR, MRFR, NMPR, PGPR, PIPR, SNSP -- position-based recruiting settings. |
| **RPOS** | 22 | 2 | **Recruit positions.** 22 entries = one per position. PGPR (position group), SOPP (position). |
| **RADV** | 30 | 3 | **Recruiting advisor.** ISRP (recruit), AVAR (advice type?), DIGT (team). |
| **RCYR** | 1 | 1 | **Recruiting year.** Single record, NWES = 0. |
| **CCGL** | 4,515 | 9 | **Coach/recruit grade links.** Maps coaches to recruits with evaluation grades: DIOG (hash?), CGCC/OCGC/PFGC/PPGC (grade categories), DINC (index), DPGC, XENU. |

### 7. Coach Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **COCH** | 384 | 153 | **Coaches.** All coaches in the game: ANLC (title, e.g., "AF Coach", "Bama Coach"), MNFC/MNLC (first/last name), DICC (coach ID), DIGT (team). 153 fields cover coaching attributes: offense/defense tendencies (IBCC-IBQC, TBFC-TBQC), recruiting skills, win/loss records (LWOG, WWOG, LTNT, WTNT), contract info, play style preferences, prestige. 384 coaches = ~3 per team (HC/OC/DC). |
| **CONT** | 369 | 12 | **Coach contracts.** DICC (coach ID), DIGT (team), DINC (index), RYCC (contract years), NMRT/XMRT (salary/negotiation), EICC (expiration). |
| **CREP** | 143 | 5 | **Coach reputation.** DICC (coach), NIOC, KPOC, MPOC (reputation metrics), YORP. |
| **CHIS** | 23 | 8 | **Coach history.** Past coaching records: DICC, IWST (win streak), DIGC (conference), DIGT (team), OLST (overall record), RYES (year). |

### 8. Dynasty Management Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **SEAI** | 1 | 20 | **Season info.** Current dynasty state: RYES=2 (year 3), TWES=1 (season type), NWES=1 (current week), WOES=22 (week of end of season?), BRES=3 (bowl round?), PFES=15, WPNS=7, WRES=15. Single record = current dynasty state. |
| **DYPH** | 2 | 8 | **Dynasty photos.** References to save-file screenshots: NFPD contains filename strings like "Pic-y s00-avalanche36o_10-07 23'55'50_00". |
| **DEID** | 1 | 2 | **Dynasty entity ID.** DICC=717, DIGT=47 -- identifies the "main" dynasty controller (Miami/B1GK4HUN4BURG3R based on coach ID match). |
| **TMWP** | 12 | 23 | **Team/user weekly progress.** One per user: nuSP (gamertag), DIGT (team), AOHT (auto-advance status), AFRT (auto-sim flag), various schedule/game state fields. Tracks each user's advance state in the dynasty. |
| **EASP** | 6 | 13 | **EA Sports features/settings.** Per-feature configuration data. |
| **MCOV** | 363 | 17 | **Media coverage.** Dynasty storylines and headlines: XTCM (story text, e.g., "The Trojans open their college football season with a game against Baylor."), XTHM (headline, e.g., "Getting Right to Work"), DIGT (team), MNGS (week). |
| **LDIF** | 1 | 4 | **Difficulty settings.** PGDL, PXDL, TCDL, VODL -- all set to 1. |
| **MLIN** | 1 | 2 | **Main line tracker.** IANT=0, IPNT=0. |
| **MOIN** | 1 | 11 | **Mode info.** IMIM (mode ID), ASCM/ASPM (settings), DIUX (user hash), PYTM=2 (play type?). |

### 9. Awards/Rankings Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **HEIS** | 10 | 11 | **Heisman Trophy candidates.** Top 10 candidates: DIGP, PACP (points), various voting category fields (CcAP, CsAP, ScAP, SsAP, VcAP, VsAP). |
| **PLAC** | 40 | 14 | **Player accolades.** Awards/honors per player per week: DIGP, saAP/taAP (award types), MNGS (week), conference/national voting fields. |
| **PRST** | 3,313 | 11 | **Prestige/award tracking.** Per-player per-week prestige data across multiple seasons. CcAP/CsAP, ScAP/SsAP, VcAP/VsAP (conference/national voting columns). |
| **PRSC** | 6,924 | 6 | **Pre-season/prestige scores.** Per-team scores: SSOS (strength of schedule?), DIGT, DIYS, EPTS (prestige points?), UNLP (unlock/rank). |
| **AAPL** | 1,114 | 6 | **All-American preseason list.** Player watchlist: DIGP, DIGC (conference), PYTT (position type), RYES (year), SOPP (position), TERA (team area?). |
| **PTIP** | 1,722 | 3 | **Pipeline/tip rankings.** DIGT (team), HCTP (points), TIPR (ranking). |
| **PTPS** | 2,583 | 5 | **Pipeline prestige by position.** DIGT, MTYP (metric type), SOPP (position), TSHC, TSRW. |

### 10. Depth Chart Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **DCHT** | 10,639 | 4 | **Depth chart.** Main depth chart: DIGP (player), DIGT (team), SOPP (position), pedd (depth/order). ~83 slots per team (128 teams). |
| **DCST** | 964 | 4 | **Depth chart starters.** Same schema as DCHT but just the starters. ~7.5 per team. |
| **TPDA** | 7,749 | 8 | **Team position depth assignments.** TSSP, DIGT, NETP, RSPP, SOPP (position), SPYP, VPYP, VTSP -- detailed position depth with backup priorities. |
| **TPHS** | 560 | 6 | **Team position history/redshirts.** 1RDP/2RDP/3RDP (round draft?), DIGT, LRDP, ryrd -- tracks position depth changes over time. |

### 11. Record Books

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **RBKS** | 3,321 | 15 | **Record book entries (school records).** HDCR (holder description, e.g., "1968 WR"), EDCR (era description), ODCR (opponent), UDCR (CPU/User), VDCR (value), DDCR (data code). Contains historical and dynasty-set records. |
| **RBKN** | 49 | 14 | **National record book.** Same schema as RBKS but for national/all-time records. 49 record categories tracked. |

### 12. Settings/Options Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **GOPT** | 1 | 139 | **Game options.** Massive settings record: play calling, difficulty sliders (YPUO/YRUO/YSUO for user pass/run/special), penalties (AFFO), quarter length, camera angles. Present in both DB0 and DB1. |
| **MOPT** | 1 | 59 | **Mode options.** Dynasty mode settings: auto-save, sim speed (ESNM=60), fatigue, CPU trade logic, recruiting settings. |
| **HSNN** | 175 | 1 | **High school team names.** Just CNMT field with names like "49ers", used for recruiting flavor. |
| **HSPL** | 1 | 1 | **High school players flag.** DICH=0. |
| **TABL** | 181 | 4 | **Table metadata.** Internal bookkeeping: FERT (field encoding?), EPFT, OIFT, SLFT -- one entry per table, used by the game engine. |
| **SCWE** | 25 | 4 | **Schedule week definitions.** Defines the season structure: 25 weeks across 6 phases (preseason, 4 regular season blocks, postseason). |
| **TSWP** | 125 | 4 | **Team schedule week pointers.** DIGT, RDIT, ROWS, RYES -- links teams to their schedule rotation entries. |

### 13. Miscellaneous Tables

| Table | Records | Fields | Description |
|-------|---------|--------|-------------|
| **0x00000110** | 123 | 10 | **Unknown/team voting?** Fields: ANDT (team name), KRCT, DIGC, DIGT, VTGT, VTRT, WOGT -- possibly poll/voting data. |
| **LGPL** | 1 | 75 | **League player spotlight.** Appears to be a featured/highlighted player record with extensive attributes. Currently empty/zeroed out. |
| **PPRO** | 640 | 3 | **Player progression mappings.** DIGP, DIPR (progression ID), DMYP (dummy?). |

---

## Empty Tables (78 tables)

### Play-Call / In-Game Stats (22 tables)
These tables are designed to capture per-play and per-game granular stats but are empty in this dynasty save (likely only populated during active gameplay, not persisted to the save file):

- **PC*** (13 tables): PCAW, PCCD, PCCK, PCCO, PCCR, PCDE, PCKI, PCKP, PCNG, PCOF, PCOL, PCSC, PCVT
- **PG*** (9 tables): PGDE, PGKI, PGKP, PGMP, PGNG, PGOF, PGOL, PGPE, PGPI

### Player Sub-Tables (5 tables)
Secondary player data that may only be populated in certain game modes:
- PLDA, PLGA, PLIA, PLRT, PLSS

### Tournament/Playoff (5 tables)
Empty postseason bracket tables:
- TSGA, TSPB, TSPD, TSPR, TSRD

### Other Empty Tables (46 tables)
Various UI, temp, or unused tables:
- CFSW, CLST, CTMU, CTRL, CUTP, DCGA, GBIN, HSPG, HSTM, IGAM, IRST, LETS, MCHG, MLAS, MRCT, PFTA, PNIN, POAG, POCH, POSA, PPBS, PSRT, RCTC, RCTN, RCWK, RTRI, RWST, SCHT, SCOS, SCSE, SOSH, SPGA, SPYR, TAUN, TCAL, TCPT, TEAH, TIMG, TMIF, TRGA, TRSE, TUNI, UOPT, USDT, USTG, WONS

---

## Key Relationships

```
PLAY.TGWP  --> TEAM.DIGT      (player belongs to team)
TEAM.DIGC  --> CONF.DIGC      (team in conference)
TEAM.DIGD  --> DIVI.DIGD      (team in division)
DIVI.DIGC  --> CONF.DIGC      (division in conference)
COCH.DIGT  --> TEAM.DIGT      (coach at team)
COCH.DICC  --> CONT.DICC      (coach has contract)
DCHT.DIGP  --> PLAY.DIGP      (depth chart references player)
DCHT.DIGT  --> TEAM.DIGT      (depth chart for team)
SCHD.GTAG  --> TEAM.DIGT      (away team in game)
SCHD.GTHG  --> TEAM.DIGT      (home team in game)
RCPT.ISRP  --> RCPR.ISRP      (recruit prospect + profile)
RECB.ISRP  --> RCPT.ISRP      (recruiting board for recruit)
RECB.DIGT  --> TEAM.DIGT      (team recruiting)
SDEF.DIGP  --> PLAY.DIGP      (season def stats for player)
SOFF.DIGP  --> PLAY.DIGP      (season off stats for player)
TMWP.nuSP  --> DYUS.nuSP      (user weekly progress)
TMWP.DIGT  --> TEAM.DIGT      (user's team)
```

---

## Summary Statistics

- **Total players:** 8,588 (PLAY table)
- **Teams:** 128 FBS teams
- **Conferences:** 25 (including FCS, Historic, Fantasy, etc.)
- **Divisions:** 22
- **Stadiums:** 185
- **Coaches:** 384 (~3 per team)
- **Recruits:** 2,710 prospects in the pipeline
- **Bowl games:** 45 defined
- **Scheduled games:** 788 this season
- **Games played/simmed:** 58 so far
- **Dynasty users:** 12 (online dynasty)
- **Dynasty season:** Year 3 (RYES=2)
- **Media stories:** 363 generated storylines
- **Record book entries:** 3,370 (3,321 school + 49 national)
- **Active injuries:** 8 current, 389 season total
- **Transfers:** 237 total
