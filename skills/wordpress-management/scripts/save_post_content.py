#!/usr/bin/env python3
"""
Save Post Content with Automatic Backup

Usage:
    python save_post_content.py --host user@host --site sites/sitename --post-id POST_ID --content-file temp/content.txt
    python save_post_content.py --host user@host --site sites/sitename --post-id POST_ID --content-file temp/content.txt --no-backup

Examples:
    # Save with automatic backup
    python save_post_content.py --host user@wpengine --site sites/mysite --post-id 10883 --content-file temp/content.txt

    # Save without backup (not recommended)
    python save_post_content.py --host user@wpengine --site sites/mysite --post-id 10883 --content-file temp/content.txt --no-backup
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def create_backup(host, site, post_id, backup_dir='temp/backups'):
    """Create backup of current post content before updating."""
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_file = backup_path / f"{post_id}-{timestamp}.txt"

    cmd = f'ssh {host} "cd {site} && wp post get {post_id} --field=post_content"'

    try:
        print(f"=æ Creating backup: {backup_file}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"L Backup failed: {result.stderr}", file=sys.stderr)
            return None

        backup_file.write_text(result.stdout)
        print(f" Backup created: {backup_file}")
        return str(backup_file)

    except subprocess.TimeoutExpired:
        print(f"L Backup timed out after 30 seconds", file=sys.stderr)
        return None
    except Exception as e:
        print(f"L Backup error: {e}", file=sys.stderr)
        return None


def get_post_info(host, site, post_id):
    """Get post title and current modified timestamp."""
    cmd = f'ssh {host} "cd {site} && wp post get {post_id} --fields=post_title,post_modified --format=json"'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None, None

        import json
        data = json.loads(result.stdout)
        return data.get('post_title'), data.get('post_modified')

    except Exception:
        return None, None


def update_post_content(host, site, post_id, content_file):
    """Update WordPress post content from file."""
    content_path = Path(content_file)

    if not content_path.exists():
        print(f"L Error: Content file not found: {content_file}", file=sys.stderr)
        return False

    if not content_path.is_file():
        print(f"L Error: Path is not a file: {content_file}", file=sys.stderr)
        return False

    # Read content
    try:
        content = content_path.read_text()
    except Exception as e:
        print(f"L Error reading content file: {e}", file=sys.stderr)
        return False

    if not content.strip():
        print(f"L Error: Content file is empty", file=sys.stderr)
        return False

    # Update post via wp-cli
    cmd = f'ssh {host} "cd {site} && wp post update {post_id} --post_content=\\"\\$(cat)\\""'

    try:
        print(f"=¾ Updating post {post_id}...")
        result = subprocess.run(
            cmd,
            shell=True,
            input=content,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"L Update failed: {result.stderr}", file=sys.stderr)
            return False

        print(f" Post updated successfully")
        print(f"   {result.stdout.strip()}")
        return True

    except subprocess.TimeoutExpired:
        print(f"L Update timed out after 60 seconds", file=sys.stderr)
        return False
    except Exception as e:
        print(f"L Update error: {e}", file=sys.stderr)
        return False


def verify_update(host, site, post_id, old_modified):
    """Verify post was actually updated by checking modified timestamp."""
    title, new_modified = get_post_info(host, site, post_id)

    if not new_modified:
        print(f"   Warning: Could not verify update", file=sys.stderr)
        return False

    if old_modified and new_modified == old_modified:
        print(f"   Warning: post_modified timestamp unchanged - update may have failed", file=sys.stderr)
        return False

    print(f" Verified: post_modified updated to {new_modified}")
    if title:
        print(f"   Post: '{title}'")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Save WordPress post content with automatic backup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save with automatic backup (recommended)
  %(prog)s --host user@wpengine --site sites/mysite --post-id 10883 --content-file temp/content.txt

  # Save without backup (not recommended)
  %(prog)s --host user@wpengine --site sites/mysite --post-id 10883 --content-file temp/content.txt --no-backup
        """
    )

    parser.add_argument(
        '--host',
        required=True,
        help='SSH host (e.g., user@host.wpengine.net)'
    )

    parser.add_argument(
        '--site',
        required=True,
        help='Site path on server (e.g., sites/sitename)'
    )

    parser.add_argument(
        '--post-id',
        required=True,
        type=int,
        help='WordPress post ID'
    )

    parser.add_argument(
        '--content-file',
        required=True,
        help='Path to file containing new post content'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip automatic backup (NOT recommended)'
    )

    parser.add_argument(
        '--backup-dir',
        default='temp/backups',
        help='Directory for backups (default: temp/backups)'
    )

    args = parser.parse_args()

    print(f"=' WordPress Post Content Updater")
    print(f"   Host: {args.host}")
    print(f"   Site: {args.site}")
    print(f"   Post ID: {args.post_id}")
    print(f"   Content: {args.content_file}")
    print()

    # Get current post info
    title, old_modified = get_post_info(args.host, args.site, args.post_id)
    if title:
        print(f"=Ä Current post: '{title}'")
        print(f"   Last modified: {old_modified}")
        print()

    # Create backup unless explicitly disabled
    if not args.no_backup:
        backup_file = create_backup(
            args.host,
            args.site,
            args.post_id,
            args.backup_dir
        )

        if not backup_file:
            print(f"\nL Failed to create backup. Aborting update for safety.", file=sys.stderr)
            print(f"   Use --no-backup to skip backup (NOT recommended)", file=sys.stderr)
            sys.exit(1)
        print()
    else:
        print(f"   Warning: Skipping backup as requested")
        print()

    # Update post content
    success = update_post_content(
        args.host,
        args.site,
        args.post_id,
        args.content_file
    )

    if not success:
        print(f"\nL Update failed", file=sys.stderr)
        if not args.no_backup and 'backup_file' in locals():
            print(f"   Backup preserved at: {backup_file}", file=sys.stderr)
            print(f"   To restore:", file=sys.stderr)
            print(f"   ssh {args.host} \"cd {args.site} && wp post update {args.post_id} --post_content=\\"\\$(cat)\\"\" < {backup_file}", file=sys.stderr)
        sys.exit(1)

    print()

    # Verify update
    verify_update(args.host, args.site, args.post_id, old_modified)

    print(f"\n Complete!")
    sys.exit(0)


if __name__ == '__main__':
    main()
