Last updated January 31, 2025

Heroku CLI plugins should provide a clear user experience, targeted primarily for human readability and usability, which delights the user, while at the same time supporting advanced users and output formats. This article provides a clear direction for designing delightful CLI plugins.

## Mission statement

The primary goal of anyone for developing CLI plugins should always be usability. Input and output should be consistent across commands to allow the user to easily learn how to interact with new commands.

## Naming the command

Plugins are made up of topics and commands. For the command `heroku apps:create`, `apps` is the topic and `create` is the command.

Generally topics are plural nouns and commands are verbs.

Ideally plugins should export a single topic, or add commands to an existing topic.

Topic and command names should always be a single, lowercase word without spaces, hyphens, underscores, or other word delimiters. Colons, however, are allowed as this is how to define subcommands (such as `heroku apps:favorites:add`). If there is no obvious way to avoid having multiple words, separate with kebab-case: `heroku pg:credentials:repair-default`

Because topics are generally nouns, the root command of a topic usually lists those nouns. So in the case of `heroku config`, it will list all the config vars for an app. Never create a `*:list` command such as `heroku config:list`.

## Description

Topic and command descriptions should be provided for all topics and commands. They should fit on 80 character width screens, begin with a lowercase character, and should not end in a period.

## Input

Input to commands is typically provided by flags and args. Stdin can also be used in cases where it is useful to stream files or information in (such as with `heroku run`).

### Flags

Flags are preferred to args. They involve a bit more typing, but make the use of the CLI clearer. For example, `heroku fork` used to accept an argument for the app to be created, as well as the standard `--app` flag to specify the source app to be forked.

So using `heroku fork` used to work like this:

```
$ heroku fork destapp -a sourceapp
```

This is confusing to the user since it isn't clear which app they are forking from and which one they are forking to. By switching to required flags, we instead expect input in this form:

```
$ heroku fork --from sourceapp --to destapp
```

This also allows the user to specify the flags in any order, and gives them the confidence that they are running the command correctly. It also allows us to show better error messages.

Ensure that descriptions are provided for all flags, that the descriptions are in lowercase, that they are concise (so as to fit on narrow screens), and that they do not end in a period to match other flag descriptions.

Flags allow us to provide autocomplete in a much better fashion than args. This is because when the user types:

```
$ heroku info --app <tab><tab>
```

We know without question that the next thing to complete is an app name and not another flag or other type of argument.

See Developing CLI Plugins for more on how to use flags.

### Arguments

Arguments are the basic way to provide input for a command. While flags are generally preferred, they are sometimes unnecessary in cases where there is only 1 argument, or the arguments are obvious and in an obvious order.

In the case of `heroku access:add`, we can specify the user we want to give access to with an argument, but the privileges are provided with a required flag:

```
$ heroku access:add user@example.com --privileges deploy
```

If this was done with only arguments, it wouldn't be clear if the privileges should go before or after the email. Using a required flag instead allows the user to specify it either way.

### Prompting

Prompting for missing input provides a nice way to show complicated options in the CLI. For example, `heroku keys:add` shows the following if multiple ssh keys are available to upload:

```
$ heroku keys:add
heroku keys:add
? Which SSH key would you like to upload? (Use arrow keys)
❯ /Users/jdickey/.ssh/id_legacy.pub
  /Users/jdickey/.ssh/id_personal.pub
  /Users/jdickey/.ssh/id_rsa.pub
```

Use inquirer to show prompts like this.

However, if prompting is required to complete a command, this means the user will not be able to script the command. Ensure that args or flags can always be provided to bypass the prompt. In this case, `heroku keys:add` can take in an argument for the path to an ssh key to skip the prompt.

## Output

In general the CLI offers 2 types of commands, output commands that show data, as well as action commands that perform an action.

### Output commands

Output commands are simply commands that display data to the user. They take many forms, but the simplest is just printing to stdout with `this.log()`:

```
this.log('output this message to the user')
// output this message to the user
```

See cli-ux for common output helpers.

### Action commands

Action commands are those that perform some remote task. For example, `heroku maintenance:on` puts an app into maintenance mode:

```
$ heroku maintenance:on --app myapp
Enabling maintenance mode for ⬢ myapp... done
```

Use cli.action() from cli-ux to show this output. Using this component ensures that warnings and errors from the API are properly displayed, the spinner is displayed correctly when it is a tty, alternative output is used when not a tty, and that the spinner will work on the right platform.

Actions are displayed on stderr because they are out-of-band information on a running task.

## Colors

Using color is encouraged in commands to help the user quickly read command output. Some nouns in the CLI such as apps and config vars have standard colors that should be used when possible:

```
import color from '@heroku-cli/color'
this.log(`this is an app: ${color.app(myapp.name)}`)
this.log(`this is a config var: ${color.configVar(myapp.name)}`)
```

See the standard colors in the heroku-cli-color repository.

When a standard color isn't available, `color` can be used to show other colors as well.

Suggested colors are magenta, cyan, blue, green, and gray. Don't forget that `.dim` and `.bright`, `.underline`, and background colors can also be used to provide more variety in color use.

Be mindful with color. Too many contrasting colors in the same place can quickly begin to compete for the user's attention. Using just a couple of colors and maybe dim/bolding existing ones can often provide enough contrast.

Yellow and red may also be used, but note that these typically are saved for errors and warning messages.

Color can be disabled by the user by adding `--no-color`, setting `COLOR=false`, or when the output is not a tty.

## Human-readable output vs machine-readable output

Terse, machine-readable output formats can also be useful but shouldn't get in the way of making beautiful CLI output. When needed, commands should offer a `--json` and/or a `--terse` flag when valuable to allow users to easily parse and script the CLI.

Care should be taken that in future releases of commands that (when possible) commands do not change their inputs and stdout after general availability in ways that will break current scripts. Generally this means additional information is OK, but modifying existing output is problematic.

### grep-parseable

Human-readable output should be grep-parseable, but not necessarily awk-parseable. For example, let's look at `heroku regions`. `heroku regions` at one point showed output like the following:

```
$ heroku regions
Common Runtime
==============
eu         Europe
us         United States

Private Spaces
==============
frankfurt  Frankfurt, Germany
london     London, United Kingdom
montreal   Montreal, Canada
Mumbai     Mumbai, India
oregon     Oregon, United States
singapore  Singapore
sydney     Sydney, Australia
tokyo      Tokyo, Japan
virginia   Virginia, United States
```

While this shows all the information about the available regions, you lose the ability to use `grep` to filter the data. Here is a better way to display this information:

```
$ heroku regions
ID         Location                 Runtime
─────────  ───────────────────────  ──────────────
eu         Europe                   Common Runtime
us         United States            Common Runtime
frankfurt  Frankfurt, Germany       Private Spaces
london     London, United Kingdom   Private Spaces
montreal   Montreal, Canada         Private Spaces
Mumbai     Mumbai, India            Private Spaces
oregon     Oregon, United States    Private Spaces
singapore  Singapore                Private Spaces
sydney     Sydney, Australia        Private Spaces
tokyo      Tokyo, Japan             Private Spaces
virginia   Virginia, United States  Private Spaces
```

Generate these tables by using cli.table() from heroku-cli-util.

Now you can use grep to filter just common runtime spaces:

```
$ heroku regions | grep "Common Runtime"
eu         Europe                   Common Runtime
us         United States            Common Runtime
```

Or if to see just tokyo:

```
$ heroku regions | grep tokyo
tokyo      Tokyo, Japan             Private Spaces
```

The older header format would make retrieving the type of the region very difficult.

Grep is useful for almost all commands and care should be taken that it always shows useful format (even if the `--context` flag is needed to show sibling rows).

### json-parseable

Sometimes printing tables can grow to be too long to reasonably fit in the CLI. Using the `--json` flag allows plugin developers to provide users with much more data but still give them the ability to parse. For example, look at `heroku releases`:

```
$ heroku releases
=== myapp Releases
v122  Attach HEROKU_POSTG…   jeff@heroku.com               2016/04/26 19:58:19 -0700
v121  Set foo config vars    jeff@heroku.com               2016/04/24 21:15:18 -0700
v120  Update REDISCLOUD b…   rediscloud@addons.heroku.com  2016/04/24 11:00:28 -0700
v119  Attach REDISCLOUD (…   jeff@heroku.com               2016/04/24 10:59:56 -0700
```

If this is run with `--json`, then the full output of each release is generated (full output not displayed for readability):

```
$ heroku releases --json
[
  {
    "description": "Attach otherdb (@ref:postgresql-rectangular-2230)",
    "user": {
      "email": "jeff@heroku.com",
      "id": "5985f8c9-a63f-42a2-bec7-40b875bb986f"
    },
    "version": 111,
    "status": "success"
  }
]
```

If a user wanted to show just the version and user for each release, jq can be used to show just those 2 fields:

```
$ heroku releases --json | jq -r '"\(.[].version) \(.[].user.email)"'
122 jeff@heroku.com
121 jeff@heroku.com
120 rediscloud@addons.heroku.com
119 jeff@heroku.com
```

Ensuring that the CLI command can support both grep and jq allows us to offer powerful scripting functionality, but without sacrificing beautiful UX that would be required with a tool like awk.

## Stdout/Stderr

Stdout should be used for all output and stderr for warning, errors and out of band information (like `cli.action()`).

## Dependency guidelines

Be mindful of dependencies. The plugin architecture allows you to install any npm package to your plugin but this comes with some cost and potential hazards.

### Native dependencies

**The Heroku CLI does not support native dependencies.** They will break when we update the node version. Also, native dependencies typically require the use of node-gyp, which requires Python, and generally is likely to have problems compiling on all user environments, especially Windows.

### Be judicious with dependencies

Use `yarn check` and `yarn outdated` to see if you have any out of date or unreferenced dependencies in your plugin.

Try to ensure you're not using too many dependencies. This uses up the user's disk space, makes install and update times longer, and could make the plugin slow. Use `npm ls` and `du -d1 node_modules | sort -n` to see how many dependencies a plugin has and how large they are.

Duplicate dependencies will be shared among other plugins if the use the same version. For example, if 2 different CLI plugins use `lodash@4.6.1`, that dependency will be shared among the 2 plugins. See the npm documentation for more on how this works.

### Use dev dependencies

Use `yarn add --dev` for packages that are only needed to work on the plugin and not for running it. This is good for testing packages, documentation packages, and linters like `tslint` or `eslint`. These packages will be installed if you run `yarn` within the plugin's repo, but not installed by the user when they run `heroku plugins:install`.

### Discouraged dependencies

The following npm packages are not recommended:

| Package | Better Alternative |  |
| --- | --- | --- |
| request | http-call | very large plugin with far too many dependencies. http-call will automatically resolve proxies, add retry logic, and handle other common situations |
| underscore | lodash | lodash has more functional tools, built with node in mind, used by many other plugins |
