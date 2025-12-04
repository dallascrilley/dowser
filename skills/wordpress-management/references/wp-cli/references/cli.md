# Wp-Cli - Cli

**Pages:** 32

---

## wp media <command>

**URL:** https://developer.wordpress.org/cli/commands/media

**Contents:**
- wp media <command>
- In this article
  - Examples
  - Subcommands

Imports files as attachments, regenerates thumbnails, or lists registered image sizes.

Fix image orientation for one or more attachments.

Lists image sizes registered with WordPress.

Creates attachments from local files or URLs.

Regenerates thumbnails for one or more attachments.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Re-generate all thumbnails, without confirmation.
$ wp media regenerate --yes
Found 3 images to regenerate.
1/3 Regenerated thumbnails for "Sydney Harbor Bridge" (ID 760).
2/3 Regenerated thumbnails for "Boardwalk" (ID 757).
3/3 Regenerated thumbnails for "Sunburst Over River" (ID 756).
Success: Regenerated 3 of 3 images.

# Import a local image and set it to be the featured image for a post.
$ wp media import ~/Downloads/image.png --post_id=123 --title="A downloaded picture" --featured_image
Imported file '/home/person/Downloads/image.png' as attachment ID 1753 and attached to post 123 as f
...
```

---

## wp post-type <command>

**URL:** https://developer.wordpress.org/cli/commands/post-type

**Contents:**
- wp post-type <command>
- In this article
  - Examples
  - Subcommands

Retrieves details on the site’s registered post types.

Gets details about a registered post type.

Lists registered post types.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Get details about a post type
$ wp post-type get page --fields=name,label,hierarchical --format=json
{"name":"page","label":"Pages","hierarchical":true}

# List post types with 'post' capability type
$ wp post-type list --capability_type=post --fields=name,public
+---------------+--------+
| name          | public |
+---------------+--------+
| post          | 1      |
| attachment    | 1      |
| revision      |        |
| nav_menu_item |        |
+---------------+--------+
```

---

## wp admin

**URL:** https://developer.wordpress.org/cli/commands/admin

**Contents:**
- wp admin
- In this article
  - Global Parameters
  - Installing

Open /wp-admin/ in a browser.

Use the wp admin command by installing the command’s package:

Once the package is successfully installed, the wp admin command will appear in the list of available commands.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
wp package install wp-cli/admin-command
```

---

## wp import

**URL:** https://developer.wordpress.org/cli/commands/import

**Contents:**
- wp import
- In this article
  - Options
  - Examples
  - Global Parameters

Imports content from a given WXR file.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Import content from a WXR file
$ wp import example.wordpress.2016-06-21.xml --authors=create
Starting the import process...
Processing post #1 ("Hello world!") (post_type: post)
-- 1 of 1
-- Tue, 21 Jun 2016 05:31:12 +0000
-- Imported post as post_id #1
Success: Finished importing from 'example.wordpress.2016-06-21.xml' file.
```

---

## wp plugin <command>

**URL:** https://developer.wordpress.org/cli/commands/plugin

**Contents:**
- wp plugin <command>
- In this article
  - Examples
  - Subcommands

Manages plugins, including installs, activations, and updates.

Activates one or more plugins.

Manages plugin auto-updates.

Deactivates one or more plugins.

Deletes plugin files without deactivating or uninstalling.

Gets details about an installed plugin.

Installs one or more plugins.

Checks if a given plugin is active.

Checks if a given plugin is installed.

Gets a list of plugins.

Gets the path to a plugin or to the plugin directory.

Searches the WordPress.org plugin directory.

Reveals the status of one or all plugins.

Toggles a plugin’s activation state.

Uninstalls one or more plugins.

Updates one or more plugins.

Verifies plugin files against WordPress.org’s checksums.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Activate plugin
$ wp plugin activate hello
Plugin 'hello' activated.
Success: Activated 1 of 1 plugins.

# Deactivate plugin
$ wp plugin deactivate hello
Plugin 'hello' deactivated.
Success: Deactivated 1 of 1 plugins.

# Delete plugin
$ wp plugin delete hello
Deleted 'hello' plugin.
Success: Deleted 1 of 1 plugins.

# Install the latest version from wordpress.org and activate
$ wp plugin install bbpress --activate
Installing bbPress (2.5.9)
Downloading install package from https://downloads.wordpress.org/plugin/bbpress.2.5.9.zip...
Using cached file '/home/vagrant/.wp-cli/cache/plugin/bbpre
...
```

---

## wp menu <command>

**URL:** https://developer.wordpress.org/cli/commands/menu

**Contents:**
- wp menu <command>
- In this article
  - Examples
  - Subcommands

Lists, creates, assigns, and deletes the active theme’s navigation menus.

Deletes one or more menus.

List, add, and delete items associated with a menu.

Gets a list of menus.

Assigns, removes, and lists a menu’s locations.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create a new menu
$ wp menu create "My Menu"
Success: Created menu 200.

# List existing menus
$ wp menu list
+---------+----------+----------+-----------+-------+
| term_id | name     | slug     | locations | count |
+---------+----------+----------+-----------+-------+
| 200     | My Menu  | my-menu  |           | 0     |
| 177     | Top Menu | top-menu | primary   | 7     |
+---------+----------+----------+-----------+-------+

# Create a new menu link item
$ wp menu item add-custom my-menu Apple http://apple.com --porcelain
1922

# Assign the 'my-menu' menu to the 'primary' location
$ wp
...
```

---

## wp cli <command>

**URL:** https://developer.wordpress.org/cli/commands/cli

**Contents:**
- wp cli <command>
- In this article
  - Examples
  - Subcommands

Reviews current WP-CLI info, checks for updates, or views defined aliases.

Retrieves, sets and updates aliases for WordPress Installations.

Manages the internal WP-CLI cache,.

Checks to see if there is a newer version of WP-CLI available.

Dumps the list of installed commands, as JSON.

Generates tab completion strings.

Detects if a command exists

Prints various details about the WP-CLI environment.

Dumps the list of global parameters, as JSON or in var_export format.

Updates WP-CLI to the latest release.

Prints WP-CLI version.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Display the version currently installed.
$ wp cli version
WP-CLI 0.24.1

# Check for updates to WP-CLI.
$ wp cli check-update
Success: WP-CLI is at the latest version.

# Update WP-CLI to the latest stable release.
$ wp cli update
You have version 0.24.0. Would you like to update to 0.24.1? [y/n] y
Downloading from https://github.com/wp-cli/wp-cli/releases/download/v0.24.1/wp-cli-0.24.1.phar...
New version works. Proceeding to replace.
Success: Updated WP-CLI to 0.24.1.

# Clear the internal WP-CLI cache.
$ wp cli cache clear
Success: Cache cleared.
```

---

## Common Issues

**URL:** https://make.wordpress.org/cli/handbook/guides/common-issues

**Contents:**
- Common Issues
- In this article
  - Error: Can’t connect to the database
  - Running wp –info produces HTML output
  - PHP Fatal error: Cannot redeclare wp_unregister_GLOBALS()
  - PHP Fatal error: Call to undefined function <WordPress function>
  - PHP Fatal error: Call to undefined function cli\posix_isatty()
  - PHP Fatal error: Allowed memory size of 999999 bytes exhausted (tried to allocate 99 bytes)
  - Error: YIKES! It looks like you’re running this as root.
  - PHP notice: Undefined index on $_SERVER superglobal

a) you’re using MAMP, but WP-CLIWP-CLI WP-CLI is the Command Line Interface for WordPress, used to do administrative and development tasks in a programmatic way. The project page is http://wp-cli.org/ https://make.wordpress.org/cli/ is not using the MAMP PHPPHP PHP (recursive acronym for PHP: Hypertext Preprocessor) is a widely-used open source general-purpose scripting language that is especially suited for web development and can be embedded into HTML. https://www.php.net/manual/en/preface.php. binary.

You can check which PHP WP-CLI is using by running wp --info.

If you need to specify an alternate PHP binary, see using a custom PHP binary.

b) it’s a WordPress multisiteMultisite Multisite is a WordPress feature which allows users to create a network of sites on a single WordPress installation. Available since WordPress version 3.0, Multisite is a continuation of WPMU or WordPress Multiuser project. WordPress MultiUser project was discontinued and its features were included into WordPress core.https://codex.wordpress.org/Create_A_Network. install.

c) the database credentials in wp-config.php are actually incorrect.

If you run wp --info on a server with Phar support disabled, you may see:

When using the WP-CLI Phar, you’ll need to whitelist Phar support in your php.ini:

If you get this fatal error running the wp command, you may have moved or edited wp-config.php beyond what wp-cli supports:

One of WP-CLI’s requirements is that the line:

remains in the wp-config.php file, so if you’ve modified or moved it, put it back there. It gets matched by a regex when WP-CLI runs.

Before WP-CLI can load wp-settings.php, it needs to know all of the constants defined in wp-config.php (database connection details and so on). Because WP-CLI doesn’t want WordPress to load yet when it’s pulling the constants out of wp-config.php, it uses regex to strip the require_once(ABSPATH . 'wp-settings.php'); statement.

If you’ve modified your wp-config.php in a way that calls WordPress functions, PHP will fail out with a fatal error, as your wp-config.php is calling a WordPress function before WordPress has been loaded to define it.

Modifying wp-config.php beyond constant definitions is not best practice. You should move any modifications to a WordPress mu-plugin, which will retain the functionality of your modifications while allowing wp-cli to parse your wp-config.php without throwing a PHP error, as well as preventing other errors.

Please ensure you have the php-proce

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
$ wp --info
Content-type: text/html; charset=UTF-8
```

Example 2 (unknown):
```unknown
suhosin.executor.include.whitelist = phar
```

Example 3 (unknown):
```unknown
PHP Fatal error: Cannot redeclare wp_unregister_GLOBALS() (previously declared in /var/www/foo.com/wp-includes/load.php:18) in /var/www/foo.com/wp-includes/load.php on line 33
```

Example 4 (php):
```php
require_once(ABSPATH . 'wp-settings.php');
```

---

## wp taxonomy <command>

**URL:** https://developer.wordpress.org/cli/commands/taxonomy

**Contents:**
- wp taxonomy <command>
- In this article
  - Examples
  - Subcommands

Retrieves information about registered taxonomies.

Gets details about a registered taxonomy.

Lists registered taxonomies.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# List all taxonomies with 'post' object type.
$ wp taxonomy list --object_type=post --fields=name,public
+-------------+--------+
| name        | public |
+-------------+--------+
| category    | 1      |
| post_tag    | 1      |
| post_format | 1      |
+-------------+--------+

# Get capabilities of 'post_tag' taxonomy.
$ wp taxonomy get post_tag --field=cap
{"manage_terms":"manage_categories","edit_terms":"manage_categories","delete_terms":"manage_categories","assign_terms":"edit_posts"}
```

---

## Identify a Plugin or Theme Conflict

**URL:** https://make.wordpress.org/cli/handbook/how-to/identify-plugin-theme-conflict

**Contents:**
- Identify a Plugin or Theme Conflict

Is WP-CLIWP-CLI WP-CLI is the Command Line Interface for WordPress, used to do administrative and development tasks in a programmatic way. The project page is http://wp-cli.org/ https://make.wordpress.org/cli/ not working with your WordPress install, but you don’t know why? It might be a pluginPlugin A plugin is a piece of software containing a group of functions that can be added to a WordPress website. They can extend functionality or add new features to your WordPress websites. WordPress plugins are written in the PHP programming language and integrate seamlessly with WordPress. These can be free in the WordPress.org Plugin Directory https://wordpress.org/plugins/ or can be cost-based plugin from a third-party or theme conflicting with the WP-CLI load process.

To verify, first run wp --skip-plugins --skip-themes to execute WP-CLI without loading plugins or themes. If WP-CLI runs as expected with plugins and themes skipped, then the problem is caused by one of those plugins or the active theme.

To see if the source of the problem is the active theme, run wp --skip-themes to see if WP-CLI loads as expected.

To see if the source of the problem is an active plugin, run wp --skip-plugins=<plugin-slug> for each active plugin to see which plugin blocks the full execution of WP-CLI. For instance, skipping the Akismet plugin would be:

Or, use xargs to try the entire list of active plugins:

Improve it on GitHub: [article_title]

See list of changes: [article_title]

**Examples:**

Example 1 (unknown):
```unknown
wp --skip-plugins=akismet
```

Example 2 (unknown):
```unknown
wp plugin list --field=name --status=active --skip-plugins | xargs -n1 -I % wp --skip-plugins=% plugin get % --field=name
```

---

## Check status of a given plugin

**URL:** https://make.wordpress.org/cli/handbook/guides/doctor/doctor-check-plugin-status

**Contents:**
- Check status of a given plugin

One of the check types included in wp doctor is Plugin_Status, or the ability to assert that a given pluginPlugin A plugin is a piece of software containing a group of functions that can be added to a WordPress website. They can extend functionality or add new features to your WordPress websites. WordPress plugins are written in the PHP programming language and integrate seamlessly with WordPress. These can be free in the WordPress.org Plugin Directory https://wordpress.org/plugins/ or can be cost-based plugin from a third-party should be active, installed, or uninstalled. Although the check type isn’t use by any of the default diagnostic checks, you can use the Plugin_Status check type in your custom doctor.yml configuration file.

As an example, here are two checks using Plugin_Status, one which ensures Akismet is active on the system and other which ensures Hello Dolly is uninstalled:

Run together, you might see:

The Plugin_Status check type accepts the following options:

Improve it on GitHub: [article_title]

See list of changes: [article_title]

**Examples:**

Example 1 (unknown):
```unknown
plugin-akismet-active:
  check: Plugin_Status
  options:
    name: akismet
    status: active
plugin-hello-uninstalled:
  check: Plugin_Status
  options:
    name: hello
    status: uninstalled
```

Example 2 (unknown):
```unknown
$ wp doctor check --config=plugin-status.yml --all
+--------------------------+---------+----------------------------------------------------------------+
| name                     | status  | message                                                        |
+--------------------------+---------+----------------------------------------------------------------+
| plugin-akismet-active    | success | Plugin 'akismet' is 'active' as expected.                      |
| plugin-hello-uninstalled | error   | Plugin 'hello' is 'inactive' but expected to be 'uninstalled'. |
+--------------------------+-
...
```

---

## Write a custom check to perform an arbitrary assertion

**URL:** https://make.wordpress.org/cli/handbook/guides/doctor/doctor-write-custom-check

**Contents:**
- Write a custom check to perform an arbitrary assertion

Because wp doctor checks are built on top of a foundational abstraction, it’s relatively straightforward for you to write your own custom check. The basic requirement is that you create a class extending runcommand\Doctor\Checks\Check that implements a run() method. The run() must set a status and message based on whatever procedural logic As an example, here’s an annotated custom check to assert Akismet is activated with a valid APIAPI An API or Application Programming Interface is a software intermediary that allows programs to interact with each other and share data in limited, clearly defined ways. key:

If the class were placed in an akismet-activated.php file, you could register it with:

Then, run the config file:

Improve it on GitHub: [article_title]

See list of changes: [article_title]

**Examples:**

Example 1 (unknown):
```unknown
<?php

/**
 * Ensures Akismet is activated with the appropriate credentials.
 */
class Akismet_Activated extends runcommand\Doctor\Checks\Check {

    public function __construct( $options = array() ) {
        parent::__construct( $options );
        // Every check is to run on 'after_wp_load' by default.
        // You could instead use 'before_wp_load' or 'after_wp_config_load'
        $this->set_when( 'after_wp_load' );
    }

    public function run() {
        // If the Akismet isn't activated, bail early.
        if ( ! class_exists( 'Akismet' ) ) {
            $this->set_status( 'error
...
```

Example 2 (unknown):
```unknown
plugin-akismet-activated:
  class: Akismet_Activated
  require: akismet-activated.php
```

Example 3 (unknown):
```unknown
$ wp doctor check plugin-akismet-activated --config=doctor.yml
+--------------------------+--------+---------------------+
| name                     | status | message             |
+--------------------------+--------+---------------------+
| plugin-akismet-activated | error  | API key is missing. |
+--------------------------+--------+---------------------+
```

---

## wp post <command>

**URL:** https://developer.wordpress.org/cli/commands/post

**Contents:**
- wp post <command>
- In this article
  - Examples
  - Subcommands

Manages posts, content, and meta.

Deletes an existing post.

Launches system editor to edit post content.

Verifies whether a post exists.

Generates some posts.

Gets details about a post.

Gets a list of posts.

Adds, updates, deletes, and lists post custom fields.

Adds, updates, removes, and lists post terms.

Updates one or more existing posts.

Gets the post ID for a given URL.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create a new post.
$ wp post create --post_type=post --post_title='A sample post'
Success: Created post 123.

# Update an existing post.
$ wp post update 123 --post_status=draft
Success: Updated post 123.

# Delete an existing post.
$ wp post delete 123
Success: Trashed post 123.
```

---

## wp option <command>

**URL:** https://developer.wordpress.org/cli/commands/option

**Contents:**
- wp option <command>
- In this article
  - Examples
  - Subcommands

Retrieves and sets site options, including plugin and WordPress settings.

Adds a new option value.

Gets the value for an option.

Gets the ‘autoload’ value for an option.

Lists options and their values.

Updates a nested value in an option.

Gets a nested value from an option.

Sets the ‘autoload’ value for an option.

Updates an option value.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Get site URL.
$ wp option get siteurl
http://example.com

# Add option.
$ wp option add my_option foobar
Success: Added 'my_option' option.

# Update option.
$ wp option update my_option '{"foo": "bar"}' --format=json
Success: Updated 'my_option' option.

# Delete option.
$ wp option delete my_option
Success: Deleted 'my_option' option.
```

---

## wp db <command>

**URL:** https://developer.wordpress.org/cli/commands/db

**Contents:**
- wp db <command>
- In this article
  - Examples
  - Subcommands

Performs basic database operations using credentials stored in wp-config.php.

Checks the current status of the database.

Removes all tables with `$table_prefix` from the database.

Opens a MySQL console using credentials from wp-config.php

Displays information about a given table.

Creates a new database.

Deletes the existing database.

Exports the database to a file or to STDOUT.

Imports a database from a file or from STDIN.

Optimizes the database.

Displays the database table prefix.

Executes a SQL query against the database.

Repairs the database.

Removes all tables from the database.

Finds a string in the database.

Displays the database name and size.

Lists the database tables.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create a new database.
$ wp db create
Success: Database created.

# Drop an existing database.
$ wp db drop --yes
Success: Database dropped.

# Reset the current database.
$ wp db reset --yes
Success: Database reset.

# Execute a SQL query stored in a file.
$ wp db query < debug.sql
```

---

## Default doctor diagnostic checks

**URL:** https://make.wordpress.org/cli/handbook/guides/doctor/doctor-default-checks

**Contents:**
- Default doctor diagnostic checks

Although it’s power comes from its ability to be customized, wp doctor includes a number of default diagnostic checks considered to be recommendations for production websites.

Use wp doctor list to view these default checks:

To explain these further:

If you create a custom doctor.yml config file, you can use wp doctor list --config=<file> to view the diagnostic checks listed in the file.

Improve it on GitHub: [article_title]

See list of changes: [article_title]

---

## wp core <command>

**URL:** https://developer.wordpress.org/cli/commands/core

**Contents:**
- wp core <command>
- In this article
  - Examples
  - Subcommands

Downloads, installs, updates, and manages a WordPress installation.

Checks for WordPress updates via Version Check API.

Downloads core WordPress files.

Runs the standard WordPress installation process.

Checks if WordPress is installed.

Transforms an existing single-site installation into a multisite installation.

Installs WordPress multisite from scratch.

Updates WordPress to a newer version.

Runs the WordPress database update procedure.

Verifies WordPress files against WordPress.org’s checksums.

Displays the WordPress version.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Download WordPress core
$ wp core download --locale=nl_NL
Downloading WordPress 4.5.2 (nl_NL)...
md5 hash verified: c5366d05b521831dd0b29dfc386e56a5
Success: WordPress downloaded.

# Install WordPress
$ wp core install --url=example.com --title=Example --admin_user=supervisor --admin_password=strongpassword --admin_email=info@example.com
Success: WordPress installed successfully.

# Display the WordPress version
$ wp core version
4.5.2
```

---

## wp shell

**URL:** https://developer.wordpress.org/cli/commands/shell

**Contents:**
- wp shell
- In this article
  - Options
  - Examples
  - Global Parameters

Opens an interactive PHP console for running and testing PHP code.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (javascript):
```javascript
# Call get_bloginfo() to get the name of the site.
$ wp shell
wp> get_bloginfo( 'name' );
=> string(6) "WP-CLI"
```

---

## wp scaffold <command>

**URL:** https://developer.wordpress.org/cli/commands/scaffold

**Contents:**
- wp scaffold <command>
- In this article
  - Examples
  - Subcommands

Generates code for post types, taxonomies, plugins, child themes, etc.

Generates PHP, JS and CSS code for registering a Gutenberg block for a plugin or theme.

Generates child theme based on an existing theme.

Generate the files needed for a basic WP-CLI command.

Generate GitHub configuration files for your command.

Generate a README.md for your command.

Generate files for writing Behat tests for your command.

Generates starter code for a plugin.

Generates files needed for running PHPUnit tests in a plugin.

Generates PHP code for registering a custom post type.

Generates PHP code for registering a custom taxonomy.

Generates files needed for running PHPUnit tests in a theme.

Generates starter code for a theme based on _s.

Generates starter code for a theme based on _s.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Generate a new plugin with unit tests.
$ wp scaffold plugin sample-plugin
Success: Created plugin files.
Success: Created test files.

# Generate theme based on _s.
$ wp scaffold _s sample-theme --theme_name="Sample Theme" --author="John Doe"
Success: Created theme 'Sample Theme'.

# Generate code for post type registration in given theme.
$ wp scaffold post-type movie --label=Movie --theme=simple-life
Success: Created '/var/www/example.com/public_html/wp-content/themes/simple-life/post-types/movie.php'.
```

---

## wp config <command>

**URL:** https://developer.wordpress.org/cli/commands/config

**Contents:**
- wp config <command>
- In this article
  - Examples
  - Subcommands

Generates and reads the wp-config.php file.

Generates a wp-config.php file.

Deletes a specific constant or variable from the wp-config.php file.

Launches system editor to edit the wp-config.php file.

Gets the value of a specific constant or variable defined in wp-config.php file.

Checks whether a specific constant or variable exists in the wp-config.php file.

Determines whether value of a specific defined constant or variable is truthy.

Lists variables, constants, and file includes defined in wp-config.php file.

Gets the path to wp-config.php file.

Sets the value of a specific constant or variable defined in wp-config.php file.

Refreshes the salts defined in the wp-config.php file.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create standard wp-config.php file.
$ wp config create --dbname=testing --dbuser=wp --dbpass=securepswd --locale=ro_RO
Success: Generated 'wp-config.php' file.

# List constants and variables defined in wp-config.php file.
$ wp config list
+------------------+------------------------------------------------------------------+----------+
| key              | value                                                            | type     |
+------------------+------------------------------------------------------------------+----------+
| table_prefix     | wp_                                     
...
```

---

## wp site <command>

**URL:** https://developer.wordpress.org/cli/commands/site

**Contents:**
- wp site <command>
- In this article
  - Examples
  - Subcommands

Creates, deletes, empties, moderates, and lists one or more sites on a multisite installation.

Activates one or more sites.

Archives one or more sites.

Creates a site in a multisite installation.

Deactivates one or more sites.

Deletes a site in a multisite installation.

Empties a site of its content (posts, comments, terms, and meta).

Lists all sites in a multisite installation.

Sets one or more sites as mature.

Adds, updates, deletes, and lists site custom fields.

Adds, updates, deletes, and lists site options in a multisite installation.

Sets one or more sites as private.

Sets one or more sites as public.

Marks one or more sites as spam.

Activates a given language.

Unarchives one or more sites.

Sets one or more sites as immature.

Removes one or more sites from spam.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create site
$ wp site create --slug=example
Success: Site 3 created: www.example.com/example/

# Output a simple list of site URLs
$ wp site list --field=url
http://www.example.com/
http://www.example.com/subdir/

# Delete site
$ wp site delete 123
Are you sure you want to delete the 'http://www.example.com/example' site? [y/n] y
Success: The site at 'http://www.example.com/example' was deleted.
```

---

## Running Commands Remotely

**URL:** https://make.wordpress.org/cli/handbook/guides/running-commands-remotely

**Contents:**
- Running Commands Remotely
- In this article
- Using an SSH connection
  - Scheme
    - docker
    - docker-compose
    - vagrant
- Aliases
- Running custom commands remotely
- Making WP-CLI accessible on a remote server

WP-CLIWP-CLI WP-CLI is the Command Line Interface for WordPress, used to do administrative and development tasks in a programmatic way. The project page is http://wp-cli.org/ https://make.wordpress.org/cli/ accepts an --ssh=[<scheme>:][<user>@]<host>[:<port>][<path>] global parameter for running a command against a remote WordPress install. This argument works similarly to how the SSHSSH Secure SHell – a protocol for securely connecting to a remote system in addition to or in place of a password. connection is parameterized in tools like scp or git.

Under the hood, WP-CLI proxies commands to the ssh executable, which then passes them to the WP-CLI installed on the remote machine. The syntax for --ssh=[<scheme>:][<user>@]<host>[:<port>][<path>] is interpreted according to the following rules:

Note: you need to have a copy of WP-CLI installed on the remote server, accessible as wp.

Furthermore, --ssh=<host> won’t load your ~/.bash_profile if you have a shell alias defined, or are extending the $PATH environment variable. If this affects you, here’s a more thorough explanation of how you can make wp accessible.

You can utilize the scheme component of the ssh argument to define a shorthand for connecting to local containerized or virtualized machines.

The scheme argument is set to ssh by default, but it also accepts vagrant, docker, and docker-compose as alternate options.

To use Docker, the command is: wp rewrite flush --ssh=docker:<name> The Docker container’s name can be found by using the docker ps command.

For Docker Compose, the command is: wp option get home_url --ssh=docker-compose:<name> The Docker container’s name can be located in the docker-compose.yml file.

With Vagrant, you can use the command: wp rewrite flush --ssh=vagrant:<name>

WP-CLI aliases are shortcuts you register in your wp-cli.yml or config.yml to effortlessly run commands against any WordPress install.

For instance, when you are working locally, have registered a new rewrite rule and need to flush rewrites inside of your Vagrant-based virtual machine, you can run:

Then, once the code goes to production, you can run:

You don’t need to SSH into machines, change directories, and generally spend a full minute to get to a given WordPress install, you can just let WP-CLI know what machine to work with and it knows how to make the actual connection.

It can also easily utilize Vagrant’s ssh helper command to figure out the SSH parameters, by piping the WP-CLI command to vagrant s

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
# Run the flush command on the development environment
$ wp @dev rewrite flush
Success: Rewrite rules flushed.
```

Example 2 (unknown):
```unknown
# Run the flush command on the production environment
$ wp @prod rewrite flush
Success: Rewrite rules flushed.
```

Example 3 (unknown):
```unknown
# Run the update check on both environments
$ wp @both core check-update
Success: WordPress is at the latest version.
Success: WordPress is at the latest version.
```

Example 4 (yaml):
```yaml
@prod:
  ssh: dev_user@example.com~/webapps/production
@dev:
  ssh: vagrant@192.168.50.10/srv/www/example.dev
@local:
  ssh: vagrant:default
@both:
  - @prod
  - @dev
```

---

## wp search-replace

**URL:** https://developer.wordpress.org/cli/commands/search-replace

**Contents:**
- wp search-replace
- In this article
  - Options
  - Examples
  - Global Parameters

Searches/replaces strings in the database.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Search and replace but skip one column
$ wp search-replace 'http://example.test' 'http://example.com' --skip-columns=guid

# Run search/replace operation but dont save in database
$ wp search-replace 'foo' 'bar' wp_posts wp_postmeta wp_terms --dry-run

# Run case-insensitive regex search/replace operation (slow)
$ wp search-replace '\[foo id="([0-9]+)"' '[bar id="\1"' --regex --regex-flags='i'

# Turn your production multisite database into a local dev database
$ wp search-replace --url=example.com example.com example.test 'wp_*options' wp_blogs wp_site --network

# Search/replace to a SQL f
...
```

---

## Quick Start

**URL:** https://make.wordpress.org/cli/handbook/guides/quick-start

**Contents:**
- Quick Start
- In this article
- Introduction
- Common Terms
- Practical Examples

Congratulations! You’ve installed WP-CLI for the first time, and are ready to level-up your use of WordPress. This page contains a brief introduction to WP-CLIWP-CLI WP-CLI is the Command Line Interface for WordPress, used to do administrative and development tasks in a programmatic way. The project page is http://wp-cli.org/ https://make.wordpress.org/cli/ with some example usage.

WP-CLI is a command line interface for WordPress. The project’s goal is to offer a complete alternative to the WordPress admin; for any action you might want to perform in the WordPress admin, there should be an equivalent WP-CLI command.

For instance, because you can install a pluginPlugin A plugin is a piece of software containing a group of functions that can be added to a WordPress website. They can extend functionality or add new features to your WordPress websites. WordPress plugins are written in the PHP programming language and integrate seamlessly with WordPress. These can be free in the WordPress.org Plugin Directory https://wordpress.org/plugins/ or can be cost-based plugin from a third-party from the WordPress admin, you can also install a plugin with WP-CLI:

And, because you can also activate plugins from the WordPress admin, you can activate a plugin with WP-CLI:

One key difference between using the WordPress admin and WP-CLI: performing any action takes many fewer clicks. As you become more familiar with the command line, you’ll notice performing a given task with WP-CLI is generally much faster than performing the same task through the WordPress admin. Investing time upfront into learning how to better use WP-CLI pays dividends in the long term.

Throughout your usage of WP-CLI, you’ll hear certain terms used over and over again.

For instance, a command is an atomic unit of WP-CLI functionality. wp plugin install is one such command, as is wp plugin activate. Commands represent a name (e.g. ‘plugin install’) and a callback, and are registered with WP_CLI::add_command() (doc).

The synopsis defines which positional and associative arguments a command accepts. Let’s take a look at the synopsis for wp plugin install:

In this example, <plugin|zip|url>... is the accepted positional argument. In fact, wp plugin install accepts the same positional argument (the slug, ZIP, or URLURL A specific web address of a website or web page on the Internet, such as a website’s URL www.wordpress.org of a plugin to install) multiple times. [--version=<version>] is one of the ac

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
$ wp plugin install akismet
Installing Akismet (3.1.8)
Downloading install package from https://downloads.wordpress.org/plugin/akismet.3.1.8.zip...
Unpacking the package...
Installing the plugin...
Plugin installed successfully.
```

Example 2 (unknown):
```unknown
$ wp plugin activate akismet
Success: Plugin 'akismet' activated.
```

Example 3 (unknown):
```unknown
$ wp plugin install
usage: wp plugin install <plugin|zip|url>... [--version=<version>] [--force] [--activate] [--activate-network]
```

Example 4 (unknown):
```unknown
$ wp core download --path=wpclidemo.dev
Creating directory '/srv/www/wpclidemo.dev/'.
Downloading WordPress 4.6.1 (en_US)...
Using cached file '/home/vagrant/.wp-cli/cache/core/wordpress-4.6.1-en_US.tar.gz'...
Success: WordPress downloaded.
```

---

## wp user <command>

**URL:** https://developer.wordpress.org/cli/commands/user

**Contents:**
- wp user <command>
- In this article
  - Examples
  - Subcommands

Manages users, along with their roles, capabilities, and meta.

Adds a capability to a user.

Adds a role for a user.

Creates, updates, deletes, lists and retrieves application passwords.

Checks if a user’s password is valid or not.

Deletes one or more users from the current site.

Verifies whether a user exists.

Generates some users.

Gets details about a user.

Imports users from a CSV file.

Lists all capabilities for a user.

Adds, updates, deletes, and lists user custom fields.

Removes a user’s capability.

Removes a user’s role.

Resets the password for one or more users.

Destroys and lists a user’s sessions.

Manages signups on a multisite installation.

Marks one or more users as spam on multisite.

Adds, updates, removes, and lists user terms.

Removes one or more users from spam on multisite.

Updates an existing user.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# List user IDs
$ wp user list --field=ID
1

# Create a new user.
$ wp user create bob bob@example.com --role=author
Success: Created user 3.
Password: k9**&amp;I4vNH(&amp;

# Update an existing user.
$ wp user update 123 --display_name=Mary --user_pass=marypass
Success: Updated user 123.

# Delete user 123 and reassign posts to user 567
$ wp user delete 123 --reassign=567
Success: Removed user 123 from http://example.com.
```

---

## wp cron <command>

**URL:** https://developer.wordpress.org/cli/commands/cron

**Contents:**
- wp cron <command>
- In this article
  - Examples
  - Subcommands

Tests, runs, and deletes WP-Cron events; manages WP-Cron schedules.

Schedules, runs, and deletes WP-Cron events.

Gets WP-Cron schedules.

Tests the WP Cron spawning system and reports back its status.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Test WP Cron spawning system
$ wp cron test
Success: WP-Cron spawning is working as expected.
```

---

## Commands Cookbook

**URL:** https://make.wordpress.org/cli/handbook/guides/commands-cookbook

**Contents:**
- Commands Cookbook
- In this article
- Overview
    - Command types
- Anatomy of a command
  - Required registration arguments
  - Quick and dirty execution
  - Optional registration arguments
    - Annotating with PHPDoc
    - Shortdesc

Creating your own custom WP-CLIWP-CLI WP-CLI is the Command Line Interface for WordPress, used to do administrative and development tasks in a programmatic way. The project page is http://wp-cli.org/ https://make.wordpress.org/cli/ command can be easier than it looks — and you can use wp scaffold package (repo) to dynamically generate everything but the command itself.

WP-CLI’s goal is to offer a complete alternative to the WordPress admin; for any action you might want to perform in the WordPress admin, there should be an equivalent WP-CLI command. A command is an atomic unit of WP-CLI functionality. wp plugin install (doc) is one such command, as is wp plugin activate (doc). Commands are useful to WordPress users because they can offer simple, precise interfaces for performing complex tasks.

But, the WordPress admin is a Swiss Army knife of infinite complexity. There’s no way just this project could handle every use case. This is why WP-CLI includes a set of common internal commands, while also offering a rich internal API for third-parties to write and register their own commands.

WP-CLI commands can be distributed as standalone packages, or bundled with WordPress plugins or themes. For the former, you can use wp scaffold package (repo) to dynamically generate everything but the command itself.

Packages are to WP-CLI as plugins are to WordPress. There are distinct differences in the approach you should take to creating a WP-CLI package. While WP-CLI is an ever-growing alternative to /wp-admin it is important to note that you must first write your package to work with the WP-CLI internal APIAPI An API or Application Programming Interface is a software intermediary that allows programs to interact with each other and share data in limited, clearly defined ways. before considering how you work with WordPress APIs.

Third-party commands:

WP-CLI supports registering any callable class, function, or closure as a command. WP_CLI::add_command() (doc) is used for both internal and third-party command registration.

The synopsis of a command defines which positional and associative arguments a command accepts. Let’s take a look at the synopsis for wp plugin install:

In this example, <plugin|zip|url>... is the accepted positional argument. In fact, wp plugin install accepts the same positional argument (the slug, ZIP, or URLURL A specific web address of a website or web page on the Internet, such as a website’s URL www.wordpress.org of a plugin to install) m

*[Content truncated]*

**Examples:**

Example 1 (unknown):
```unknown
$ wp plugin install
usage: wp plugin install <plugin|zip|url>... [--version=<version>] [--force] [--activate] [--activate-network]
```

Example 2 (unknown):
```unknown
// 1. Command is a function
function foo_command( $args ) {
    WP_CLI::success( $args[0] );
}
WP_CLI::add_command( 'foo', 'foo_command' );

// 2. Command is a closure
$foo_command = function( $args ) {
    WP_CLI::success( $args[0] );
}
WP_CLI::add_command( 'foo', $foo_command );

// 3. Command is a method on a class
class Foo_Command {
    public function __invoke( $args ) {
        WP_CLI::success( $args[0] );
    }
}
WP_CLI::add_command( 'foo', 'Foo_Command' );

// 4. Command is a method on a class with constructor arguments
class Foo_Command {
    protected $bar;
    public function __con
...
```

Example 3 (unknown):
```unknown
class Foo_Command {
    public function __invoke( $args ) {
        WP_CLI::success( $args[0] );
    }
}
WP_CLI::add_command( 'core foo', 'Foo_Command' );
```

Example 4 (unknown):
```unknown
<?php
WP_CLI::success( "The script has run!" );
```

---

## wp find

**URL:** https://developer.wordpress.org/cli/commands/find

**Contents:**
- wp find
- In this article
  - Installing
  - Options
  - Available Fields
  - Examples
  - Global Parameters

Find WordPress installations on the filesystem.

Use the wp find command by installing the command’s package:

Once the package is successfully installed, the wp find command will appear in the list of available commands.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
wp package install wp-cli/find-command
```

Example 2 (unknown):
```unknown
# Find WordPress installations.
$ wp find ./
+--------------------------------------+---------------------+-------+--------+
| version_path                         | version             | depth | alias  |
+--------------------------------------+---------------------+-------+--------+
| /Users/wpcli/wp-includes/version.php | 4.8-alpha-39357-src | 2     | @wpcli |
+--------------------------------------+---------------------+-------+--------+
```

---

## wp profile <command>

**URL:** https://developer.wordpress.org/cli/commands/profile

**Contents:**
- wp profile <command>
- In this article
  - Examples
  - Installing
  - Subcommands

Quickly identify what’s slow with WordPress.

Use the wp profile command by installing the command’s package:

Once the package is successfully installed, the wp profile command will appear in the list of available commands.

Profile arbitrary code execution.

Profile execution of an arbitrary file.

Profile key metrics for WordPress hooks (actions and filters).

Profile each stage of the WordPress load process (bootstrap, main_query, template).

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# See an overview for each stage of the load process.
$ wp profile stage --fields=stage,time,cache_ratio
+------------+---------+-------------+
| stage      | time    | cache_ratio |
+------------+---------+-------------+
| bootstrap  | 0.7994s | 93.21%      |
| main_query | 0.0123s | 94.29%      |
| template   | 0.792s  | 91.23%      |
+------------+---------+-------------+
| total (3)  | 1.6037s | 92.91%      |
+------------+---------+-------------+

# Dive into hook performance for a given stage.
$ wp profile stage bootstrap --fields=hook,time,cache_ratio --spotlight
+----------------------
...
```

Example 2 (unknown):
```unknown
wp package install wp-cli/profile-command
```

---

## wp export

**URL:** https://developer.wordpress.org/cli/commands/export

**Contents:**
- wp export
- In this article
  - Options
  - Filters
  - Examples
  - Global Parameters

Exports WordPress content to a WXR file.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Export posts published by the user between given start and end date
$ wp export --dir=/tmp/ --user=admin --post_type=post --start_date=2011-01-01 --end_date=2011-12-31
Starting export process...
Writing to file /tmp/staging.wordpress.2016-05-24.000.xml
Success: All done with export.

# Export posts by IDs
$ wp export --dir=/tmp/ --post__in=123,124,125
Starting export process...
Writing to file /tmp/staging.wordpress.2016-05-24.000.xml
Success: All done with export.

# Export a random subset of content
$ wp export --post__in="$(wp post list --post_type=post --orderby=rand --posts_per_page=8 -
...
```

---

## Write a check for verifying contents of WordPress files

**URL:** https://make.wordpress.org/cli/handbook/guides/doctor/doctor-check-file-contents

**Contents:**
- Write a check for verifying contents of WordPress files

One of the check types included in wp doctor is File_Contents, or the ability to check all or a selection of WordPress files for a given regex pattern. The check type is in use by a couple of the default diagnostic checks, and you can use the File_Contents check type in your custom doctor.yml configuration file.

The File_Contents check type is the most efficient way to check WordPress files because it only iterates the filesystem once, regardless of how many file checks you’ve registered.

As an example, here are two checks using File_Contents, one which ensures sessions aren’t used by plugins and the other which ensures $_SERVER['SERVER_NAME'] isn’t used in wp-config.php:

Run together, you might see:

The File_Contents check type accepts the following options:

Improve it on GitHub: [article_title]

See list of changes: [article_title]

**Examples:**

Example 1 (unknown):
```unknown
file-sessions:
  check: File_Contents
  options:
    regex: .*(session_start|\$_SESSION).*
    only_wp_content: true
file-server-name-wp-config:
  check: File_Contents
  options:
    regex: define\(.+WP_(HOME|SITEURL).+\$_SERVER.+SERVER_NAME
    path: wp-config.php
```

Example 2 (unknown):
```unknown
$ wp doctor check --config=file-contents.yml --all
+----------------------------+---------+-----------------------------------------------------------------------------------------+
| name                       | status  | message                                                                                 |
+----------------------------+---------+-----------------------------------------------------------------------------------------+
| file-sessions              | success | All 'php' files passed check for '.*(session_start|\$_SESSION).*'.                      |
| file-server-name-wp-con
...
```

---

## wp term <command>

**URL:** https://developer.wordpress.org/cli/commands/term

**Contents:**
- wp term <command>
- In this article
  - Examples
  - Subcommands

Manages taxonomy terms and term meta, with create, delete, and list commands.

Deletes an existing term.

Generates some terms.

Gets details about a term.

Lists terms in a taxonomy.

Adds, updates, deletes, and lists term custom fields.

Migrate a term of a taxonomy to another taxonomy.

Recalculates number of posts assigned to each term.

Updates an existing term.

Command documentation is regenerated at every release. To add or update an example, please submit a pull request against the corresponding part of the codebase.

**Examples:**

Example 1 (unknown):
```unknown
# Create a new term.
$ wp term create category Apple --description="A type of fruit"
Success: Created category 199.

# Get details about a term.
$ wp term get category 199 --format=json --fields=term_id,name,slug,count
{"term_id":199,"name":"Apple","slug":"apple","count":1}

# Update an existing term.
$ wp term update category 15 --name=Apple
Success: Term updated.

# Get the term's URL.
$ wp term list post_tag --include=123 --field=url
http://example.com/tag/tips-and-tricks

# Delete post category
$ wp term delete category 15
Success: Deleted category 15.

# Recount posts assigned to each cat
...
```

---
