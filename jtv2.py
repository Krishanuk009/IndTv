#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

DEFAULT_JSON_URL = "https://m3u-86e.pages.dev/jtv-mb.json"
DEFAULT_OUTPUT = "jtv2.m3u"
DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = 30
USER_AGENT = "IndTv"

def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

def fetch_json(url: str, retries: int = DEFAULT_RETRIES, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, Any]]:
    headers = {"User-Agent": USER_AGENT}
    cache_buster = f"?t={int(time.time())}"
    full_url = url + cache_buster

    for attempt in range(1, retries + 1):
        try:
            logging.info(f"Fetching JSON (attempt {attempt}/{retries}) from {url}")
            resp = requests.get(full_url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                raise ValueError(f"Expected list, got {type(data).__name__}")
            logging.info(f"Successfully fetched {len(data)} channels")
            return data
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)
    return []

def generate_m3u(channels: List[Dict[str, Any]], source_url: str) -> str:
    lines = []
    lines.append("#EXTM3U")
    lines.append(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    lines.append("")

    for ch in channels:
        name = ch.get("name", "Unknown")
        tvg_id = ch.get("id", "")
        logo = ch.get("logo", "")
        group = ch.get("group", "Other")
        mpd_url = ch.get("mpd_url", "")
        license_url = ch.get("license_url", "")
        stream_type = ch.get("type", "").lower()
        user_agent = ch.get("user_agent")
        headers = ch.get("headers")

        stream_url = mpd_url

        extinf = (
            f'#EXTINF:-1 tvg-id="{tvg_id}" '
            f'tvg-name="{name}" '
            f'tvg-logo="{logo}" '
            f'group-title="{group}",{name}'
        )
        lines.append(extinf)

        if stream_type == "dash":
            lines.append("#KODIPROP:inputstream.adaptive.manifest_type=mpd")
        if license_url:
            lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            lines.append(f"#KODIPROP:inputstream.adaptive.license_key={license_url}")

        # VLC user-agent (only if present)
        if user_agent:
            lines.append(f"#EXTVLCOPT:http-user-agent={user_agent}")

        # VLC headers as JSON (only if present)
        if headers and isinstance(headers, dict):
            lines.append(f"#EXTHTTP:{json.dumps(headers)}")

        lines.append(stream_url)
        lines.append("")

    return "\n".join(lines)

def write_if_changed(content: str, output_path: Path) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                old_content = f.read()
            if old_content == content:
                logging.info(f"Content unchanged; skipping write to {output_path}")
                return False
        except Exception as e:
            logging.warning(f"Could not read existing file: {e}")

    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        tmp_path.replace(output_path)
        logging.info(f"Successfully written {output_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to write file: {e}")
        if tmp_path.exists():
            tmp_path.unlink()
        raise

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate M3U playlist from JSON source"
    )
    parser.add_argument(
        "-u", "--url",
        default=os.getenv("JSON_URL", DEFAULT_JSON_URL),
        help=f"JSON source URL (default: {DEFAULT_JSON_URL})"
    )
    parser.add_argument(
        "-o", "--output",
        default=os.getenv("OUTPUT_FILE", DEFAULT_OUTPUT),
        help=f"Output M3U file (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "-r", "--retries",
        type=int,
        default=int(os.getenv("RETRIES", DEFAULT_RETRIES)),
        help=f"Number of retries (default: {DEFAULT_RETRIES})"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--log-file",
        help="Write logs to this file as well"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite even if content unchanged"
    )
    args = parser.parse_args()

    setup_logging(args.verbose, args.log_file)
    logging.info("Starting M3U generator")

    try:
        channels = fetch_json(args.url, retries=args.retries)
        if not channels:
            logging.error("No channels received; aborting.")
            return 1

        content = generate_m3u(channels, args.url)

        output_path = Path(args.output)
        if args.force:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            logging.info(f"Forced write to {output_path}")
        else:
            written = write_if_changed(content, output_path)
            if not written:
                logging.info("No changes detected; file remains untouched.")

        logging.info("Done.")
        return 0

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    sys.exit(main())
