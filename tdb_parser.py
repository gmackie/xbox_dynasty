#!/usr/bin/env python3
"""
EA TDB Save File Parser

Parses Xbox 360 NCAA Football save files (roster + dynasty) that use EA's
proprietary TDB binary database format wrapped in an MC02 container.

Usage:
    python tdb_parser.py <file>                          List all tables
    python tdb_parser.py <file> <TABLE>                  Dump table as CSV
    python tdb_parser.py <file> <TABLE> -o out.csv       Write to file
    python tdb_parser.py <file> <TABLE> --schema         Show field definitions
    python tdb_parser.py <file> <TABLE> --raw            Use raw field codes
    python tdb_parser.py export <file> -o dir/           Export all tables
    python tdb_parser.py sqlite <file> [-o out.db]       Export to SQLite
    python tdb_parser.py diff <file1> <file2> <TABLE>    Compare tables
"""

import argparse
import csv
import io
import os
import sqlite3
import struct
import sys


# Field type constants
FIELD_STRING = 0
FIELD_BINARY = 1
FIELD_SINT = 2
FIELD_UINT = 3
FIELD_FLOAT = 4

FIELD_TYPE_NAMES = {
    FIELD_STRING: "String",
    FIELD_BINARY: "Binary",
    FIELD_SINT: "SInt",
    FIELD_UINT: "UInt",
    FIELD_FLOAT: "Float",
}

# Per-table field name mappings. The same 4-char codes can have DIFFERENT
# meanings across tables (e.g. HTCP = "Release" in PLAY but "Catching" in RCPT).
# Verified by cross-referencing TDB dumps against game-exported CSVs.
TABLE_FIELD_NAMES = {
    # PLAY table - verified across 7,411 unique-name players, zero mismatches
    "PLAY": {
        "ANFP": "FirstName", "ANLP": "LastName", "TGWP": "TeamId",
        "RVOP": "Overall", "DPSP": "Speed", "RTSP": "Strength",
        "IGAP": "Agility", "CCAP": "Acceleration", "PMJP": "Jumping",
        "RWAP": "Awareness", "ATSP": "Stamina", "JNIP": "Injury",
        "KTBP": "BreakTackle", "KRTP": "Trucking", "VSEP": "Elusiveness",
        "RASP": "StiffArm", "VMSP": "SpinMove", "VMJP": "JukeMove",
        "RACP": "Carrying", "VCBP": "BallCarrierVision",
        "KBPP": "PassBlock", "KBRP": "RunBlock",
        "SBPP": "Catching", "FBPP": "SpectacularCatch",
        "WFBP": "CatchInTraffic", "SBRP": "RouteRunning",
        "HTCP": "Release", "TCPS": "Tackle", "FART": "HitPower",
        "RTRP": "Pursuit", "SLER": "PlayRecognition",
        "KATP": "PowerMoves", "TIHP": "FinesseMoves",
        "SRPP": "BlockShedding", "CRPP": "ManCoverage",
        "VMPP": "ZoneCoverage", "VMFP": "Press",
        "HSBP": "ThrowPower", "VCMP": "ThrowAccuracy",
        "VCZP": "KickPower", "SRYP": "KickAccuracy",
        "SOPP": "Position",
    },
    # RCPT table - verified across 2,572 unique-name recruits
    # NOTE: 15 field codes have DIFFERENT meanings vs PLAY table
    "RCPT": {
        "ANFP": "FirstName", "ANLP": "LastName",
        "ISRP": "RecordIndex", "BCCR": "Caliber", "KRCR": "Rank",
        "PGPR": "Position", "TGHP": "Height", "TGWP": "Weight",
        "TATS": "HomeState",
        "DPSP": "Speed", "RTSP": "Strength", "IGAP": "Agility",
        "CCAP": "Acceleration", "PMJP": "Jumping", "ATSP": "Stamina",
        "JNIP": "Injury",
        "KTBP": "BreakTackle", "KRTP": "Trucking", "VSEP": "Elusiveness",
        "RASP": "StiffArm", "VMSP": "SpinMove", "VMJP": "JukeMove",
        "RACP": "Carrying", "VCBP": "BallCarrierVision",
        "KBPP": "PassBlock", "KBRP": "RunBlock", "LBIP": "ImpactBlocking",
        "HTCP": "Catching", "TCPS": "SpectacularCatch",
        "FART": "CatchInTraffic", "RTRP": "RouteRunning", "SLER": "Release",
        "KATP": "Tackle", "TIHP": "HitPower", "SRPP": "Pursuit",
        "CRPP": "PlayRecognition",
        "VMPP": "PowerMoves", "VMFP": "FinesseMoves", "HSBP": "BlockShedding",
        "VCMP": "ManCoverage", "VCZP": "ZoneCoverage", "SRYP": "Press",
        "PHTP": "ThrowPower", "AHTP": "ThrowAccuracy",
        "RPKP": "KickPower", "CAKP": "KickAccuracy",
        "RVOP": "Overall", "VOCR": "Potential", "RWAP": "Awareness",
        "EOPP": "ScoutedOverall", "TRKP": "BaseOverall",
        "EHGP": "HomeTownId", "DHCR": "HomeTownHash",
        "MCCR": "ReducedSchoolsFlag", "GTSP": "RecruitingStage",
    },
    # TEAM table - 128 teams, key fields
    "TEAM": {
        "ANDT": "TeamName", "ANLT": "LocationName", "ANMT": "Mascot",
        "ANST": "Abbreviation", "TASC": "AsciiCode",
        "DIGT": "TeamId", "DIGC": "ConferenceId", "DIGD": "DivisionId",
        "DIGS": "StadiumId", "DIGL": "LeagueLevel",
        "WHCT": "AllTimeWins", "LHCT": "AllTimeLosses", "THCT": "AllTimeTies",
        "NYCN": "NatChampCount",
        "WSPT": "SeasonWins", "LSPT": "SeasonLosses",
        "APCT": "APPollRank", "FPCT": "CoachesPollRank",
        "WCRC": "ConfWins", "LCRC": "ConfLosses",
        "SCPT": "ConfStanding", "SDPT": "DivStanding",
        "VORT": "OverallRating", "RFTT": "RecruitingPrestige",
        "WOBC": "BowlWins", "LOBC": "BowlLosses",
    },
    # COCH table - coaches (HC/OC/DC)
    "COCH": {
        "MNFC": "FirstName", "MNLC": "LastName", "ANLC": "CoachTitle",
        "DICC": "CoachId", "DIGT": "TeamId", "SPOC": "StaffPosition",
        "ATDC": "DefenseCoaching", "ATOC": "OffenseCoaching",
        "NWTC": "CareerWins", "LTOC": "CareerLosses",
        "WTTC": "TeamWins", "LTTC": "TeamLosses",
        "TARC": "OverallRating",
    },
    # SCHD table - verified via 10 game score cross-references
    "SCHD": {
        "CSHG": "HomeScore", "CSAG": "AwayScore",
        "GTHG": "HomeTeamId", "GTAG": "AwayTeamId",
        "TWES": "WeekNum", "TADG": "DayOfWeek",
        "DOTG": "GameTime", "ATSG": "GameStatus",
        "ISES": "SeasonType", "RYES": "DynastyYear",
    },
    # STST/TSSE - team stats, verified via additive identities & opponent swaps
    "STST": {
        "DIGT": "TeamId",
        "post": "PassingYards", "apst": "PassingAttempts",
        "cpst": "PassingCompletions",
        "rost": "RushingYards", "arst": "RushingAttempts",
        "yost": "TotalOffensiveYards",
        "ytst": "TotalReturnYards", "rkst": "KickReturnYards",
        "rpst": "PuntReturnYards", "yTst": "TotalAllPurposeYards",
        "yPst": "PenaltyYards",
        "ipst": "InterceptionsThrown", "lfst": "FumblesLost",
        "agst": "TurnoversCommitted",
        "iDst": "InterceptionsByDefense", "rfst": "FumblesRecovered",
        "atst": "TurnoversForced",
        "ksst": "SacksMade", "asst": "SacksAllowed",
        "d1st": "FirstDowns", "d3st": "ThirdDownAttempts",
        "c3st": "ThirdDownConversions",
        "tPst": "PassingTouchdowns",
        "a2st": "TwoPointAttempts", "c2st": "TwoPointConversions",
    },
    "TSSE": {
        "DIGT": "TeamId",
        "post": "PassingYards", "apst": "PassingAttempts",
        "rost": "RushingYards", "arst": "RushingAttempts",
        "yost": "TotalOffensiveYards",
        "ytst": "TotalReturnYards", "yTst": "TotalAllPurposeYards",
        "yPst": "PenaltyYards",
        "ipst": "InterceptionsThrown", "lfst": "FumblesLost",
        "agst": "TurnoversCommitted",
        "iDst": "InterceptionsByDefense", "rfst": "FumblesRecovered",
        "atst": "TurnoversForced",
        "ksst": "SacksMade", "asst": "SacksAllowed",
        "d1st": "FirstDowns",
        "tPst": "PassingTouchdowns",
        "pdst": "OppPassingYards", "ydst": "OppRushingYards",
    },
    # SOFF - player offensive season stats
    "SOFF": {
        "DIGP": "PlayerId",
        "taag": "PassAttempts", "mcag": "PassCompletions",
        "ayag": "PassYards", "Nlag": "PassLong",
        "dtag": "PassTouchdowns", "niag": "Interceptions",
        "asag": "SacksTaken",
        "taug": "RushAttempts", "ayug": "RushYards", "Nlug": "RushLong",
        "dtug": "RushTouchdowns",
        "accg": "Receptions", "aycg": "RecYards", "Lrcg": "RecLong",
        "dtcg": "RecTouchdowns",
    },
    # SDEF - player defensive season stats
    "SDEF": {
        "DIGP": "PlayerId",
        "thdg": "Tackles", "atdg": "TacklesForLoss",
        "ltdg": "Sacks", "dpdg": "PassDeflections",
        "fflg": "ForcedFumbles", "rflg": "FumbleRecoveries",
        "nisg": "Interceptions", "kslg": "HalfSacks",
        "Rlsg": "IntReturnYards", "yisg": "IntReturnLong",
    },
    # SKIC - kicker/punter season stats
    # Verified: bakg+cakg+dakg+eakg==afkg (100%), bmkg+cmkg+dmkg+emkg==mfkg (100%)
    "SKIC": {
        "DIGP": "PlayerId",
        "afkg": "FGAttempts", "mfkg": "FGMade", "Lfkg": "FGLong",
        "aekg": "XPAttempts", "mekg": "XPMade",
        "bakg": "FGAtt_20_29", "bmkg": "FGMade_20_29",
        "cakg": "FGAtt_30_39", "cmkg": "FGMade_30_39",
        "dakg": "FGAtt_40_49", "dmkg": "FGMade_40_49",
        "eakg": "FGAtt_50Plus", "emkg": "FGMade_50Plus",
        "tapg": "TotalPunts", "aypg": "TotalPuntYards",
        "ynpg": "NetPuntYards", "Nlpg": "PuntLong",
        "knkg": "Kickoffs", "tppg": "PuntTouchbacks",
        "btkg": "KickoffTouchbacks",
    },
    # CONF table
    "CONF": {
        "MANC": "Name", "DIGC": "ConferenceId", "DIGL": "LeagueLevel",
    },
    # DIVI table
    "DIVI": {
        "MAND": "FullName", "MNDS": "ShortName",
        "DIGC": "ConferenceId", "DIGD": "DivisionId",
    },
    # STAD table
    "STAD": {
        "MANS": "StadiumName", "NNTS": "Nickname",
        "TICS": "City", "DIGS": "StadiumId",
        "PACS": "Capacity", "TOIS": "IsIndoor",
    },
    # BOWL table
    "BOWL": {
        "EMNB": "BowlName", "DIGS": "StadiumId",
        "NWES": "WeekNum",
    },
    # INJY table
    "INJY": {
        "DIGP": "PlayerId", "DIGT": "TeamId",
        "LJNI": "Duration", "TJNI": "InjuryType",
    },
    # HEIS table
    "HEIS": {
        "DIGP": "PlayerId", "PACP": "HesmanPoints",
        "KRPH": "CandidateRank",
    },
    # SEAI table - dynasty state
    "SEAI": {
        "RYES": "DynastyYear", "NWES": "CurrentWeek",
        "TWES": "WeekType", "WOES": "TotalWeeks",
    },
    # CONT table - coach contracts
    "CONT": {
        "DICC": "CoachId", "DIGT": "TeamId", "SPOC": "StaffPosition",
        "RYCC": "YearsRemaining",
    },
    # CITY table
    "CITY": {
        "MNYC": "CityName", "TSYC": "StateName",
        "POPC": "Population", "DIYC": "CityIndex",
    },
}

# Legacy flat lookup for backward compatibility (PLAY table defaults)
FIELD_NAMES = TABLE_FIELD_NAMES["PLAY"]


def extract_bits(record_bytes, bit_offset, bit_width):
    """Extract bit_width bits starting at bit_offset from record_bytes (MSB-first)."""
    if bit_width == 0:
        return 0
    result = 0
    for i in range(bit_width):
        byte_idx = (bit_offset + i) // 8
        bit_idx = 7 - ((bit_offset + i) % 8)  # MSB-first
        if byte_idx < len(record_bytes):
            result = (result << 1) | ((record_bytes[byte_idx] >> bit_idx) & 1)
        else:
            result <<= 1
    return result


def decode_field(record_bytes, field):
    """Decode a field value from a record's raw bytes."""
    ftype = field["type"]
    bit_offset = field["bit_offset"]
    bit_width = field["bits"]

    if ftype == FIELD_STRING:
        # String fields are byte-aligned, extract raw bytes
        byte_offset = bit_offset // 8
        byte_len = bit_width // 8
        raw = record_bytes[byte_offset : byte_offset + byte_len]
        # Null-terminate
        null_pos = raw.find(b"\x00")
        if null_pos >= 0:
            raw = raw[:null_pos]
        return raw.decode("ascii", errors="replace")

    elif ftype == FIELD_BINARY:
        byte_offset = bit_offset // 8
        byte_len = bit_width // 8
        return record_bytes[byte_offset : byte_offset + byte_len].hex()

    elif ftype == FIELD_UINT:
        return extract_bits(record_bytes, bit_offset, bit_width)

    elif ftype == FIELD_SINT:
        raw = extract_bits(record_bytes, bit_offset, bit_width)
        # Sign-extend
        if bit_width > 0 and (raw >> (bit_width - 1)) & 1:
            raw -= 1 << bit_width
        return raw

    elif ftype == FIELD_FLOAT:
        raw = extract_bits(record_bytes, bit_offset, bit_width)
        if bit_width == 32:
            return struct.unpack(">f", struct.pack(">I", raw))[0]
        return raw

    else:
        return extract_bits(record_bytes, bit_offset, bit_width)


def parse_tdb(data, tdb_offset):
    """Parse a single TDB database at the given offset in data.

    Returns a dict with 'tables' mapping table_name -> table_info.
    """
    # TDB header (24 bytes)
    magic = data[tdb_offset : tdb_offset + 2]
    if magic != b"DB":
        raise ValueError(f"Invalid TDB magic at 0x{tdb_offset:X}: {magic!r}")

    version = struct.unpack(">H", data[tdb_offset + 2 : tdb_offset + 4])[0]
    db_size = struct.unpack(">I", data[tdb_offset + 8 : tdb_offset + 12])[0]
    table_count = struct.unpack(">I", data[tdb_offset + 16 : tdb_offset + 20])[0]

    # TOC starts at tdb_offset + 24
    toc_offset = tdb_offset + 24
    data_area = toc_offset + table_count * 8

    tables = {}
    for i in range(table_count):
        entry_off = toc_offset + i * 8
        name_bytes = data[entry_off : entry_off + 4]
        # Names are stored reversed
        reversed_bytes = name_bytes[::-1]
        if all(32 <= b < 127 for b in reversed_bytes):
            name = reversed_bytes.decode("ascii")
        else:
            name = f"0x{name_bytes.hex().upper()}"
        offset = struct.unpack(">I", data[entry_off + 4 : entry_off + 8])[0]
        table_abs = data_area + offset

        tables[name] = parse_table(data, table_abs, name)

    return {
        "version": version,
        "db_size": db_size,
        "table_count": table_count,
        "tdb_offset": tdb_offset,
        "tables": tables,
    }


def parse_table(data, table_offset, name):
    """Parse a table header, field definitions, and record data."""
    hdr = data[table_offset : table_offset + 40]
    if len(hdr) < 40:
        return {"name": name, "error": "truncated header"}

    alloc_type = struct.unpack(">I", hdr[4:8])[0]
    record_length = struct.unpack(">I", hdr[8:12])[0]
    capacity = struct.unpack(">H", hdr[20:22])[0]
    record_count = struct.unpack(">H", hdr[22:24])[0]
    field_count = hdr[28]

    # Parse field definitions (16 bytes each, starting after 40-byte header)
    fields = []
    field_start = table_offset + 40
    for i in range(field_count):
        fd_off = field_start + i * 16
        ftype = struct.unpack(">I", data[fd_off : fd_off + 4])[0]
        bit_offset = struct.unpack(">I", data[fd_off + 4 : fd_off + 8])[0]
        fname = data[fd_off + 8 : fd_off + 12].decode("ascii", errors="replace")
        bits = struct.unpack(">I", data[fd_off + 12 : fd_off + 16])[0]
        fields.append(
            {
                "name": fname,
                "type": ftype,
                "bit_offset": bit_offset,
                "bits": bits,
            }
        )

    # Record data starts after field definitions
    record_data_offset = field_start + field_count * 16

    return {
        "name": name,
        "alloc_type": alloc_type,
        "record_length": record_length,
        "capacity": capacity,
        "record_count": record_count,
        "field_count": field_count,
        "fields": fields,
        "record_data_offset": record_data_offset,
    }


def read_records(data, table_info):
    """Read all active records from a table."""
    records = []
    rec_off = table_info["record_data_offset"]
    rec_len = table_info["record_length"]
    rec_count = table_info["record_count"]
    fields = table_info["fields"]

    for i in range(rec_count):
        start = rec_off + i * rec_len
        rec_bytes = data[start : start + rec_len]
        row = {}
        for field in fields:
            row[field["name"]] = decode_field(rec_bytes, field)
        records.append(row)

    return records


def find_tdbs(data):
    """Find all TDB databases in the file.

    Handles MC02 wrapper and scans for additional TDB databases
    (dynasty files have two).
    """
    tdbs = []

    # Check for MC02 wrapper
    if data[:4] == b"MC02":
        sub_hdr_size = struct.unpack(">I", data[8:12])[0]
        first_tdb = sub_hdr_size + 0x1C

        # Parse MC02 timestamp from sub-header
        # Sub-header starts at 0x1C with a 4-byte prefix, then timestamp fields
        ts_offset = 0x1C + 4
        if ts_offset + 12 <= len(data):
            year = struct.unpack(">H", data[ts_offset : ts_offset + 2])[0]
            month = struct.unpack(">H", data[ts_offset + 2 : ts_offset + 4])[0]
            day = struct.unpack(">H", data[ts_offset + 4 : ts_offset + 6])[0]
            hour = struct.unpack(">H", data[ts_offset + 6 : ts_offset + 8])[0]
            minute = struct.unpack(">H", data[ts_offset + 8 : ts_offset + 10])[0]
            second = struct.unpack(">H", data[ts_offset + 10 : ts_offset + 12])[0]
            timestamp = f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        else:
            timestamp = None
    elif data[:2] == b"DB":
        first_tdb = 0
        timestamp = None
    else:
        raise ValueError(f"Unknown file format (magic: {data[:4]!r})")

    # Parse first TDB
    if data[first_tdb : first_tdb + 2] == b"DB":
        tdbs.append(first_tdb)

    # Scan for additional TDBs (dynasty files have two)
    # Search for "DB\x00\x08" pattern after the first TDB
    search_start = first_tdb + 24  # skip first TDB header
    while search_start < len(data) - 24:
        idx = data.find(b"DB\x00\x08", search_start)
        if idx < 0:
            break
        # Validate: check table_count is reasonable
        tc = struct.unpack(">I", data[idx + 16 : idx + 20])[0]
        ds = struct.unpack(">I", data[idx + 8 : idx + 12])[0]
        if 0 < tc < 500 and ds > 0 and idx != first_tdb:
            tdbs.append(idx)
        search_start = idx + 24

    return tdbs, timestamp


def format_schema(table_info):
    """Format field definitions as a readable table."""
    lines = []
    lines.append(f"Table: {table_info['name']}")
    lines.append(
        f"  Records: {table_info['record_count']} / {table_info['capacity']} "
        f"(capacity), Record size: {table_info['record_length']} bytes, "
        f"Fields: {table_info['field_count']}"
    )
    lines.append("")
    lines.append(f"  {'Name':<8} {'Type':<8} {'BitOff':>6} {'Bits':>5}")
    lines.append(f"  {'─'*8} {'─'*8} {'─'*6} {'─'*5}")
    # Sort fields by bit_offset for readability
    sorted_fields = sorted(table_info["fields"], key=lambda f: f["bit_offset"])
    for f in sorted_fields:
        type_name = FIELD_TYPE_NAMES.get(f["type"], f"?({f['type']})")
        lines.append(
            f"  {f['name']:<8} {type_name:<8} {f['bit_offset']:>6} {f['bits']:>5}"
        )
    return "\n".join(lines)


def records_to_csv(records, fields, output=None, friendly_names=False,
                   table_name=None):
    """Write records as CSV. Returns string if output is None."""
    if not records:
        return ""

    # Sort fields by bit_offset for consistent column order
    sorted_fields = sorted(fields, key=lambda f: f["bit_offset"])
    raw_names = [f["name"] for f in sorted_fields]

    if friendly_names:
        # Use per-table mapping if available, fall back to PLAY defaults
        name_map = TABLE_FIELD_NAMES.get(table_name, FIELD_NAMES) if table_name else FIELD_NAMES
        header_names = [name_map.get(n, n) for n in raw_names]
    else:
        header_names = raw_names

    def _write(dest):
        writer = csv.writer(dest)
        writer.writerow(header_names)
        for rec in records:
            writer.writerow([rec.get(n, "") for n in raw_names])

    if output is None:
        buf = io.StringIO()
        _write(buf)
        return buf.getvalue()
    else:
        _write(output)


def load_file(path):
    """Load a save file and return (data, tdb_offsets, timestamp)."""
    with open(path, "rb") as f:
        data = f.read()
    tdb_offsets, timestamp = find_tdbs(data)
    if not tdb_offsets:
        print(f"Error: No TDB databases found in {path}", file=sys.stderr)
        sys.exit(1)
    return data, tdb_offsets, timestamp


def find_table_in_file(data, tdb_offsets, table_name, db_idx=None):
    """Find a table by name across TDB databases. Returns (data, table_info)."""
    target = table_name.upper()
    if db_idx is not None:
        indices = [db_idx]
    else:
        indices = range(len(tdb_offsets))

    for idx in indices:
        db = parse_tdb(data, tdb_offsets[idx])
        if target in db["tables"]:
            return data, db["tables"][target]

    return None, None


def cmd_list(args):
    """List all tables in a file."""
    data, tdb_offsets, timestamp = load_file(args.file)

    if timestamp:
        print(f"Timestamp: {timestamp}")
    print(f"Found {len(tdb_offsets)} TDB database(s)\n")

    for db_idx, tdb_off in enumerate(tdb_offsets):
        db = parse_tdb(data, tdb_off)
        print(
            f"DB {db_idx}: version={db['version']}, "
            f"tables={db['table_count']}, "
            f"offset=0x{tdb_off:X}"
        )
        print(f"  {'Table':<12} {'Records':>8} {'Capacity':>9} {'Fields':>7} "
              f"{'RecLen':>7}")
        print(f"  {'─'*12} {'─'*8} {'─'*9} {'─'*7} {'─'*7}")
        for name in sorted(db["tables"]):
            t = db["tables"][name]
            if "error" in t:
                print(f"  {name:<12} ERROR: {t['error']}")
            else:
                print(
                    f"  {name:<12} {t['record_count']:>8} "
                    f"{t['capacity']:>9} {t['field_count']:>7} "
                    f"{t['record_length']:>7}"
                )
        print()


def cmd_dump(args):
    """Dump a single table as CSV."""
    data, tdb_offsets, timestamp = load_file(args.file)

    if args.db is not None and args.db >= len(tdb_offsets):
        print(
            f"Error: DB index {args.db} out of range "
            f"(file has {len(tdb_offsets)} DBs)",
            file=sys.stderr,
        )
        sys.exit(1)

    _, table_info = find_table_in_file(data, tdb_offsets, args.table, args.db)

    if table_info is None:
        print(f"Error: Table '{args.table.upper()}' not found", file=sys.stderr)
        for db_idx, tdb_off in enumerate(tdb_offsets):
            db = parse_tdb(data, tdb_off)
            tables = sorted(db["tables"].keys())
            print(f"  DB {db_idx}: {', '.join(tables)}", file=sys.stderr)
        sys.exit(1)

    if args.schema:
        print(format_schema(table_info))
        return

    records = read_records(data, table_info)
    use_friendly = not args.raw
    tname = args.table.upper()
    if args.output:
        with open(args.output, "w", newline="") as f:
            records_to_csv(records, table_info["fields"], f,
                           friendly_names=use_friendly, table_name=tname)
        print(f"Wrote {len(records)} records to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(
            records_to_csv(records, table_info["fields"],
                           friendly_names=use_friendly, table_name=tname)
        )


def cmd_export(args):
    """Export all tables (or tables with data) to a directory of CSV files."""
    data, tdb_offsets, timestamp = load_file(args.file)
    outdir = args.output or "export"
    os.makedirs(outdir, exist_ok=True)

    db_indices = [args.db] if args.db is not None else range(len(tdb_offsets))
    total_files = 0
    use_friendly = not args.raw

    for db_idx in db_indices:
        if db_idx >= len(tdb_offsets):
            continue
        db = parse_tdb(data, tdb_offsets[db_idx])
        prefix = f"db{db_idx}_" if len(tdb_offsets) > 1 else ""

        for name in sorted(db["tables"]):
            t = db["tables"][name]
            if "error" in t or t["record_count"] == 0:
                continue

            records = read_records(data, t)
            fname = f"{prefix}{name}.csv"
            fpath = os.path.join(outdir, fname)
            with open(fpath, "w", newline="") as f:
                records_to_csv(records, t["fields"], f,
                               friendly_names=use_friendly, table_name=name)
            total_files += 1

    print(f"Exported {total_files} tables to {outdir}/", file=sys.stderr)


def cmd_sqlite(args):
    """Export all tables to a single SQLite database file."""
    data, tdb_offsets, timestamp = load_file(args.file)
    outpath = args.output or os.path.splitext(os.path.basename(args.file))[0] + ".db"

    # Remove existing file to avoid stale data
    if os.path.exists(outpath):
        os.remove(outpath)

    conn = sqlite3.connect(outpath)
    db_indices = [args.db] if args.db is not None else range(len(tdb_offsets))
    use_friendly = not args.raw
    total_tables = 0

    # Map TDB field types to SQLite type affinities
    sqlite_types = {
        FIELD_STRING: "TEXT",
        FIELD_BINARY: "TEXT",
        FIELD_SINT: "INTEGER",
        FIELD_UINT: "INTEGER",
        FIELD_FLOAT: "REAL",
    }

    for db_idx in db_indices:
        if db_idx >= len(tdb_offsets):
            continue
        db = parse_tdb(data, tdb_offsets[db_idx])
        prefix = f"db{db_idx}_" if len(tdb_offsets) > 1 else ""

        for name in sorted(db["tables"]):
            t = db["tables"][name]
            if "error" in t or t["record_count"] == 0:
                continue

            records = read_records(data, t)
            sorted_fields = sorted(t["fields"], key=lambda f: f["bit_offset"])
            raw_names = [f["name"] for f in sorted_fields]

            if use_friendly:
                name_map = TABLE_FIELD_NAMES.get(name, FIELD_NAMES)
                col_names = [name_map.get(n, n) for n in raw_names]
            else:
                col_names = list(raw_names)

            # Deduplicate column names (SQLite identifiers are case-insensitive,
            # so e.g. "tpst" and "tPst" collide)
            seen = {}
            for i, c in enumerate(col_names):
                key = c.lower()
                if key in seen:
                    seen[key] += 1
                    col_names[i] = f"{c}_{seen[key]}"
                else:
                    seen[key] = 0

            col_defs = ", ".join(
                f'"{c}" {sqlite_types.get(sf["type"], "TEXT")}'
                for c, sf in zip(col_names, sorted_fields)
            )
            table_name = f"{prefix}{name}"
            conn.execute(f'CREATE TABLE "{table_name}" ({col_defs})')

            placeholders = ", ".join("?" for _ in col_names)
            conn.executemany(
                f'INSERT INTO "{table_name}" VALUES ({placeholders})',
                [[rec.get(n, "") for n in raw_names] for rec in records],
            )
            total_tables += 1

    conn.commit()
    conn.close()
    print(f"Exported {total_tables} tables to {outpath}", file=sys.stderr)


def cmd_diff(args):
    """Compare a table between two files and show differences."""
    data1, offsets1, _ = load_file(args.file1)
    data2, offsets2, _ = load_file(args.file2)

    target = args.table.upper()
    _, t1 = find_table_in_file(data1, offsets1, target, args.db)
    _, t2 = find_table_in_file(data2, offsets2, target, args.db)

    if t1 is None:
        print(f"Error: Table '{target}' not found in {args.file1}", file=sys.stderr)
        sys.exit(1)
    if t2 is None:
        print(f"Error: Table '{target}' not found in {args.file2}", file=sys.stderr)
        sys.exit(1)

    recs1 = read_records(data1, t1)
    recs2 = read_records(data2, t2)

    # Build field name list (sorted by bit_offset)
    sorted_fields = sorted(t1["fields"], key=lambda f: f["bit_offset"])
    field_names = [f["name"] for f in sorted_fields]

    # Determine a key for matching records. Use string fields if available,
    # otherwise fall back to record index.
    string_fields = [f["name"] for f in sorted_fields if f["type"] == FIELD_STRING]

    def record_key(rec):
        if string_fields:
            return tuple(str(rec.get(f, "")) for f in string_fields)
        return None

    # Try key-based matching first
    use_keys = string_fields and len({record_key(r) for r in recs1}) == len(recs1)

    if use_keys:
        map2 = {}
        for r in recs2:
            map2[record_key(r)] = r

        added = []
        removed = []
        changed = []

        keys1 = set()
        for r1 in recs1:
            k = record_key(r1)
            keys1.add(k)
            r2 = map2.get(k)
            if r2 is None:
                removed.append(r1)
            else:
                diffs = {}
                for fn in field_names:
                    v1, v2 = r1.get(fn), r2.get(fn)
                    if str(v1) != str(v2):
                        diffs[fn] = (v1, v2)
                if diffs:
                    changed.append((r1, diffs))

        for r2 in recs2:
            if record_key(r2) not in keys1:
                added.append(r2)
    else:
        # Index-based matching
        added = []
        removed = []
        changed = []
        max_len = max(len(recs1), len(recs2))
        for i in range(max_len):
            if i >= len(recs1):
                added.append(recs2[i])
            elif i >= len(recs2):
                removed.append(recs1[i])
            else:
                diffs = {}
                for fn in field_names:
                    v1, v2 = recs1[i].get(fn), recs2[i].get(fn)
                    if str(v1) != str(v2):
                        diffs[fn] = (v1, v2)
                if diffs:
                    changed.append((recs1[i], diffs))

    # Print summary
    print(f"Diff: {target} ({len(recs1)} vs {len(recs2)} records)")
    print(f"  Changed: {len(changed)}, Added: {len(added)}, Removed: {len(removed)}")

    if not changed and not added and not removed:
        print("  No differences found.")
        return

    # Print changes
    # Build a label for each record using string fields
    def rec_label(rec):
        parts = []
        for sf in string_fields:
            v = rec.get(sf, "")
            if v:
                parts.append(str(v))
        return " | ".join(parts) if parts else f"(record)"

    name_map = TABLE_FIELD_NAMES.get(target, FIELD_NAMES)
    for rec, diffs in changed:
        label = rec_label(rec)
        print(f"\n  ~ {label}")
        for fn, (v1, v2) in sorted(diffs.items()):
            fn_display = name_map.get(fn, fn)
            print(f"      {fn_display}: {v1} -> {v2}")

    for rec in added:
        print(f"\n  + {rec_label(rec)}")

    for rec in removed:
        print(f"\n  - {rec_label(rec)}")


def main():
    # Detect subcommand mode vs default mode
    if len(sys.argv) > 1 and sys.argv[1] in ("export", "sqlite", "diff"):
        mode = sys.argv[1]
        if mode == "export":
            parser = argparse.ArgumentParser(
                prog="tdb_parser.py export",
                description="Export all tables to CSV files",
            )
            parser.add_argument("file", help="Path to the save file")
            parser.add_argument(
                "-o", "--output", help="Output directory (default: export)"
            )
            parser.add_argument("--db", type=int, default=None, help="TDB index")
            parser.add_argument(
                "--raw", action="store_true", help="Use raw field codes"
            )
            args = parser.parse_args(sys.argv[2:])
            cmd_export(args)
        elif mode == "sqlite":
            parser = argparse.ArgumentParser(
                prog="tdb_parser.py sqlite",
                description="Export all tables to a SQLite database",
            )
            parser.add_argument("file", help="Path to the save file")
            parser.add_argument(
                "-o", "--output", help="Output .db file (default: <input>.db)"
            )
            parser.add_argument("--db", type=int, default=None, help="TDB index")
            parser.add_argument(
                "--raw", action="store_true", help="Use raw field codes"
            )
            args = parser.parse_args(sys.argv[2:])
            cmd_sqlite(args)
        elif mode == "diff":
            parser = argparse.ArgumentParser(
                prog="tdb_parser.py diff",
                description="Compare a table between two files",
            )
            parser.add_argument("file1", help="First save file")
            parser.add_argument("file2", help="Second save file")
            parser.add_argument("table", help="Table name to compare")
            parser.add_argument("--db", type=int, default=None, help="TDB index")
            args = parser.parse_args(sys.argv[2:])
            cmd_diff(args)
    else:
        parser = argparse.ArgumentParser(
            description="EA TDB Save File Parser for NCAA Football"
        )
        parser.add_argument("file", help="Path to the save file")
        parser.add_argument(
            "table", nargs="?", help="Table name to dump (e.g. PLAY)"
        )
        parser.add_argument("-o", "--output", help="Output CSV file path")
        parser.add_argument(
            "--schema", action="store_true",
            help="Show field definitions instead of data",
        )
        parser.add_argument(
            "--db", type=int, default=None,
            help="TDB index for dynasty files (0 or 1)",
        )
        parser.add_argument(
            "--raw", action="store_true",
            help="Use raw TDB field codes instead of friendly names",
        )
        args = parser.parse_args()

        if args.table:
            cmd_dump(args)
        else:
            cmd_list(args)


if __name__ == "__main__":
    main()
