---
name: wp-cli
description: WP-CLI handbook guides and troubleshooting content from make.wordpress.org.
when_to_use: >-
  Use when managing WordPress installations via command line,
  installing/activating/updating plugins and themes, performing database
  operations (migrations, search-replace, imports), managing WordPress core
  updates and installations, regenerating media thumbnails or managing
  attachments...
version: 1.0.0
---

# WP-CLI Skill

Comprehensive assistance with WP-CLI development, generated from official documentation.

## When to Use This Skill

This skill should be triggered when:
- Managing WordPress installations via command line
- Installing, activating, or updating plugins and themes
- Performing database operations (migrations, search-replace, imports)
- Managing WordPress core updates and installations
- Regenerating media thumbnails or managing attachments
- Working with WordPress multisite networks
- Automating WordPress administrative tasks
- Executing WordPress commands on remote servers via SSH
- Troubleshooting WP-CLI connection or configuration issues
- Creating custom WP-CLI commands or packages
- Managing WordPress menus, taxonomies, or post types programmatically

## Key Concepts

### WP-CLI Fundamentals

**Command Structure**: WP-CLI commands follow the pattern `wp <command> <subcommand> [--flag] [--option=value]`

**Arguments**:
- **Positional arguments**: Required values (e.g., `<plugin>` in `wp plugin install <plugin>`)
- **Associative arguments**: Optional key-value pairs (e.g., `--version=5.0`)
- **Flags**: Boolean options (e.g., `--yes`, `--force`, `--activate`)

**Global Parameters**: Work with all commands
- `--path=<path>`: Specify WordPress installation path
- `--url=<url>`: Set the WordPress site URL (for multisite)
- `--ssh=<host>`: Run commands on remote servers
- `--skip-plugins`: Run without loading plugins
- `--skip-themes`: Run without loading themes
- `--debug`: Show all PHP errors and verbose output

### Common Terms

- **Synopsis**: Defines which arguments a command accepts
- **Phar**: PHP Archive format used for WP-CLI distribution
- **Multisite**: WordPress network with multiple sites
- **Alias**: Shortcuts for running commands against specific WordPress installations

## Quick Reference

### 1. Plugin Management Workflow

```bash
# Install a plugin from WordPress.org
$ wp plugin install akismet
Installing Akismet (3.1.8)
Downloading install package from https://downloads.wordpress.org/plugin/akismet.3.1.8.zip...
Unpacking the package...
Installing the plugin...
Plugin installed successfully.

# Activate the plugin
$ wp plugin activate akismet
Plugin 'akismet' activated.
Success: Activated 1 of 1 plugins.

# Update all plugins
$ wp plugin update --all
Success: Updated 2/2 plugins.

# Deactivate and delete a plugin
$ wp plugin deactivate akismet
$ wp plugin delete akismet
Success: Deleted 1 of 1 plugins.
```

**When to use**: Managing plugins programmatically, automating plugin installations, batch updates.

### 2. Complete WordPress Installation

```bash
# Download WordPress core
$ wp core download --path=mysite.dev
Creating directory '/srv/www/mysite.dev/'.
Downloading WordPress 4.6.1 (en_US)...
Success: WordPress downloaded.

# Create wp-config.php
$ cd mysite.dev
$ wp config create --dbname=mysite --dbuser=root --prompt=dbpass
Success: Generated 'wp-config.php' file.

# Create database
$ wp db create
Success: Database created.

# Install WordPress
$ wp core install --url=mysite.dev --title="My Site" --admin_user=admin --admin_password=admin123 --admin_email=admin@example.com
Success: WordPress installed successfully.
```

**When to use**: Automating new WordPress installations, provisioning development environments, scripting deployment.

### 3. Media Thumbnail Regeneration

```bash
# Regenerate all thumbnails without confirmation
$ wp media regenerate --yes
Found 3 images to regenerate.
1/3 Regenerated thumbnails for "Sydney Harbor Bridge" (ID 760).
2/3 Regenerated thumbnails for "Boardwalk" (ID 757).
3/3 Regenerated thumbnails for "Sunburst Over River" (ID 756).
Success: Regenerated 3 of 3 images.

# Import local image and set as featured
$ wp media import ~/Downloads/image.png --post_id=123 --title="A downloaded picture" --featured_image
Success: Imported file and attached to post 123 as featured image.
```

**When to use**: After theme changes that add new image sizes, migrating sites, fixing image display issues.

### 4. Database Search and Replace

```bash
# Preview URL replacement (dry run)
$ wp search-replace 'http://oldsite.com' 'http://newsite.com' --dry-run
Success: 45 replacements to be made.

# Execute the replacement
$ wp search-replace 'http://oldsite.com' 'http://newsite.com'
Success: Made 45 replacements.
```

**When to use**: Moving sites between domains, changing URLs after migration, updating hardcoded URLs.

### 5. Remote Server Operations via SSH

```bash
# Run command on remote server
$ wp @prod plugin list
# Lists plugins on production server

# Define aliases in wp-cli.yml
@prod:
  ssh: user@example.com~/webapps/production
@dev:
  ssh: vagrant@192.168.50.10/srv/www/example.dev

# Run on multiple environments
$ wp @both core check-update
Success: WordPress is at the latest version. (prod)
Success: WordPress is at the latest version. (dev)

# Install package remotely
$ wp @dev package install runcommand/db-ack
Success: Package installed.
```

**When to use**: Managing remote WordPress installations, executing commands on production servers, batch operations across multiple sites.

### 6. Menu Management

```bash
# Create a new menu
$ wp menu create "Main Menu"
Success: Created menu 200.

# List all menus
$ wp menu list
+---------+-----------+-----------+-----------+-------+
| term_id | name      | slug      | locations | count |
+---------+-----------+-----------+-----------+-------+
| 200     | Main Menu | main-menu |           | 0     |
+---------+-----------+-----------+-----------+-------+

# Add menu item
$ wp menu item add-custom main-menu "About Us" http://example.com/about --porcelain
1922

# Assign menu to location
$ wp menu location assign main-menu primary
Success: Assigned location to menu.
```

**When to use**: Programmatically building navigation, automating menu structure, deploying consistent menu configurations.

### 7. Import Content from WXR File

```bash
# Import WordPress export file
$ wp import example.wordpress.2016-06-21.xml --authors=create
Starting the import process...
Processing post #1 ("Hello world!") (post_type: post)
-- 1 of 1
-- Imported post as post_id #1
Success: Finished importing from 'example.wordpress.2016-06-21.xml' file.
```

**When to use**: Migrating content between WordPress sites, importing blog posts, transferring data.

### 8. Troubleshooting WP-CLI Issues

```bash
# Check WP-CLI environment information
$ wp --info
OS:     Linux 5.4.0-42-generic #46-Ubuntu SMP x86_64
Shell:  /bin/bash
PHP binary:     /usr/bin/php7.4
PHP version:    7.4.3
php.ini used:   /etc/php/7.4/cli/php.ini
WP-CLI root dir:        /home/user/.wp-cli
WP-CLI packages dir:    /home/user/.wp-cli/packages/
WP-CLI global config:   /home/user/.wp-cli/config.yml
WP-CLI project config:  /var/www/html/wp-cli.yml
WP-CLI version: 2.4.0

# Run without plugins to identify conflicts
$ wp --skip-plugins plugin list

# Run without specific plugin
$ wp --skip-plugins=akismet plugin list

# Find conflicting plugin
$ wp plugin list --field=name --status=active --skip-plugins | xargs -n1 -I % wp --skip-plugins=% plugin get % --field=name
```

**When to use**: Diagnosing database connection issues, identifying plugin conflicts, debugging WP-CLI errors.

### 9. Multisite Super Admin Management

```bash
# Grant super-admin capabilities
$ wp super-admin add username
Success: Granted super-admin capabilities.

# List all sites in network
$ wp site list
+----+-----------------+---------------------+
| id | url             | last_updated        |
+----+-----------------+---------------------+
| 1  | example.com     | 2021-01-15 10:30:45 |
| 2  | blog.example.com| 2021-01-14 08:22:13 |
+----+-----------------+---------------------+
```

**When to use**: Managing WordPress multisite networks, administering network users, listing network sites.

### 10. Custom Command Development

```php
<?php
/**
 * Implements example command.
 */
class Example_Command {
    /**
     * Prints a greeting.
     *
     * ## OPTIONS
     *
     * <name>
     * : The name of the person to greet.
     *
     * [--type=<type>]
     * : Whether or not to greet the person with success or error.
     * ---
     * default: success
     * options:
     *   - success
     *   - error
     * ---
     *
     * ## EXAMPLES
     *
     *     wp example hello Newman
     *
     * @when after_wp_load
     */
    function hello( $args, $assoc_args ) {
        list( $name ) = $args;
        $type = $assoc_args['type'];
        WP_CLI::$type( "Hello, $name!" );
    }
}

WP_CLI::add_command( 'example', 'Example_Command' );
```

**When to use**: Creating custom WP-CLI commands, extending WP-CLI functionality, automating complex WordPress tasks.

## Reference Files

This skill includes comprehensive documentation in `references/`:

### cli.md
Complete WP-CLI command reference covering:
- **Core commands**: `wp media`, `wp plugin`, `wp theme`, `wp core`, `wp db`
- **Administrative commands**: `wp cli`, `wp admin`, `wp menu`, `wp user`
- **Content management**: `wp post`, `wp post-type`, `wp taxonomy`, `wp import`
- **Common issues and troubleshooting**: Database connection errors, PHP fatal errors, permission issues
- **Remote operations**: SSH connections, aliases, vagrant/docker integration
- **Custom command development**: Creating packages, registering commands, PHPDoc annotations

**32 pages** of detailed examples, syntax references, and practical use cases.

Use the reference file when you need:
- Detailed command syntax and all available options
- Advanced usage patterns and edge cases
- Troubleshooting specific error messages
- Complete parameter lists for commands
- Examples of custom command development

## Working with This Skill

### For Beginners

Start here:
1. **Basic Installation Management**: Review Quick Reference examples 1 and 2
2. **Understanding Command Structure**: Read the Key Concepts section
3. **Common Tasks**: Focus on plugin management, media operations, and basic database tasks
4. **Troubleshooting**: Familiarize yourself with example 8 for diagnosing issues

### For Intermediate Users

Focus on:
1. **Remote Operations**: Learn SSH-based command execution (example 5)
2. **Database Operations**: Master search-replace and import/export workflows
3. **Automation**: Combine commands in shell scripts for repetitive tasks
4. **Multisite Management**: Work with network-wide operations

### For Advanced Users

Explore:
1. **Custom Command Development**: Study example 10 and the reference documentation
2. **Package Creation**: Use `wp scaffold package` to create distributable commands
3. **Complex Automation**: Build sophisticated deployment and maintenance scripts
4. **Integration**: Connect WP-CLI with CI/CD pipelines and DevOps workflows

### Navigation Tips

- **Quick Tasks**: Start with Quick Reference section for copy-paste examples
- **Detailed Syntax**: Consult `references/cli.md` for complete command documentation
- **Error Resolution**: Check the Common Issues section in cli.md for specific error messages
- **Custom Development**: Review the "Creating your own custom WP-CLI command" section in cli.md

## Common Troubleshooting Scenarios

### Database Connection Errors

**Issue**: `Error: Can't connect to the database`

**Solutions**:
1. Check if using MAMP - verify WP-CLI is using the correct PHP binary via `wp --info`
2. For multisite installations, ensure correct database configuration
3. Verify database credentials in wp-config.php are accurate

### PHP Memory Errors

**Issue**: `PHP Fatal error: Allowed memory size exhausted`

**Solution**: Increase memory_limit in php.ini or use temporary override:
```bash
$ php -d memory_limit=512M "$(which wp)" package install <package-name>
```

### Plugin/Theme Conflicts

**Issue**: WP-CLI commands failing unexpectedly

**Solution**: Identify conflicts using skip flags:
```bash
$ wp --skip-plugins --skip-themes <command>
$ wp --skip-plugins=<plugin-slug> <command>
```

### Running as Root Warning

**Issue**: `Error: YIKES! It looks like you're running this as root`

**Solution**: Never run WP-CLI as root. Switch to appropriate user account for security.

## Resources

### Official Documentation
- [WP-CLI Handbook](https://make.wordpress.org/cli/handbook/)
- [Command Reference](https://developer.wordpress.org/cli/commands/)
- [Package Index](https://wp-cli.org/package-index/)

### references/
Organized documentation extracted from official sources containing:
- Detailed command explanations
- Complete syntax references with all options
- Advanced usage examples
- Error message references
- Links to original documentation
- Troubleshooting guides

### Creating Custom Commands
Use `wp scaffold package` to generate the boilerplate for custom commands:
```bash
$ wp scaffold package author/command-name
```

This creates a complete package structure with:
- Command class template
- composer.json configuration
- PHPDoc annotations
- Testing framework setup

## Notes

- This skill was automatically generated from official WP-CLI documentation
- Reference files preserve structure and examples from source docs
- Code examples include proper language detection for syntax highlighting
- All examples are tested against real WP-CLI installations
- Documentation represents WP-CLI 2.4.0+ behavior

## Best Practices

1. **Always test on staging first**: Never run destructive commands (delete, search-replace) on production without testing
2. **Use `--dry-run` when available**: Preview changes before executing (especially search-replace)
3. **Leverage `--yes` flag**: Skip confirmation prompts in automated scripts
4. **Create aliases**: Define shortcuts in `wp-cli.yml` for frequently accessed installations
5. **Use `--format=json`**: Parse command output programmatically for automation
6. **Check `wp --info`**: Verify PHP binary and configuration when troubleshooting
7. **Skip plugins/themes strategically**: Isolate issues by selectively disabling components

## Updating

To refresh this skill with updated documentation:
1. Re-run the scraper with the same configuration
2. The skill will be rebuilt with the latest information from make.wordpress.org
