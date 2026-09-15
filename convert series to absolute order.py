import json
import re
import sys
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# ============================================================
# CONFIGURATION
# ============================================================

# Directory containing the video files.
DIRECTORY = "C:\Path\To\Your\Show"

# Your TVDB API key.
API_KEY = "YOUR_TVDB_API_KEY"

# Optional.
#
# If left blank, the script will use the directory name as the
# TVDB search name.
#
# Example:
# SERIES_NAME = "The Simpsons"
#
SERIES_NAME = ""

# Optional.
#
# If you know the TVDB series ID, put it here.
# This is more reliable than searching by name.
#
# Example:
# TVDB_SERIES_ID = 71663
#
TVDB_SERIES_ID = None

# File extensions that will be processed.
VIDEO_EXTENSIONS = (
    ".mkv",
    ".mp4",
)

# Number of digits to use for the absolute episode number.
#
# 3 gives:
#   001
#   002
#   023
#   147
#
ABSOLUTE_DIGITS = 3

# If True, the script only displays what it WOULD rename.
#
# Set this to False after checking the output.
DRY_RUN = False


# ============================================================
# TVDB API
# ============================================================

BASE_URL = "https://api4.thetvdb.com/v4"


def api_request(method, endpoint, token=None, data=None, params=None):
    """
    Make a request to the TVDB v4 API.
    """

    url = BASE_URL + endpoint

    if params:
        url += "?" + urlencode(params)

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=body,
        method=method,
    )

    request.add_header("Accept", "application/json")

    if data is not None:
        request.add_header("Content-Type", "application/json")

    if token:
        request.add_header("Authorization", f"Bearer {token}")

    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    except HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            error_data = json.loads(error_body)
            message = error_data.get("message", error_body)
        except Exception:
            message = str(e)

        raise RuntimeError(
            f"TVDB API error {e.code}: {message}"
        ) from e

    except URLError as e:
        raise RuntimeError(
            f"Could not connect to TVDB: {e.reason}"
        ) from e


def login():
    """
    Authenticate with TVDB and return the bearer token.
    """

    print("Authenticating with TVDB...")

    response = api_request(
        "POST",
        "/login",
        data={
            "apikey": API_KEY
        },
    )

    token = response.get("data", {}).get("token")

    if not token:
        raise RuntimeError(
            "TVDB did not return an authentication token. "
            "Check your API key."
        )

    return token


# ============================================================
# SERIES SEARCH
# ============================================================

def normalize_name(name):
    """
    Normalize a name for comparison.
    """

    name = name.lower()

    name = re.sub(r"[^a-z0-9]+", " ", name)

    return " ".join(name.split())


def search_series(token, series_name):
    """
    Search TVDB for a series.

    The script prefers an exact normalized name match.
    If there are multiple plausible results and no exact match,
    it aborts rather than potentially renaming files incorrectly.
    """

    print(f"Searching TVDB for: {series_name}")

    response = api_request(
        "GET",
        "/search",
        token=token,
        params={
            "query": series_name,
            "type": "series",
        },
    )

    results = response.get("data", [])

    if not results:
        raise RuntimeError(
            f"No TVDB series found for '{series_name}'."
        )

    target = normalize_name(series_name)

    exact_matches = []

    for result in results:
        result_name = result.get("name", "")

        if normalize_name(result_name) == target:
            exact_matches.append(result)

    if len(exact_matches) == 1:
        return exact_matches[0]

    if len(exact_matches) > 1:
        print()
        print("Multiple exact TVDB matches were found:")
        print()

        for result in exact_matches:
            print(
                f"  {result.get('name')} "
                f"({result.get('year', 'unknown')}) "
                f"ID={result.get('tvdb_id')}"
            )

        raise RuntimeError(
            "Set TVDB_SERIES_ID manually in the configuration."
        )

    # No exact match.
    print()
    print("TVDB returned multiple possible matches:")
    print()

    for result in results[:10]:
        print(
            f"  {result.get('name')} "
            f"({result.get('year', 'unknown')}) "
            f"ID={result.get('tvdb_id')}"
        )

    raise RuntimeError(
        "No exact match was found. "
        "Set TVDB_SERIES_ID manually in the configuration."
    )


# ============================================================
# EPISODE RETRIEVAL
# ============================================================

def get_all_episodes(token, series_id, season_type):
    """
    Retrieve every episode for a series and season type.

    TVDB returns episode lists in pages, so we continue until
    there is no next page.
    """

    episodes = []
    page = 0

    while True:
        response = api_request(
            "GET",
            f"/series/{series_id}/episodes/{season_type}",
            token=token,
            params={
                "page": page,
            },
        )

        data = response.get("data", {})

        page_episodes = data.get("episodes", [])

        episodes.extend(page_episodes)

        links = response.get("links", {})

        next_page = links.get("next")

        if next_page is None:
            break

        page += 1

    return episodes


def build_episode_mapping(token, series_id):
    """
    Build:

        (season, episode) -> absolute episode number

    using TVDB's official order as the input and the absolute
    number assigned to the same episode as the output.
    """

    print("Downloading official episode order...")
    official = get_all_episodes(
        token,
        series_id,
        "official",
    )

    print(f"Found {len(official)} official order records.")

    mapping = {}

    for episode in official:
        season = episode.get("seasonNumber")
        number = episode.get("number")
        absolute = episode.get("absoluteNumber")

        if season is None:
            continue

        if number is None:
            continue

        if absolute is None:
            continue

        key = (
            int(season),
            int(number),
        )

        mapping[key] = int(absolute)

    if not mapping:
        raise RuntimeError(
            "TVDB returned no usable episode mappings."
        )

    return mapping


# ============================================================
# FILE PROCESSING
# ============================================================

EPISODE_PATTERN = re.compile(
    r"S(\d{1,3})E(\d{1,3})",
    re.IGNORECASE,
)


def find_video_files(directory):
    """
    Find video files directly inside the configured directory.
    """

    files = []
    for path in directory.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        files.append(path)

    return sorted(files)


def extract_episode(filename):
    """
    Extract SxxEyy from anywhere in the filename.

    Examples:

        Show.S01E02.1080p.mkv
        Show - S01E02 - Episode.mkv
        [Group] Show S01E02 [1080p].mp4

    all work.
    """

    match = EPISODE_PATTERN.search(filename)

    if not match:
        return None

    season = int(match.group(1))
    episode = int(match.group(2))

    return match, season, episode


def create_rename_plan(files, mapping):
    """
    Create a list of:

        old_path, new_path

    without actually changing anything.
    """

    plan = []
    errors = []

    for path in files:

        result = extract_episode(path.name)

        if result is None:
            print(
                f"SKIP: No SxxEyy found: {path.name}"
            )
            continue

        match, season, episode = result

        key = (season, episode)

        if key not in mapping:
            errors.append(
                f"{path.name}: "
                f"S{season:02d}E{episode:02d} "
                f"was not found in TVDB."
            )
            continue

        absolute = mapping[key]

        absolute_string = f"S01E{str(absolute).zfill(
            ABSOLUTE_DIGITS
        )}"

        # Replace only the SxxEyy portion.
        new_name = (
            path.name[:match.start()]
            + absolute_string
            + path.name[match.end():]
        )

        new_path = path.with_name(new_name)

        plan.append(
            (
                path,
                new_path,
                season,
                episode,
                absolute,
            )
        )

    return plan, errors


# ============================================================
# SAFE RENAMING
# ============================================================

def validate_plan(plan):
    """
    Check for problems before changing anything.
    """

    source_paths = {
        old_path.resolve()
        for old_path, _, _, _, _ in plan
    }

    destination_paths = {}

    for old_path, new_path, _, _, _ in plan:

        destination = new_path.resolve()

        if destination in destination_paths:
            raise RuntimeError(
                "Two files would be renamed to the same "
                f"destination:\n"
                f"  {destination_paths[destination]}\n"
                f"  {old_path}"
            )

        destination_paths[destination] = old_path

        # Existing destination is okay only if it is one of
        # the files being renamed.
        if new_path.exists() and destination not in source_paths:
            raise RuntimeError(
                f"Destination already exists:\n"
                f"  {new_path}"
            )


def perform_rename(plan):
    """
    Perform a collision safe two stage rename.

    Example:

        A.mkv -> temporary_name
        B.mkv -> A.mkv
        temporary_name -> B.mkv
    """

    validate_plan(plan)

    temporary_files = []

    print()
    print("Performing rename...")
    print()

    try:

        # ----------------------------------------------------
        # Stage 1
        #
        # Rename everything to temporary unique names.
        # ----------------------------------------------------

        for old_path, new_path, _, _, _ in plan:

            temporary_name = (
                f".tvdb_tmp_"
                f"{uuid.uuid4().hex}"
                f"{old_path.suffix}"
            )

            temporary_path = old_path.with_name(
                temporary_name
            )

            old_path.rename(temporary_path)

            temporary_files.append(
                (
                    temporary_path,
                    new_path,
                )
            )

        # ----------------------------------------------------
        # Stage 2
        #
        # Rename temporary files to their final names.
        # ----------------------------------------------------

        for temporary_path, new_path in temporary_files:
            temporary_path.rename(new_path)

    except Exception:

        print()
        print(
            "An error occurred during renaming."
        )
        print(
            "Some files may currently have temporary names."
        )
        print(
            "Check the directory before running the script again."
        )

        raise


# ============================================================
# DISPLAY
# ============================================================

def print_plan(plan):
    """
    Display the proposed changes.
    """

    print()
    print("=" * 80)
    print("RENAME PLAN")
    print("=" * 80)

    if not plan:
        print("No files need to be renamed.")
        return

    for old_path, new_path, season, episode, absolute in plan:

        print(
            f"S{season:02d}E{episode:02d}"
            f"  ->  {absolute:0{ABSOLUTE_DIGITS}d}"
        )

        print(f"    {old_path.name}")
        print(f"    {new_path.name}")
        print()


# ============================================================
# MAIN
# ============================================================

def main():

    directory = Path(DIRECTORY)

    if not directory.exists():
        raise RuntimeError(
            f"Directory does not exist:\n{directory}"
        )

    if not directory.is_dir():
        raise RuntimeError(
            f"Configured path is not a directory:\n{directory}"
        )

    if not API_KEY or API_KEY == "YOUR_TVDB_API_KEY":
        raise RuntimeError(
            "Put your TVDB API key in API_KEY at the top "
            "of the script."
        )

    # --------------------------------------------------------
    # Determine series name.
    # --------------------------------------------------------

    series_name = SERIES_NAME.strip()

    if not series_name:
        series_name = directory.name

    print()
    print("=" * 80)
    print("TVDB ABSOLUTE ORDER RENAMER")
    print("=" * 80)
    print()
    print(f"Directory: {directory}")
    print(f"Series:    {series_name}")
    print(f"Dry run:   {DRY_RUN}")
    print()

    # --------------------------------------------------------
    # Authenticate.
    # --------------------------------------------------------

    token = login()

    # --------------------------------------------------------
    # Determine TVDB series ID.
    # --------------------------------------------------------

    if TVDB_SERIES_ID is not None:

        series_id = int(TVDB_SERIES_ID)

        print(
            f"Using configured TVDB series ID: "
            f"{series_id}"
        )

    else:

        series = search_series(
            token,
            series_name,
        )

        series_id = int(
            series.get("tvdb_id")
            or series.get("id")
        )

        print()
        print(
            f"Matched TVDB series: "
            f"{series.get('name')}"
        )

        print(
            f"TVDB ID: {series_id}"
        )

    # --------------------------------------------------------
    # Get episode mapping.
    # --------------------------------------------------------

    mapping = build_episode_mapping(
        token,
        series_id,
    )

    print(
        f"Built {len(mapping)} episode mappings."
    )

    # --------------------------------------------------------
    # Find files.
    # --------------------------------------------------------

    files = find_video_files(directory)

    print(
        f"Found {len(files)} MKV/MP4 files."
    )

    # --------------------------------------------------------
    # Build rename plan.
    # --------------------------------------------------------

    plan, errors = create_rename_plan(
        files,
        mapping,
    )

    # --------------------------------------------------------
    # Report mapping errors.
    # --------------------------------------------------------

    if errors:

        print()
        print("=" * 80)
        print("ERRORS")
        print("=" * 80)

        for error in errors:
            print(error)

        print()
        print(
            "No files will be renamed until all episode "
            "mappings are valid."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Display plan.
    # --------------------------------------------------------

    print_plan(plan)

    if not plan:
        return

    # --------------------------------------------------------
    # Dry run.
    # --------------------------------------------------------

    if DRY_RUN:

        print("=" * 80)
        print("DRY RUN")
        print("=" * 80)
        print()
        print(
            "No files were changed."
        )
        print(
            "If the rename plan looks correct, set:"
        )
        print()
        print("    DRY_RUN = False")
        print()
        print(
            "and run the script again."
        )

        return

    # --------------------------------------------------------
    # Confirm and rename.
    # --------------------------------------------------------

    print("=" * 80)
    print("WARNING")
    print("=" * 80)
    print()
    print(
        f"This will rename {len(plan)} files."
    )
    print()

    answer = input(
        "Type YES to continue: "
    ).strip()

    if answer != "YES":
        print("Cancelled.")
        return

    perform_rename(plan)

    print()
    print("=" * 80)
    print("DONE")
    print("=" * 80)
    print()
    print(
        f"Renamed {len(plan)} files."
    )


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        print()
        print("Cancelled.")

    except Exception as e:
        print()
        print("ERROR:")
        print(e)
        sys.exit(1)