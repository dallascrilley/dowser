#!/usr/bin/env python3
"""
Get WordPress Post ID by Slug

Usage:
    python get_post_id.py --host user@host --site sites/sitename --slug page-slug
    python get_post_id.py --host user@host --site sites/sitename --title "Page Title"

Examples:
    python get_post_id.py --host user@wpengine --site sites/mysite --slug about-us
    python get_post_id.py --host user@wpengine --site sites/mysite --title "About Us"
"""

import argparse
import subprocess
import json
import sys


def get_post_id_by_slug(host, site, slug):
    """Get WordPress post ID using slug via wp-cli."""
    cmd = f'ssh {host} "cd {site} && wp post list --post_type=page --name={slug} --fields=ID,post_title --format=json"'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"L Error: {result.stderr}", file=sys.stderr)
            return None

        posts = json.loads(result.stdout)

        if not posts:
            print(f"L No page found with slug: {slug}", file=sys.stderr)
            return None

        if len(posts) > 1:
            print(f"   Warning: Multiple pages found with slug '{slug}':", file=sys.stderr)
            for post in posts:
                print(f"   ID: {post['ID']}, Title: {post['post_title']}", file=sys.stderr)
            print(f"   Using first match: {posts[0]['ID']}", file=sys.stderr)

        post_id = posts[0]['ID']
        post_title = posts[0]['post_title']

        print(f" Found: ID={post_id}, Title='{post_title}'")
        return post_id

    except subprocess.TimeoutExpired:
        print(f"L Error: Command timed out after 30 seconds", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"L Error: Invalid JSON response from wp-cli", file=sys.stderr)
        print(f"   Output: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"L Error: {e}", file=sys.stderr)
        return None


def get_post_id_by_title(host, site, title):
    """Get WordPress post ID using title search via wp-cli."""
    cmd = f'ssh {host} "cd {site} && wp post list --post_type=page --s=\\"{title}\\" --fields=ID,post_title --format=json"'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"L Error: {result.stderr}", file=sys.stderr)
            return None

        posts = json.loads(result.stdout)

        if not posts:
            print(f"L No page found with title matching: {title}", file=sys.stderr)
            return None

        if len(posts) > 1:
            print(f"   Warning: Multiple pages found matching '{title}':", file=sys.stderr)
            for post in posts:
                print(f"   ID: {post['ID']}, Title: {post['post_title']}", file=sys.stderr)
            print(f"   Using first match: {posts[0]['ID']}", file=sys.stderr)

        post_id = posts[0]['ID']
        post_title = posts[0]['post_title']

        print(f" Found: ID={post_id}, Title='{post_title}'")
        return post_id

    except subprocess.TimeoutExpired:
        print(f"L Error: Command timed out after 30 seconds", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"L Error: Invalid JSON response from wp-cli", file=sys.stderr)
        print(f"   Output: {result.stdout}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"L Error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Get WordPress post ID by slug or title',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --host user@wpengine --site sites/mysite --slug about-us
  %(prog)s --host user@wpengine --site sites/mysite --title "About Us"
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

    search_group = parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument(
        '--slug',
        help='Page slug (e.g., about-us)'
    )

    search_group.add_argument(
        '--title',
        help='Page title (searches with partial match)'
    )

    args = parser.parse_args()

    if args.slug:
        post_id = get_post_id_by_slug(args.host, args.site, args.slug)
    else:
        post_id = get_post_id_by_title(args.host, args.site, args.title)

    if post_id:
        # Output just the ID for easy scripting
        print(post_id)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
