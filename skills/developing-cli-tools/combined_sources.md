12-factor-cli-apps.md (===== coding/developing-cli-tools/resources/12-factor-cli-apps/12-factor-cli-apps.md =====) ====================

Title: 12 Factor CLI Apps

URL Source: https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46

Published Time: 2018-10-09T01:13:51Z


CLIs are a fantastic way to build products. Unlike web applications, they take a small fraction of the time to build and are much more powerful. With the web, you can do whatever the developer programmed. With CLIs, you can easily mash-up multiple tools together yourself to perform advanced tasks. They require more technical expertise to use, but still work well for admin tasks, power-user tasks, or developer products.

At Heroku, we’ve come up with a methodology called the [12 factor app](https://12factor.net/). It’s a set of principles designed to make great web applications that are easy to maintain. In that spirit, here are 12 CLI factors to keep in mind when building your next CLI application. Following these principles will offer CLI UX that users will love.

We’ve also built a CLI framework called [oclif](https://oclif.io/) that is designed to follow these principles to build great CLIs in Node.

1. Great help is essential
--------------------------

Having good help documentation for a CLI is extremely important. It’s far more important than when building a web application as you can’t guide the user with a UI.

A CLI should provide in-CLI help **and**help on the web (READMEs are a great place). That provides the immediate-ness of not needing to leave the terminal while also giving Google the opportunity to help your users (make sure Google is indexing the docs too btw).

Unless you already know your users will want man pages, I wouldn’t bother also outputting them as they just aren’t used often enough anymore. Novice developers are unaware of them and they don’t work on Windows. Offline support isn’t necessary if you already have in-CLI help. Still, man page support is coming to oclif because in a framework I think it makes sense. It can be solved once for all oclif CLIs to reap the benefits.

In the CLI, make sure **all**of the following displays the help. You can’t control what the user inputs so all of these **must** show help.

# list all commands

$ mycli

$ mycli --help

$ mycli help

$ mycli -h# get help for subcommand

$ mycli subcommand --help

$ mycli subcommand -h
`-h,--help` should be a reserved flag used for help only. In the case of `$ mycli subcommand help`. You can’t guarantee that `help` isn’t an argument that should be passed to the subcommand. In that case, it’s better to only show the help if it would otherwise error out with an invalid argument error. _There is actually a Heroku app named “help” which has caused this problem for me before._

[Shell completion](https://github.com/oclif/plugin-autocomplete) is another great way to offer help to the users.

In terms of the help itself, show a description of the command, description of the arguments, description of all the flags, and most importantly: provide examples of common usage of the CLI. Even if the usage is obvious to you, it’s by far the most common referenced bit of documentation users will find.

Press enter or click to view image in full size

![Image 3](https://miro.medium.com/v2/resize:fit:700/1*UdKDss6k-v36qrbcF4oBNw.png)

Of course, by building a CLI with oclif you get all this for free. Online docs, in-CLI docs, and autocomplete. We’re even working on a linter to help you enforce descriptions everywhere.

Press enter or click to view image in full size

![Image 4](https://miro.medium.com/v2/resize:fit:700/1*Wbwo-r2HRHTzGSlykqn0SQ.png)

Example oclif readme auto-documentation

2. Prefer flags to args
-----------------------

A CLI can accept 2 types of shell inputs: flags and args. Flags require a bit more typing, but make the CLI much clearer. For example, in the Heroku CLI we used to have a command called `heroku fork.` It took in a source app to copy from and a destination app to copy to. Initially, this used a flag and an argument like this:

$ heroku fork FROMAPP --app TOAPP
Using a flag and an arg, it was really confusing which was the source and which was the destination app. We changed this to use flags for both:

$ heroku fork --from FROMAPP --to TOAPP
This way it’s clear which is the source and which is the destination.

_Note that we actually removed this command from the Heroku CLI but it’s still a great example of how args can be confusing._

Sometimes args are just fine though when the argument is obvious such as `$ rm file_to_remove`. A good rule of thumb is 1 type of argument is fine, 2 types are very suspect, and 3 are never good.

For **variable** length arguments, it’s fine to have multiple arguments. (For example, `$ rm file1 file2 file3`). It’s just when they’re different types that it becomes confusing to the user.

Flags are also **much** easier to write autocomplete logic for as you know exactly what the value should be.

For CLIs that pass flags off to some other process (such as `heroku run`), the flag parser should accept a `--` argument to denote that it should stop parsing and simply pass everything down as an argument. This allows you to run a command like `heroku run -a myapp -- myscript.sh -a arg1` (This shows how `-a` can be a flag for `heroku run` but also a different `-a` is passed to the dyno).

3. What version am I on?
------------------------

Ensure you can get the CLI version through any of the following:

$ mycli version # multi only

$ mycli --version

$ mycli -V
Unless it’s a single-command CLI that also has a `-v,--verbose` flag, `$ mycli -v` should also just display the CLI version. It’s frustrating to run 3 different commands to get the version for a CLI until you find the right one.

The version command is a main place you’ll ask users for debugging information so it’s a good place to add any helpful extra information aside from just the version number that might help you diagnose issues.

I also suggest sending the version string as the User-Agent so you can debug server-side issues. (Assuming your CLI uses an API of some sort)

Press enter or click to view image in full size

![Image 5](https://miro.medium.com/v2/resize:fit:700/1*4kwxuIP4XyM6TGQAd_td9g.png)

4. Mind the streams
-------------------

Stdout and stderr provide a way for you to output messages to the user while also allowing them to redirect content to a file. For example:

$ myapp > foo.txt

Warning: something went wrong
Because this warning is on stderr, it doesn’t end up in the file. Putting the warning on stdout would not only hide the warning here, but it would be especially problematic for structured data like JSON or binary. Use stderr for errors and warnings which by default will always end up on the screen even if stdout is redirected.

Not everything on stderr is an error though. For example, you can use curl to download a file but the progress output is on stderr. This allows you to redirect the stdout while still seeing the progress.

Press enter or click to view image in full size

![Image 6](https://miro.medium.com/v2/resize:fit:700/1*Q6FL70WgULj4-tLOvx7otg.gif)

**In short: stdout is for output, stderr is for messaging.**

_If you run a subcommand in your CLI, make sure you pipe the stderr of that subcommand up to the user always. This way any issues are surfaced ultimately to the user’s screen._

5. Handle things going wrong
----------------------------

Things go wrong in CLIs much more often than in web apps. Without a UI to guide the user, the only thing we can do is display an error to the user. This is expected behavior and part of using any CLI.

First and foremost, make your errors informative. A great error message should contain the following:

1.   Error code
2.   Error title
3.   Error description (Optional)
4.   How to fix the error
5.   URL for more information

For example, if our CLI errored out with a file permission issue, we could show the following:

$ myapp dump -o myfile.out

Error: EPERM - Invalid permissions on myfile.out

Cannot write to myfile.out, file does not have write permissions.

Fix with: chmod +w myfile.out

https://github.com/jdxcode/myapp
_Just think if every CLI was this helpful how incredible it would be to be a programmer._

Get Jeff D.’s stories in your inbox
-----------------------------------

Join Medium for free to get updates from this writer.

Sometimes though you will have unhandled errors you didn’t expect the user to run into. For that, have a way to view full traceback information as well as full debug output with environment variables.

In oclif we use the [debug](https://www.npmjs.com/package/debug) module which allows us to output debug statements grouped by component if the `DEBUG` environment variable is set. We have a lot of verbose logging if debug is fully enabled which is incredibly valuable to us when debugging issues.

Error logs can also be useful for post-mortem debugging but ensure they have timestamps, truncate them occasionally so they don’t eat up space on disk, and make sure they don’t contain ansi color codes.

6. Be fancy!
------------

![Image 7](https://miro.medium.com/v2/resize:fit:563/1*ruLBiz3x3Fg7XN2pVUC31g.gif)

spinner example

Modern CLIs shouldn’t be afraid to show off. Use colors/dimming to highlight important information. Use spinners and progress bars to show long-running tasks to tell the user you’re still working. Leverage OS notifications when a very long-running task is done.

Still, you need to be able to fall back and know _when_ to fall back to more basic behavior. If the user’s stdout isn’t connected to a tty (usually this means they’re piping to a file), then don’t display colors on stdout. (likewise with stderr)

Spinners and progress bars are also not a good idea when it’s not a tty. These work by outputting ansi codes to overwrite which only works on a screen. You never want to output those codes to a file.

The user may have reasons for just not wanting this fancy output. Respect this if `TERM=dumb`, [NO_COLOR](https://no-color.org/) is set, or if they specify `--no-color`. I would also suggest adding in an app-specific `MYAPP_NOCOLOR=1` environment variable as well in case they want to disable color on just your CLI.

7. Prompt if you can
--------------------

For accepting input, if stdin is a tty then prompt rather than forcing the user to specify a flag. Never _require_ a prompt though. The user needs to be able to automate your CLI in a script so allow them to override prompts always.

Press enter or click to view image in full size

![Image 8](https://miro.medium.com/v2/resize:fit:700/1*X-PnBs4mM7BI2vTAjDXS6A.gif)

Prompt example

Another great place to add prompts is confirmation dialogs for dangerous actions. For example when destroying a Heroku app, you’ll need to type the app name again to confirm:

Press enter or click to view image in full size

![Image 9](https://miro.medium.com/v2/resize:fit:700/1*w_OYC5FXnBub9QPJQGJuQg.gif)

Checkboxes and radio buttons are a great way to improve CLI UX when you want to present options to the user visually:

![Image 10](https://miro.medium.com/v2/resize:fit:554/1*ODEhiWAn3qoZ2SSIw4yINw.gif)

transferring multiple apps to a new user with the Heroku CLI

8. Use tables
-------------

_Note that_`cli.table()`_from_[_cli-ux@5_](https://github.com/oclif/cli-ux/tree/supertable)_allows you to easily create tables following these principles._

Tables are a very common way to output data in a CLI. It’s important that each row of your output is a single ‘entry’ of data. Never output table borders. It’s noisy and a huge pain for parsing. This is an example of what **not** to do:

Press enter or click to view image in full size

![Image 11](https://miro.medium.com/v2/resize:fit:700/1*AybS19Drx08ihW4KsrNhpw.png)

By keeping each row to a single entry, you can do things like pipe to wc to get the count of lines, or grep to filter each line:

Press enter or click to view image in full size

![Image 12](https://miro.medium.com/v2/resize:fit:700/1*0mJtpvzUtursztCIrZoKrA.png)

listing files, piping to wc to count number of files, then doing the same of files with “.js” in the name. Note that wc has 3 counts: lines, words, and characters. You may also notice ls follows factor #6 where it behaves differently when piped vs when it is outputting to the screen (tty).

Be mindful of the screen width. Only show a few columns by default but allow the user to pass `--columns` with a comma-separated list of column names to add less common types.

Truncate rows that are going to spill over the current screen width unless `--no-truncate` is set.

Show column headers by default but allow them to be hidden with `--no-headers`.

Allow users to pass `--filter` to filter specific columns. (grep can usually do this, but a flag can filter on specific cell values)

Allow sorting by column with `--sort`. Allow inverse and multi-column sort as well.

Allow output in csv or json. Displaying raw output as json is a great way to output structured data. It can be manipulated with [jq](https://stedolan.github.io/jq/). While jq is incredibly useful, cut and awk are simpler tools that work better with csv data.

9. Be speedy
------------

CLIs need to start quickly. Use `$ time mycli` to benchmark your CLI. Here is a rough guide:

*   <100ms: very fast (sadly, not feasible for scripting languages)
*   100ms–500ms: fast enough, aim here
*   500ms-2s: usable, but not going to impress anyone
*   2s+: languid, users will prefer to avoid your CLI at this point

Obviously if your CLI is performing a major task like downloading a large file or something heavily CPU-bound it won’t perform as quickly. In that case, make sure to show a progress bar or at least a spinner. Even just a spinner will give the impression the CLI is much faster than it is.

_oclif is designed to have minimal overhead. Right now on my box it sits around 150ms which is about as good as node can get. It doesn’t need to require all the js files in your CLI, just the command that is about to run. So even if you have hundreds of commands, the overhead will still be 150ms._

10. Encourage contributions
---------------------------

Keep your code open source. This allows users to poke around and diagnose problems themselves. It’s healthy to the community to offer a sample in case it’s useful to others. It makes organizations look great as well.

[Make sure you pick a license of course](https://choosealicense.com/). GitHub and GitLab are great places to put your CLI and the README gives you a perfect place to provide an overview of the CLI.

Write up how to run the CLI locally and run the test suites. Offer a [contribution guideline doc](https://help.github.com/articles/setting-guidelines-for-repository-contributors/) to tell contributors what you expect in terms of commit syntax, code quality, tests, or whatever else is important for them to know.

[Add a code of conduct](https://help.github.com/articles/adding-a-code-of-conduct-to-your-project/). Even if you don’t feel that it’s necessary. It’s important to some people and they’ll feel much better by seeing one. To others they probably won’t even notice it. It’ll be helpful in the event someone is being rude and you have a document to point to.

In oclif, the [plugins system](https://oclif.io/docs/plugins.html) offers a great way for people to extend your CLI. These plugins can later be included as a core plugin to provide functionality to all users.

11. Be clear about subcommands
------------------------------

There are 2 types of CLIs: single and multi-command. Single-command CLIs are basic UNIX-style CLIs like `cp` or `grep`. Multi-commands are more like `git` or `npm` which accept a subcommand as the first argument.

If a CLI is simple and only performs one basic task, it’s good fit for a single-command CLI. Most CLIs, however, will probably benefit from using subcommands.

_Either way, if the user doesn’t pass anything arguments to the CLI, it’s always better to list the subcommands (for multi) or display the help (for single) rather than do some default behavior. Usually the user will do this before doing anything else._

When you start using subcommands, it doesn’t take long before sub-subcommands become useful (we call these “topics” in oclif). Git chooses to separate subcommands from topics with spaces:

$ git submodule add git@github.com:oclif/command
Where in the Heroku CLI we use colons:

$ heroku domains:add [www.myapp.com](http://www.myapp.com/)
Colons are preferable to help delineate the command between the arguments passed _to_ the command. The user quickly learns that argument 1 is the command and how to get help for it.

_Getting into the weeds a little bit, there is another technical reason why we prefer colons. For topic-level commands like_`$ heroku domains`_we list all the domains of an app. If we used spaces to separate commands from subcommands_**_and_**_wanted this topic-level command to accept an argument, the parser could have no way to determine if the argument was a subcommand or argument to the topic command. Therefore, using spaces to separate makes it so you cannot have topic-commands also accept an argument._

12. Follow XDG-spec
-------------------

[XDG-spec](https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html) is a great standard that should be used to find out where to put files. Unless environment variables like `XDG_CONFIG_HOME` say otherwise, use `~/.config/myapp` for config files, and `~/.local/share/myapp` for data files.

For cache files though, use `~/.cache/myapp` on Unix but on MacOS it’s better to default to `~/Library/Caches/myapp`. On Windows you can use `%LOCALAPPDATA%\myapp`.

==================== rules.md (===== coding/developing-cli-tools/resources/cli-dev-guidelines/rules.md =====) ====================

### The Basics[](http://clig.dev/#the-basics)

There are a few basic rules you need to follow. Get these wrong, and your program will be either very hard to use, or flat-out broken.

**Use a command-line argument parsing library where you can.** Either your language’s built-in one, or a good third-party one. They will normally handle arguments, flag parsing, help text, and even spelling suggestions in a sensible way.

Here are some that we like:

*   Multi-platform: [docopt](http://docopt.org/)
*   Bash: [argbash](https://argbash.dev/)
*   Go: [Cobra](https://github.com/spf13/cobra), [cli](https://github.com/urfave/cli)
*   Haskell: [optparse-applicative](https://hackage.haskell.org/package/optparse-applicative)
*   Java: [picocli](https://picocli.info/)
*   Julia: [ArgParse.jl](https://github.com/carlobaldassi/ArgParse.jl), [Comonicon.jl](https://github.com/comonicon/Comonicon.jl)
*   Kotlin: [clikt](https://ajalt.github.io/clikt/)
*   Node: [oclif](https://oclif.io/)
*   Deno: [parseArgs](https://jsr.io/@std/cli/doc/parse-args/~/parseArgs)
*   Perl: [Getopt::Long](https://metacpan.org/pod/Getopt::Long)
*   PHP: [console](https://github.com/symfony/console), [CLImate](https://climate.thephpleague.com/)
*   Python: [Argparse](https://docs.python.org/3/library/argparse.html), [Click](https://click.palletsprojects.com/), [Typer](https://github.com/tiangolo/typer)
*   Ruby: [TTY](https://ttytoolkit.org/)
*   Rust: [clap](https://docs.rs/clap)
*   Swift: [swift-argument-parser](https://github.com/apple/swift-argument-parser)

**Return zero exit code on success, non-zero on failure.** Exit codes are how scripts determine whether a program succeeded or failed, so you should report this correctly. Map the non-zero exit codes to the most important failure modes.

**Send output to `stdout`.** The primary output for your command should go to `stdout`. Anything that is machine readable should also go to `stdout`—this is where piping sends things by default.

**Send messaging to `stderr`.** Log messages, errors, and so on should all be sent to `stderr`. This means that when commands are piped together, these messages are displayed to the user and not fed into the next command.

### Help[](http://clig.dev/#help)

**Display extensive help text when asked.** Display help when passed `-h` or `--help` flags. This also applies to subcommands which might have their own help text.

**Display concise help text by default.** When `myapp` or `myapp subcommand` requires arguments to function, and is run with no arguments, display concise help text.

You can ignore this guideline if your program is interactive by default (e.g. `npm init`).

The concise help text should only include:

*   A description of what your program does.
*   One or two example invocations.
*   Descriptions of flags, unless there are lots of them.
*   An instruction to pass the `--help` flag for more information.

`jq` does this well. When you type `jq`, it displays an introductory description and an example, then prompts you to pass `jq --help` for the full listing of flags:

```
$ jq
jq - commandline JSON processor [version 1.6]

Usage:    jq [options] <jq filter> [file...]
    jq [options] --args <jq filter> [strings...]
    jq [options] --jsonargs <jq filter> [JSON_TEXTS...]

jq is a tool for processing JSON inputs, applying the given filter to
its JSON text inputs and producing the filter's results as JSON on
standard output.

The simplest filter is ., which copies jq's input to its output
unmodified (except for formatting, but note that IEEE754 is used
for number representation internally, with all that that implies).

For more advanced filters see the jq(1) manpage ("man jq")
and/or https://stedolan.github.io/jq

Example:

    $ echo '{"foo": 0}' | jq .
    {
        "foo": 0
    }

For a listing of options, use jq --help.
```

**Show full help when `-h` and `--help` is passed.** All of these should show help:

```
$ myapp
$ myapp --help
$ myapp -h
```

Ignore any other flags and arguments that are passed—you should be able to add `-h` to the end of anything and it should show help. Don’t overload `-h`.

If your program is `git`-like, the following should also offer help:

```
$ myapp help
$ myapp help subcommand
$ myapp subcommand --help
$ myapp subcommand -h
```

**Provide a support path for feedback and issues.** A website or GitHub link in the top-level help text is common.

**In help text, link to the web version of the documentation.** If you have a specific page or anchor for a subcommand, link directly to that. This is particularly useful if there is more detailed documentation on the web, or further reading that might explain the behavior of something.

**Lead with examples.** Users tend to use examples over other forms of documentation, so show them first in the help page, particularly the common complex uses. If it helps explain what it’s doing and it isn’t too long, show the actual output too.

You can tell a story with a series of examples, building your way toward complex uses.

**If you’ve got loads of examples, put them somewhere else,** in a cheat sheet command or a web page. It’s useful to have exhaustive, advanced examples, but you don’t want to make your help text really long.

For more complex use cases, e.g. when integrating with another tool, it might be appropriate to write a fully-fledged tutorial.

**Display the most common flags and commands at the start of the help text.** It’s fine to have lots of flags, but if you’ve got some really common ones, display them first. For example, the Git command displays the commands for getting started and the most commonly used subcommands first:

```
$ git
usage: git [--version] [--help] [-C <path>] [-c <name>=<value>]
           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]
           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]
           <command> [<args>]

These are common Git commands used in various situations:

start a working area (see also: git help tutorial)
   clone      Clone a repository into a new directory
   init       Create an empty Git repository or reinitialize an existing one

work on the current change (see also: git help everyday)
   add        Add file contents to the index
   mv         Move or rename a file, a directory, or a symlink
   reset      Reset current HEAD to the specified state
   rm         Remove files from the working tree and from the index

examine the history and state (see also: git help revisions)
   bisect     Use binary search to find the commit that introduced a bug
   grep       Print lines matching a pattern
   log        Show commit logs
   show       Show various types of objects
   status     Show the working tree status
…
```

**Use formatting in your help text.** Bold headings make it much easier to scan. But, try to do it in a terminal-independent way so that your users aren’t staring down a wall of escape characters.

```
$ heroku apps --help
list your apps

USAGE
  $ heroku apps

OPTIONS
  -A, --all          include apps in all teams
  -p, --personal     list apps in personal account when a default team is set
  -s, --space=space  filter by space
  -t, --team=team    team to use
  --json             output in json format

EXAMPLES
  $ heroku apps
  === My Apps
  example
  example2

  === Collaborated Apps
  theirapp   other@owner.name

COMMANDS
  apps:create     creates a new app
  apps:destroy    permanently destroy an app
  apps:errors     view app errors
  apps:favorites  list favorited apps
  apps:info       show detailed app information
  apps:join       add yourself to a team app
  apps:leave      remove yourself from a team app
  apps:lock       prevent team members from joining an app
  apps:open       open the app in a web browser
  apps:rename     rename an app
  apps:stacks     show the list of available stacks
  apps:transfer   transfer applications to another user or team
  apps:unlock     unlock an app so any team member can join
```

Note: When `heroku apps --help` is piped through a pager, the command emits no escape characters.

**If the user did something wrong and you can guess what they meant, suggest it.** For example, `brew update jq` tells you that you should run `brew upgrade jq`.

You can ask if they want to run the suggested command, but don’t force it on them. For example:

```
$ heroku pss
 ›   Warning: pss is not a heroku command.
Did you mean ps? [y/n]:
```

Rather than suggesting the corrected syntax, you might be tempted to just run it for them, as if they’d typed it right in the first place. Sometimes this is the right thing to do, but not always.

Firstly, invalid input doesn’t necessarily imply a simple typo—it can often mean the user has made a logical mistake, or misused a shell variable. Assuming what they meant can be dangerous, especially if the resulting action modifies state.

Secondly, be aware that if you change what the user typed, they won’t learn the correct syntax. In effect, you’re ruling that the way they typed it is valid and correct, and you’re committing to supporting that indefinitely. Be intentional in making that decision, and document both syntaxes.

_Further reading: [“Do What I Mean”](http://www.catb.org/~esr/jargon/html/D/DWIM.html)_

**If your command is expecting to have something piped to it and `stdin` is an interactive terminal, display help immediately and quit.** This means it doesn’t just hang, like `cat`. Alternatively, you could print a log message to `stderr`.

### Documentation[](http://clig.dev/#documentation)

The purpose of [help text](http://clig.dev/#help) is to give a brief, immediate sense of what your tool is, what options are available, and how to perform the most common tasks. Documentation, on the other hand, is where you go into full detail. It’s where people go to understand what your tool is for, what it _isn’t_ for, how it works and how to do everything they might need to do.

**Provide web-based documentation.** People need to be able to search online for your tool’s documentation, and to link other people to specific parts. The web is the most inclusive documentation format available.

**Provide terminal-based documentation.** Documentation in the terminal has several nice properties: it’s fast to access, it stays in sync with the specific installed version of the tool, and it works without an internet connection.

**Consider providing man pages.**[man pages](https://en.wikipedia.org/wiki/Man_page), Unix’s original system of documentation, are still in use today, and many users will reflexively check `man mycmd` as a first step when trying to learn about your tool. To make them easier to generate, you can use a tool like [ronn](http://rtomayko.github.io/ronn/ronn.1.html) (which can also generate your web docs).

However, not everyone knows about `man`, and it doesn’t run on all platforms, so you should also make sure your terminal docs are accessible via your tool itself. For example, `git` and `npm` make their man pages accessible via the `help` subcommand, so `npm help ls` is equivalent to `man npm-ls`.

```
NPM-LS(1)                                                            NPM-LS(1)

NAME
       npm-ls - List installed packages

SYNOPSIS
         npm ls [[<@scope>/]<pkg> ...]

         aliases: list, la, ll

DESCRIPTION
       This command will print to stdout all the versions of packages that are
       installed, as well as their dependencies, in a tree-structure.

       ...
```

### Output[](http://clig.dev/#output)

**Human-readable output is paramount.** Humans come first, machines second. The most simple and straightforward heuristic for whether a particular output stream (`stdout` or `stderr`) is being read by a human is _whether or not it’s a TTY_. Whatever language you’re using, it will have a utility or library for doing this (e.g. [Python](https://stackoverflow.com/questions/858623/how-to-recognize-whether-a-script-is-running-on-a-tty), [Node](https://nodejs.org/api/process.html#process_a_note_on_process_i_o), [Go](https://github.com/mattn/go-isatty)).

_Further reading on [what a TTY is](https://unix.stackexchange.com/a/4132)._

**Have machine-readable output where it does not impact usability.** Streams of text is the universal interface in UNIX. Programs typically output lines of text, and programs typically expect lines of text as input, therefore you can compose multiple programs together. This is normally done to make it possible to write scripts, but it can also help the usability for humans using programs. For example, a user should be able to pipe output to `grep` and it should do what they expect.

> “Expect the output of every program to become the input to another, as yet unknown, program.” — [Doug McIlroy](http://web.archive.org/web/20220609080931/https://homepage.cs.uri.edu/~thenry/resources/unix_art/ch01s06.html)

**If human-readable output breaks machine-readable output, use `--plain` to display output in plain, tabular text format for integration with tools like `grep` or `awk`.** In some cases, you might need to output information in a different way to make it human-readable.

For example, if you are displaying a line-based table, you might choose to split a cell into multiple lines, fitting in more information while keeping it within the width of the screen. This breaks the expected behavior of there being one piece of data per line, so you should provide a `--plain` flag for scripts, which disables all such manipulation and outputs one record per line.

**Display output as formatted JSON if `--json` is passed.** JSON allows for more structure than plain text, so it makes it much easier to output and handle complex data structures. [`jq`](https://stedolan.github.io/jq/) is a common tool for working with JSON on the command-line, and there is now a [whole ecosystem of tools](https://ilya-sher.org/2018/04/10/list-of-json-tools-for-command-line/) that output and manipulate JSON.

It is also widely used on the web, so by using JSON as the input and output of programs, you can pipe directly to and from web services using `curl`.

**Display output on success, but keep it brief.** Traditionally, when nothing is wrong, UNIX commands display no output to the user. This makes sense when they’re being used in scripts, but can make commands appear to be hanging or broken when used by humans. For example, `cp` will not print anything, even if it takes a long time.

It’s rare that printing nothing at all is the best default behavior, but it’s usually best to err on the side of less.

For instances where you do want no output (for example, when used in shell scripts), to avoid clumsy redirection of `stderr` to `/dev/null`, you can provide a `-q` option to suppress all non-essential output.

**If you change state, tell the user.** When a command changes the state of a system, it’s especially valuable to explain what has just happened, so the user can model the state of the system in their head—particularly if the result doesn’t directly map to what the user requested.

For example, `git push` tells you exactly what it is doing, and what the new state of the remote branch is:

```
$ git push
Enumerating objects: 18, done.
Counting objects: 100% (18/18), done.
Delta compression using up to 8 threads
Compressing objects: 100% (10/10), done.
Writing objects: 100% (10/10), 2.09 KiB | 2.09 MiB/s, done.
Total 10 (delta 8), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (8/8), completed with 8 local objects.
To github.com:replicate/replicate.git
 + 6c22c90...a2a5217 bfirsh/fix-delete -> bfirsh/fix-delete
```

**Make it easy to see the current state of the system.** If your program does a lot of complex state changes and it is not immediately visible in the filesystem, make sure you make this easy to view.

For example, `git status` tells you as much information as possible about the current state of your Git repository, and some hints at how to modify the state:

```
$ git status
On branch bfirsh/fix-delete
Your branch is up to date with 'origin/bfirsh/fix-delete'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   cli/pkg/cli/rm.go

no changes added to commit (use "git add" and/or "git commit -a")
```

**Suggest commands the user should run.** When several commands form a workflow, suggesting to the user commands they can run next helps them learn how to use your program and discover new functionality. For example, in the `git status` output above, it suggests commands you can run to modify the state you are viewing.

**Actions crossing the boundary of the program’s internal world should usually be explicit.** This includes things like:

*   Reading or writing files that the user didn’t explicitly pass as arguments (unless those files are storing internal program state, such as a cache).
*   Talking to a remote server, e.g. to download a file.

**Increase information density—with ASCII art!** For example, `ls` shows permissions in a scannable way. When you first see it, you can ignore most of the information. Then, as you learn how it works, you pick out more patterns over time.

```
-rw-r--r-- 1 root root     68 Aug 22 23:20 resolv.conf
lrwxrwxrwx 1 root root     13 Mar 14 20:24 rmt -> /usr/sbin/rmt
drwxr-xr-x 4 root root   4.0K Jul 20 14:51 security
drwxr-xr-x 2 root root   4.0K Jul 20 14:53 selinux
-rw-r----- 1 root shadow  501 Jul 20 14:44 shadow
-rw-r--r-- 1 root root    116 Jul 20 14:43 shells
drwxr-xr-x 2 root root   4.0K Jul 20 14:57 skel
-rw-r--r-- 1 root root      0 Jul 20 14:43 subgid
-rw-r--r-- 1 root root      0 Jul 20 14:43 subuid
```

**Use color with intention.** For example, you might want to highlight some text so the user notices it, or use red to indicate an error. Don’t overuse it—if everything is a different color, then the color means nothing and only makes it harder to read.

**Disable color if your program is not in a terminal or the user requested it.** These things should disable colors:

*   `stdout` or `stderr` is not an interactive terminal (a TTY). It’s best to individually check—if you’re piping `stdout` to another program, it’s still useful to get colors on `stderr`.
*   The `NO_COLOR` environment variable is set and it is not empty (regardless of its value).
*   The `TERM` environment variable has the value `dumb`.
*   The user passes the option `--no-color`.
*   You may also want to add a `MYAPP_NO_COLOR` environment variable in case users want to disable color specifically for your program.

_Further reading: [no-color.org](https://no-color.org/), [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)_

**If `stdout` is not an interactive terminal, don’t display any animations.** This will stop progress bars turning into Christmas trees in CI log output.

**Use symbols and emoji where it makes things clearer.** Pictures can be better than words if you need to make several things distinct, catch the user’s attention, or just add a bit of character. Be careful, though—it can be easy to overdo it and make your program look cluttered or feel like a toy.

For example, [yubikey-agent](https://github.com/FiloSottile/yubikey-agent) uses emoji to add structure to the output so it isn’t just a wall of text, and a ❌ to draw your attention to an important piece of information:

```
$ yubikey-agent -setup
🔐 The PIN is up to 8 numbers, letters, or symbols. Not just numbers!
❌ The key will be lost if the PIN and PUK are locked after 3 incorrect tries.

Choose a new PIN/PUK: 
Repeat the PIN/PUK: 

🧪 Retriculating splines …

✅ Done! This YubiKey is secured and ready to go.
🤏 When the YubiKey blinks, touch it to authorize the login.

🔑 Here's your new shiny SSH public key:
ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBCEJ/
UwlHnUFXgENO3ifPZd8zoSKMxESxxot4tMgvfXjmRp5G3BGrAnonncE7Aj11pn3SSYgEcrrn2sMyLGpVS0=

💭 Remember: everything breaks, have a backup plan for when this YubiKey does.
```

**By default, don’t output information that’s only understandable by the creators of the software.** If a piece of output serves only to help you (the developer) understand what your software is doing, it almost certainly shouldn’t be displayed to normal users by default—only in verbose mode.

Invite usability feedback from outsiders and people who are new to your project. They’ll help you see important issues that you are too close to the code to notice.

**Don’t treat `stderr` like a log file, at least not by default.** Don’t print log level labels (`ERR`, `WARN`, etc.) or extraneous contextual information, unless in verbose mode.

**Use a pager (e.g. `less`) if you are outputting a lot of text.** For example, `git diff` does this by default. Using a pager can be error-prone, so be careful with your implementation such that you don’t make the experience worse for the user. Use a pager only if `stdin` or `stdout` is an interactive terminal.

A good sensible set of options to use for `less` is `less -FIRX`. This does not page if the content fills one screen, ignores case when you search, enables color and formatting, and leaves the contents on the screen when `less` quits.

There might be libraries in your language that are more robust than piping to `less`. For example, [pypager](https://github.com/prompt-toolkit/pypager) in Python.

### Errors[](http://clig.dev/#errors)

One of the most common reasons to consult documentation is to fix errors. If you can make errors into documentation, then this will save the user loads of time.

**Catch errors and rewrite them for humans.** If you’re expecting an error to happen, catch it and rewrite the error message to be useful. Think of it like a conversation, where the user has done something wrong and the program is guiding them in the right direction. Example: “Can’t write to file.txt. You might need to make it writable by running ‘chmod +w file.txt’.”

**Signal-to-noise ratio is crucial.** The more irrelevant output you produce, the longer it’s going to take the user to figure out what they did wrong. If your program produces multiple errors of the same type, consider grouping them under a single explanatory header instead of printing many similar-looking lines.

**Consider where the user will look first.** Put the most important information at the end of the output. The eye will be drawn to red text, so use it intentionally and sparingly.

**If there is an unexpected or unexplainable error, provide debug and traceback information, and instructions on how to submit a bug.** That said, don’t forget about the signal-to-noise ratio: you don’t want to overwhelm the user with information they don’t understand. Consider writing the debug log to a file instead of printing it to the terminal.

**Make it effortless to submit bug reports.** One nice thing you can do is provide a URL and have it pre-populate as much information as possible.

_Further reading: [Google: Writing Helpful Error Messages](https://developers.google.com/tech-writing/error-messages), [Nielsen Norman Group: Error-Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines)_

### Arguments and flags[](http://clig.dev/#arguments-and-flags)

A note on terminology:

*   _Arguments_, or _args_, are positional parameters to a command. For example, the file paths you provide to `cp` are args. The order of args is often important: `cp foo bar` means something different from `cp bar foo`.
*   _Flags_ are named parameters, denoted with either a hyphen and a single-letter name (`-r`) or a double hyphen and a multiple-letter name (`--recursive`). They may or may not also include a user-specified value (`--file foo.txt`, or `--file=foo.txt`). The order of flags, generally speaking, does not affect program semantics.

**Prefer flags to args.** It’s a bit more typing, but it makes it much clearer what is going on. It also makes it easier to make changes to how you accept input in the future. Sometimes when using args, it’s impossible to add new input without breaking existing behavior or creating ambiguity.

_Citation: [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)._

**Have full-length versions of all flags.** For example, have both `-h` and `--help`. Having the full version is useful in scripts where you want to be verbose and descriptive, and you don’t have to look up the meaning of flags everywhere.

_Citation: [GNU Coding Standards](https://www.gnu.org/prep/standards/html\_node/Command\_002dLine-Interfaces.html)._

**Only use one-letter flags for commonly used flags,** particularly at the top-level when using subcommands. That way you don’t “pollute” your namespace of short flags, forcing you to use convoluted letters and cases for flags you add in the future.

**Multiple arguments are fine for simple actions against multiple files.** For example, `rm file1.txt file2.txt file3.txt`. This also makes it work with globbing: `rm *.txt`.

**If you’ve got two or more arguments for different things, you’re probably doing something wrong.** The exception is a common, primary action, where the brevity is worth memorizing. For example, `cp <source> <destination>`.

_Citation: [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)._

**Use standard names for flags, if there is a standard.** If another commonly used command uses a flag name, it’s best to follow that existing pattern. That way, a user doesn’t have to remember two different options (and which command it applies to), and users can even guess an option without having to look at the help text.

Here’s a list of commonly used options:

*   `-a`, `--all`: All. For example, `ps`, `fetchmail`.
*   `-d`, `--debug`: Show debugging output.
*   `-f`, `--force`: Force. For example, `rm -f` will force the removal of files, even if it thinks it does not have permission to do it. This is also useful for commands which are doing something destructive that usually require user confirmation, but you want to force it to do that destructive action in a script.
*   `--json`: Display JSON output. See the [output](http://clig.dev/#output) section.
*   `-h`, `--help`: Help. This should only mean help. See the [help](http://clig.dev/#help) section.
*   `-n`, `--dry-run`: Dry run. Do not run the command, but describe the changes that would occur if the command were run. For example, `rsync`, `git add`.
*   `--no-input`: See the [interactivity](http://clig.dev/#interactivity) section.
*   `-o`, `--output`: Output file. For example, `sort`, `gcc`.
*   `-p`, `--port`: Port. For example, `psql`, `ssh`.
*   `-q`, `--quiet`: Quiet. Display less output. This is particularly useful when displaying output for humans that you might want to hide when running in a script.
*   `-u`, `--user`: User. For example, `ps`, `ssh`.
*   `--version`: Version.
*   `-v`: This can often mean either verbose or version. You might want to use `-d` for verbose and this for version, or for nothing to avoid confusion.

**Make the default the right thing for most users.** Making things configurable is good, but most users are not going to find the right flag and remember to use it all the time (or alias it). If it’s not the default, you’re making the experience worse for most of your users.

For example, `ls` has terse default output to optimize for scripts and other historical reasons, but if it were designed today, it would probably default to `ls -lhF`.

**Prompt for user input.** If a user doesn’t pass an argument or flag, prompt for it. (See also: [Interactivity](http://clig.dev/#interactivity))

**Never _require_ a prompt.** Always provide a way of passing input with flags or arguments. If `stdin` is not an interactive terminal, skip prompting and just require those flags/args.

**Confirm before doing anything dangerous.** A common convention is to prompt for the user to type `y` or `yes` if running interactively, or requiring them to pass `-f` or `--force` otherwise.

“Dangerous” is a subjective term, and there are differing levels of danger:

*   **Mild:** A small, local change such as deleting a file. You might want to prompt for confirmation, you might not. For example, if the user is explicitly running a command called something like “delete,” you probably don’t need to ask.
*   **Moderate:** A bigger local change like deleting a directory, a remote change like deleting a resource of some kind, or a complex bulk modification that can’t be easily undone. You usually want to prompt for confirmation here. Consider giving the user a way to “dry run” the operation so they can see what’ll happen before they commit to it.
*   **Severe:** Deleting something complex, like an entire remote application or server. You don’t just want to prompt for confirmation here—you want to make it hard to confirm by accident. Consider asking them to type something non-trivial such as the name of the thing they’re deleting. Let them alternatively pass a flag such as `--confirm="name-of-thing"`, so it’s still scriptable.

Consider whether there are non-obvious ways to accidentally destroy things. For example, imagine a situation where changing a number in a configuration file from 10 to 1 means that 9 things will be implicitly deleted—this should be considered a severe risk, and should be difficult to do by accident.

**If input or output is a file, support `-` to read from `stdin` or write to `stdout`.** This lets the output of another command be the input of your command and vice versa, without using a temporary file. For example, `tar` can extract files from `stdin`:

```
$ curl https://example.com/something.tar.gz | tar xvf -
```

**If a flag can accept an optional value, allow a special word like “none”.** For example, `ssh -F` takes an optional filename of an alternative `ssh_config` file, and `ssh -F none` runs SSH with no config file. Don’t just use a blank value—this can make it ambiguous whether arguments are flag values or arguments.

**If possible, make arguments, flags and subcommands order-independent.** A lot of CLIs, especially those with subcommands, have unspoken rules on where you can put various arguments. For example a command might have a `--foo` flag that only works if you put it before the subcommand:

```
mycmd --foo=1 subcmd
works

$ mycmd subcmd --foo=1
unknown flag: --foo
```

This can be very confusing for the user—especially given that one of the most common things users do when trying to get a command to work is to hit the up arrow to get the last invocation, stick another option on the end, and run it again. If possible, try to make both forms equivalent, although you might run up against the limitations of your argument parser.

**Do not read secrets directly from flags.** When a command accepts a secret, e.g. via a `--password` flag, the flag value will leak the secret into `ps` output and potentially shell history. And, this sort of flag encourages the use of insecure environment variables for secrets. (Environment variables are insecure because they can often be read by other users, their values end up in debug logs, etc.)

Consider accepting sensitive data only via files, e.g. with a `--password-file` flag, or via `stdin`. A `--password-file` flag allows a secret to be passed in discreetly, in a wide variety of contexts.

(It’s possible to pass a file’s contents into a flag in Bash by using `--password $(< password.txt)`. This approach has the same security problems mentioned above. It’s best avoided.)

### Interactivity[](http://clig.dev/#interactivity)

**Only use prompts or interactive elements if `stdin` is an interactive terminal (a TTY).** This is a pretty reliable way to tell whether you’re piping data into a command or whether it’s being run in a script, in which case a prompt won’t work and you should throw an error telling the user what flag to pass.

**If `--no-input` is passed, don’t prompt or do anything interactive.** This allows users an explicit way to disable all prompts in commands. If the command requires input, fail and tell the user how to pass the information as a flag.

**If you’re prompting for a password, don’t print it as the user types.** This is done by turning off echo in the terminal. Your language should have helpers for this.

**Let the user escape.** Make it clear how to get out. (Don’t do what vim does.) If your program hangs on network I/O etc, always make Ctrl-C still work. If it’s a wrapper around program execution where Ctrl-C can’t quit (SSH, tmux, telnet, etc), make it clear how to do that. For example, SSH allows escape sequences with the `~` escape character.

### Subcommands[](http://clig.dev/#subcommands)

If you’ve got a tool that’s sufficiently complex, you can reduce its complexity by making a set of subcommands. If you have several tools that are very closely related, you can make them easier to use and discover by combining them into a single command (for example, RCS vs. Git).

They’re useful for sharing stuff—global flags, help text, configuration, storage mechanisms.

**Be consistent across subcommands.** Use the same flag names for the same things, have similar output formatting, etc.

**Use consistent names for multiple levels of subcommand.** If a complex piece of software has lots of objects and operations that can be performed on those objects, it is a common pattern to use two levels of subcommand for this, where one is a noun and one is a verb. For example, `docker container create`. Be consistent with the verbs you use across different types of objects.

Either `noun verb` or `verb noun` ordering works, but `noun verb` seems to be more common.

_Further reading: [User experience, CLIs, and breaking the world, by John Starich](https://uxdesign.cc/user-experience-clis-and-breaking-the-world-baed8709244f)._

**Don’t have ambiguous or similarly-named commands.** For example, having two subcommands called “update” and “upgrade” is quite confusing. You might want to use different words, or disambiguate with extra words.

### Robustness[](http://clig.dev/#robustness-guidelines)

**Validate user input.** Everywhere your program accepts data from the user, it will eventually be given bad data. Check early and bail out before anything bad happens, and [make the errors understandable](http://clig.dev/#errors).

**Responsive is more important than fast.** Print something to the user in <100ms. If you’re making a network request, print something before you do it so it doesn’t hang and look broken.

**Show progress if something takes a long time.** If your program displays no output for a while, it will look broken. A good spinner or progress indicator can make a program appear to be faster than it is.

Ubuntu 20.04 has a nice progress bar that sticks to the bottom of the terminal.

If the progress bar gets stuck in one place for a long time, the user won’t know if stuff is still happening or if the program’s crashed. It’s good to show estimated time remaining, or even just have an animated component, to reassure them that you’re still working on it.

There are many good libraries for generating progress bars. For example, [tqdm](https://github.com/tqdm/tqdm) for Python, [schollz/progressbar](https://github.com/schollz/progressbar) for Go, and [node-progress](https://github.com/visionmedia/node-progress) for Node.js.

**Do stuff in parallel where you can, but be thoughtful about it.** It’s already difficult to report progress in the shell; doing it for parallel processes is ten times harder. Make sure it’s robust, and that the output isn’t confusingly interleaved. If you can use a library, do so—this is code you don’t want to write yourself. Libraries like [tqdm](https://github.com/tqdm/tqdm) for Python and [schollz/progressbar](https://github.com/schollz/progressbar) for Go support multiple progress bars natively.

The upside is that it can be a huge usability gain. For example, `docker pull`’s multiple progress bars offer crucial insight into what’s going on.

```
$ docker image pull ruby
Using default tag: latest
latest: Pulling from library/ruby
6c33745f49b4: Pull complete 
ef072fc32a84: Extracting [================================================>  ]  7.569MB/7.812MB
c0afb8e68e0b: Download complete 
d599c07d28e6: Download complete 
f2ecc74db11a: Downloading [=======================>                           ]  89.11MB/192.3MB
3568445c8bf2: Download complete 
b0efebc74f25: Downloading [===========================================>       ]  19.88MB/22.88MB
9cb1ba6838a0: Download complete
```

One thing to be aware of: hiding logs behind progress bars when things go _well_ makes it much easier for the user to understand what’s going on, but if there is an error, make sure you print out the logs. Otherwise, it will be very hard to debug.

**Make things time out.** Allow network timeouts to be configured, and have a reasonable default so it doesn’t hang forever.

**Make it recoverable.** If the program fails for some transient reason (e.g. the internet connection went down), you should be able to hit `<up>` and `<enter>` and it should pick up from where it left off.

**Make it crash-only.** This is the next step up from idempotence. If you can avoid needing to do any cleanup after operations, or you can defer that cleanup to the next run, your program can exit immediately on failure or interruption. This makes it both more robust and more responsive.

_Citation: [Crash-only software: More than meets the eye](https://lwn.net/Articles/191059/)._

**People are going to misuse your program.** Be prepared for that. They will wrap it in scripts, use it on bad internet connections, run many instances of it at once, and use it in environments you haven’t tested in, with quirks you didn’t anticipate. (Did you know macOS filesystems are case-insensitive but also case-preserving?)

### Future-proofing[](http://clig.dev/#future-proofing)

In software of any kind, it’s crucial that interfaces don’t change without a lengthy and well-documented deprecation process. Subcommands, arguments, flags, configuration files, environment variables: these are all interfaces, and you’re committing to keeping them working. ([Semantic versioning](https://semver.org/) can only excuse so much change; if you’re putting out a major version bump every month, it’s meaningless.)

**Keep changes additive where you can.** Rather than modify the behavior of a flag in a backwards-incompatible way, maybe you can add a new flag—as long as it doesn’t bloat the interface too much. (See also: [Prefer flags to args](http://clig.dev/#arguments-and-flags).)

**Warn before you make a non-additive change.** Eventually, you’ll find that you can’t avoid breaking an interface. Before you do, forewarn your users in the program itself: when they pass the flag you’re looking to deprecate, tell them it’s going to change soon. Make sure there’s a way they can modify their usage today to make it future-proof, and tell them how to do it.

If possible, you should detect when they’ve changed their usage and not show the warning any more: now they won’t notice a thing when you finally roll out the change.

**Changing output for humans is usually OK.** The only way to make an interface easy to use is to iterate on it, and if the output is considered an interface, then you can’t iterate on it. Encourage your users to use `--plain` or `--json` in scripts to keep output stable (see [Output](http://clig.dev/#output)).

**Don’t have a catch-all subcommand.** If you have a subcommand that’s likely to be the most-used one, you might be tempted to let people omit it entirely for brevity’s sake. For example, say you have a `run` command that wraps an arbitrary shell command:

```
$ mycmd run echo "hello world"
```

You could make it so that if the first argument to `mycmd` isn’t the name of an existing subcommand, you assume the user means `run`, so they can just type this:

```
$ mycmd echo "hello world"
```

This has a serious drawback, though: now you can never add a subcommand named `echo`—or _anything at all_—without risking breaking existing usages. If there’s a script out there that uses `mycmd echo`, it will do something entirely different after that user upgrades to the new version of your tool.

**Don’t allow arbitrary abbreviations of subcommands.** For example, say your command has an `install` subcommand. When you added it, you wanted to save users some typing, so you allowed them to type any non-ambiguous prefix, like `mycmd ins`, or even just `mycmd i`, and have it be an alias for `mycmd install`. Now you’re stuck: you can’t add any more commands beginning with `i`, because there are scripts out there that assume `i` means `install`.

There’s nothing wrong with aliases—saving on typing is good—but they should be explicit and remain stable.

**Don’t create a “time bomb.”** Imagine it’s 20 years from now. Will your command still run the same as it does today, or will it stop working because some external dependency on the internet has changed or is no longer maintained? The server most likely to not exist in 20 years is the one that you are maintaining right now. (But don’t build in a blocking call to Google Analytics either.)

### Signals and control characters[](http://clig.dev/#signals)

**If a user hits Ctrl-C (the INT signal), exit as soon as possible.** Say something immediately, before you start clean-up. Add a timeout to any clean-up code so it can’t hang forever.

**If a user hits Ctrl-C during clean-up operations that might take a long time, skip them.** Tell the user what will happen when they hit Ctrl-C again, in case it is a destructive action.

For example, when quitting Docker Compose, you can hit Ctrl-C a second time to force your containers to stop immediately instead of shutting them down gracefully.

```
$  docker-compose up
…
^CGracefully stopping... (press Ctrl+C again to force)
```

Your program should expect to be started in a situation where clean-up has not been run. (See [Crash-only software: More than meets the eye](https://lwn.net/Articles/191059/).)

### Configuration[](http://clig.dev/#configuration)

Command-line tools have lots of different types of configuration, and lots of different ways to supply it (flags, environment variables, project-level config files). The best way to supply each piece of configuration depends on a few factors, chief among them _specificity_, _stability_ and _complexity_.

Configuration generally falls into a few categories:

1.   Likely to vary from one invocation of the command to the next.

Examples:

    *   Setting the level of debugging output
    *   Enabling a safe mode or dry run of a program

Recommendation: **Use [flags](http://clig.dev/#arguments-and-flags).**[Environment variables](http://clig.dev/#environment-variables) may or may not be useful as well.

2.   Generally stable from one invocation to the next, but not always. Might vary between projects. Definitely varies between different users working on the same project.

This type of configuration is often specific to an individual computer.

Examples:

    *   Providing a non-default path to items needed for a program to start
    *   Specifying how or whether color should appear in output
    *   Specifying an HTTP proxy server to route all requests through

Recommendation: **Use [flags](http://clig.dev/#arguments-and-flags) and probably [environment variables](http://clig.dev/#environment-variables) too.** Users may want to set the variables in their shell profile so they apply globally, or in `.env` for a particular project.

If this configuration is sufficiently complex, it may warrant a configuration file of its own, but environment variables are usually good enough.

3.   Stable within a project, for all users.

This is the type of configuration that belongs in version control. Files like `Makefile`, `package.json` and `docker-compose.yml` are all examples of this.

Recommendation: **Use a command-specific, version-controlled file.**

**Follow the XDG-spec.** In 2010 the X Desktop Group, now [freedesktop.org](https://freedesktop.org/), developed a specification for the location of base directories where config files may be located. One goal was to limit the proliferation of dotfiles in a user’s home directory by supporting a general-purpose `~/.config` folder. The XDG Base Directory Specification ([full spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html), [summary](https://wiki.archlinux.org/index.php/XDG_Base_Directory#Specification)) is supported by yarn, fish, wireshark, emacs, neovim, tmux, and many other projects you know and love.

**If you automatically modify configuration that is not your program’s, ask the user for consent and tell them exactly what you’re doing.** Prefer creating a new config file (e.g. `/etc/cron.d/myapp`) rather than appending to an existing config file (e.g. `/etc/crontab`). If you have to append or modify to a system-wide config file, use a dated comment in that file to delineate your additions.

**Apply configuration parameters in order of precedence.** Here is the precedence for config parameters, from highest to lowest:

*   Flags
*   The running shell’s environment variables
*   Project-level configuration (e.g. `.env`)
*   User-level configuration
*   System wide configuration

### Environment variables[](http://clig.dev/#environment-variables)

**Environment variables are for behavior that _varies with the context_ in which a command is run.** The “environment” of an environment variable is the terminal session—the context in which the command is running. So, an env var might change each time a command runs, or between terminal sessions on one machine, or between instantiations of one project across several machines.

Environment variables may duplicate the functionality of flags or configuration parameters, or they may be distinct from those things. See [Configuration](http://clig.dev/#configuration) for a breakdown of common types of configuration and recommendations on when environment variables are most appropriate.

**For maximum portability, environment variable names must only contain uppercase letters, numbers, and underscores (and mustn’t start with a number).** Which means `O_O` and `OWO` are the only emoticons that are also valid environment variable names.

**Aim for single-line environment variable values.** While multi-line values are possible, they create usability issues with the `env` command.

**Avoid commandeering widely used names.** Here’s a [list of POSIX standard env vars](https://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap08.html).

**Check general-purpose environment variables for configuration values when possible:**

*   `NO_COLOR`, to disable color (see [Output](http://clig.dev/#output)) or `FORCE_COLOR` to enable it and ignore the detection logic
*   `DEBUG`, to enable more verbose output
*   `EDITOR`, if you need to prompt the user to edit a file or input more than a single line
*   `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and `NO_PROXY`, if you’re going to perform network operations (The HTTP library you’re using might already check for these.)
*   `SHELL`, if you need to open up an interactive session of the user’s preferred shell (If you need to execute a shell script, use a specific interpreter like `/bin/sh`)
*   `TERM`, `TERMINFO` and `TERMCAP`, if you’re going to use terminal-specific escape sequences
*   `TMPDIR`, if you’re going to create temporary files
*   `HOME`, for locating configuration files
*   `PAGER`, if you want to automatically page output
*   `LINES` and `COLUMNS`, for output that’s dependent on screen size (e.g. tables)

**Read environment variables from `.env` where appropriate.** If a command defines environment variables that are unlikely to change as long as the user is working in a particular directory, then it should also read them from a local `.env` file so users can configure it differently for different projects without having to specify them every time. Many languages have libraries for reading `.env` files ([Rust](https://crates.io/crates/dotenv), [Node](https://www.npmjs.com/package/dotenv), [Ruby](https://github.com/bkeepers/dotenv)).

**Don’t use `.env` as a substitute for a proper [configuration file](http://clig.dev/#configuration).**`.env` files have a lot of limitations:

*   A `.env` file is not commonly stored in source control
*   (Therefore, any configuration stored in it has no history)
*   It has only one data type: string
*   It lends itself to being poorly organized
*   It makes encoding issues easy to introduce
*   It often contains sensitive credentials & key material that would be better stored more securely

If it seems like these limitations will hamper usability or security, then a dedicated config file might be more appropriate.

**Do not read secrets from environment variables.** While environment variables may be convenient for storing secrets, they have proven too prone to leakage:

*   Exported environment variables are sent to every process, and from there can easily leak into logs or be exfiltrated
*   Shell substitutions like `curl -H "Authorization: Bearer $BEARER_TOKEN"` will leak into globally-readable process state. (cURL offers the `-H @filename` alternative for reading sensitive headers from a file.)
*   Docker container environment variables can be viewed by anyone with Docker daemon access via `docker inspect`
*   Environment variables in systemd units are globally readable via `systemctl show`

Secrets should only be accepted via credential files, pipes, `AF_UNIX` sockets, secret management services, or another IPC mechanism.

### Naming[](http://clig.dev/#naming)

> “Note the obsessive use of abbreviations and avoidance of capital letters; [Unix] is a system invented by people to whom repetitive stress disorder is what black lung is to miners. Long names get worn down to three-letter nubbins, like stones smoothed by a river.” — Neal Stephenson, _[In the Beginning was the Command Line](https://web.stanford.edu/class/cs81n/command.txt)_

The name of your program is particularly important on the CLI: your users will be typing it all the time, and it needs to be easy to remember and type.

**Make it a simple, memorable word.** But not too generic, or you’ll step on the toes of other commands and confuse users. For example, both ImageMagick and Windows used the command `convert`.

**Use only lowercase letters, and dashes if you really need to.**`curl` is a good name, `DownloadURL` is not.

**Keep it short.** Users will be typing it all the time. Don’t make it _too_ short: the very shortest commands are best reserved for the common utilities used all the time, such as `cd`, `ls`, `ps`.

**Make it easy to type.** If you expect people to type your command name all day, make it easy on their hands.

A real-world example: long before Docker Compose was `docker compose`, it was [`plum`](https://github.com/aanand/fig/blob/0eb7d308615bae1ad4be1ca5112ac7b6b6cbfbaf/setup.py#L26). This turned out to be such an awkward, one-handed hopscotch that it was immediately renamed to [`fig`](https://github.com/aanand/fig/commit/0cafdc9c6c19dab2ef2795979dc8b2f48f623379), which – as well as being shorter – flows much more easily.

_Further reading: [The Poetics of CLI Command Names](https://smallstep.com/blog/the-poetics-of-cli-command-names/)_

### Distribution[](http://clig.dev/#distribution)

**If possible, distribute as a single binary.** If your language doesn’t compile to binary executables as standard, see if it has something like [PyInstaller](https://www.pyinstaller.org/). If you really can’t distribute as a single binary, use the platform’s native package installer so you aren’t scattering things on disk that can’t easily be removed. Tread lightly on the user’s computer.

If you’re making a language-specific tool, such as a code linter, then this rule doesn’t apply—it’s safe to assume the user has an interpreter for that language installed on their computer.

**Make it easy to uninstall.** If it needs instructions, put them at the bottom of the install instructions—one of the most common times people want to uninstall software is right after installing it.

### Analytics[](http://clig.dev/#analytics)

Usage metrics can be helpful to understand how users are using your program, how to make it better, and where to focus effort. But, unlike websites, users of the command-line expect to be in control of their environment, and it is surprising when programs do things in the background without telling them.

**Do not phone home usage or crash data without consent.** Users will find out, and they will be angry. Be very explicit about what you collect, why you collect it, how anonymous it is and how you go about anonymizing it, and how long you retain it for.

Ideally, ask users whether they want to contribute data (“opt-in”). If you choose to do it by default (“opt-out”), then clearly tell users about it on your website or first run, and make it easy to disable.

Examples of projects that collect usage statistics:

*   Angular.js [collects detailed analytics using Google Analytics](https://angular.io/analytics), in the name of feature prioritization. You have to explicitly opt in. You can change the tracking ID to point to your own Google Analytics property if you want to track Angular usage inside your organization.
*   Homebrew sends metrics to Google Analytics and has [a nice FAQ](https://docs.brew.sh/Analytics) detailing their practices.
*   Next.js [collects anonymized usage statistics](https://nextjs.org/telemetry) and is enabled by default.

**Consider alternatives to collecting analytics.**

*   Instrument your web docs. If you want to know how people are using your CLI tool, make a set of docs around the use cases you’d like to understand best, and see how they perform over time. Look at what people search for within your docs.
*   Instrument your downloads. This can be a rough metric to understand usage and what operating systems your users are running.
*   Talk to your users. Reach out and ask people how they’re using your tool. Encourage feedback and feature requests in your docs and repos, and try to draw out more context from those who submit feedback.

_Further reading: [Open Source Metrics](https://opensource.guide/metrics/)_

Further reading[](http://clig.dev/#further-reading)
---------------------------------------------------

*   [The Unix Programming Environment](https://en.wikipedia.org/wiki/The_Unix_Programming_Environment), Brian W. Kernighan and Rob Pike
*   [POSIX Utility Conventions](https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap12.html)
*   [Program Behavior for All Programs](https://www.gnu.org/prep/standards/html_node/Program-Behavior.html), GNU Coding Standards
*   [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46), Jeff Dickey
*   [CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide), Heroku

==================== cli-style-guide.md (===== coding/developing-cli-tools/resources/cli-style-guide/cli-style-guide.md =====) ====================

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


==================== gnu-standards.md (===== coding/developing-cli-tools/resources/gnu-standards.md =====) ====================

## 4.1 Non-GNU Standards

The GNU Project regards standards published by other organizations as suggestions, not orders. We consider those standards, but we do not "obey" them. In developing a GNU program, you should implement an outside standard's specifications when that makes the GNU system better overall in an objective sense. When it doesn't, you shouldn't. 

In most cases, following published standards is convenient for users—it means that their programs or scripts will work more portably. For instance, GCC implements nearly all the features of Standard C as specified by that standard. C program developers would be unhappy if it did not. And GNU utilities mostly follow specifications of POSIX; shell script writers and users would be unhappy if our programs were incompatible. 

But we do not follow either of these specifications rigidly, and there are specific points on which we decided not to follow them, so as to make the GNU system better for users. 

For instance, Standard C says that nearly all extensions to C are prohibited. How silly! GCC implements many extensions, some of which were later adopted as part of the standard. If you want these constructs to give an error message as "required" by the standard, you must specify '--pedantic', which was implemented only so that we can say "GCC is a 100% implementation of the standard", not because there is any reason to actually use it. 

POSIX specifies that 'df' and 'du' must output sizes by default in units of 512 bytes. What users want is units of 1k, so that is what we do by default. If you want the ridiculous behavior "required" by POSIX, you must set the environment variable 'POSIXLY_CORRECT' (which was originally going to be named 'POSIX_ME_HARDER'). 

GNU utilities also depart from the letter of the POSIX specification when they support long-named command-line options, and intermixing of options with ordinary arguments. This minor incompatibility with POSIX is never a problem in practice, and it is very useful. 

In particular, don't reject a new feature, or remove an old one, merely because a standard says it is "forbidden" or "deprecated".

## 4.2 Writing Robust Programs

Avoid arbitrary limits on the length or number of _any_ data structure, including file names, lines, files, and symbols, by allocating all data structures dynamically. In most Unix utilities, "long lines are silently truncated". This is not acceptable in a GNU utility. 

Utilities reading files should not drop NUL characters, or any other nonprinting characters. Programs should work properly with multibyte character encodings, such as UTF-8. You can use libiconv to deal with a range of encodings. 

Check every system call for an error return, unless you know you wish to ignore errors. Include the system error text (from `strerror`, or equivalent) in _every_ error message resulting from a failing system call, as well as the name of the file if any and the name of the utility. Just "cannot open foo.c" or "stat failed" is not sufficient. 

Check every call to `malloc` or `realloc` to see if it returned `NULL`. Check `realloc` even if you are making the block smaller; in a system that rounds block sizes to a power of 2, `realloc` may get a different block if you ask for less space. 

You must expect `free` to alter the contents of the block that was freed. Anything you want to fetch from the block, you must fetch before calling `free`. 

If `malloc` fails in a noninteractive program, make that a fatal error. In an interactive program (one that reads commands from the user), it is better to abort the command and return to the command reader loop. This allows the user to kill other processes to free up virtual memory, and then try the command again. 

Use `getopt_long` to decode arguments, unless the argument syntax makes this unreasonable. 

When static storage is to be written in during program execution, use explicit C code to initialize it. This way, restarting the program (without reloading it), or part of it, will reinitialize those variables. Reserve C initialized declarations for data that will not be changed. 

Try to avoid low-level interfaces to obscure Unix data structures (such as file directories, utmp, or the layout of kernel memory), since these are less likely to work compatibly. If you need to find all the files in a directory, use `readdir` or some other high-level interface. These are supported compatibly by GNU. 

The preferred signal handling facilities are the BSD variant of `signal`, and the POSIX `sigaction` function; the alternative USG `signal` interface is an inferior design. 

Nowadays, using the POSIX signal functions may be the easiest way to make a program portable. If you use `signal`, then on GNU/Linux systems running GNU libc version 1, you should include bsd/signal.h instead of signal.h, so as to get BSD behavior. It is up to you whether to support systems where `signal` has only the USG behavior, or give up on them. 

In error checks that detect "impossible" conditions, just abort. There is usually no point in printing any message. These checks indicate the existence of bugs. Whoever wants to fix the bugs will have to read the source code and run a debugger. So explain the problem with comments in the source. The relevant data will be in variables, which are easy to examine with the debugger, so there is no point moving them elsewhere. 

Do not use a count of errors as the exit status for a program. _That does not work_ , because exit status values are limited to 8 bits (0 through 255). A single run of the program might have 256 errors; if you try to return 256 as the exit status, the parent process will see 0 as the status, and it will appear that the program succeeded. 

If you make temporary files, check the `TMPDIR` environment variable; if that variable is defined, use the specified directory instead of /tmp. 

In addition, be aware that there is a possible security problem when creating temporary files in world-writable directories. In C, you can avoid this problem by creating temporary files in this manner: 
```
fd = open (filename, O_WRONLY | O_CREAT | O_EXCL, 0600);

```

or by using the `mkstemps` function from Gnulib (see [mkstemps](https://www.gnu.org/software/gnulib/manual/html_node/mkstemps.html#mkstemps) in Gnulib). 

In bash, use `set -C` (long name `noclobber`) to avoid this problem. In addition, the `mktemp` utility is a more general solution for creating temporary files from shell scripts (see [mktemp invocation](https://www.gnu.org/software/coreutils/manual/html_node/mktemp-invocation.html#mktemp-invocation) in GNU Coreutils).

## 4.3 Library Behavior

Try to make library functions reentrant. If they need to do dynamic storage allocation, at least try to avoid any nonreentrancy aside from that of `malloc` itself. 

Here are certain name conventions for libraries, to avoid name conflicts. 

Choose a name prefix for the library, more than two characters long. All external function and variable names should start with this prefix. In addition, there should only be one of these in any given library member. This usually means putting each one in a separate source file. 

An exception can be made when two external symbols are always used together, so that no reasonable program could use one without the other; then they can both go in the same file. 

External symbols that are not documented entry points for the user should have names beginning with '_'. The '_' should be followed by the chosen name prefix for the library, to prevent collisions with other libraries. These can go in the same files with user entry points if you like. 

Static functions and variables can be used as you like and need not fit any naming convention.

## 4.4 Formatting Error Messages

Error messages from compilers should look like this: 
```
sourcefile:lineno: message

```

If you want to mention the column number, use one of these formats: 
```
sourcefile:lineno:column: message
sourcefile:lineno.column: message


```

Line numbers should start from 1 at the beginning of the file, and column numbers should start from 1 at the beginning of the line. (Both of these conventions are chosen for compatibility.) Calculate column numbers assuming that space and all ASCII printing characters have equal width, and assuming tab stops every 8 columns. For non-ASCII characters, Unicode character widths should be used when in a UTF-8 locale; GNU libc and GNU gnulib provide suitable `wcwidth` functions. 

The error message can also give both the starting and ending positions of the erroneous text. There are several formats so that you can avoid redundant information such as a duplicate line number. Here are the possible formats: 
```
sourcefile:line1.column1-line2.column2: message
sourcefile:line1.column1-column2: message
sourcefile:line1-line2: message

```

When an error is spread over several files, you can use this format: 
```
file1:line1.column1-file2:line2.column2: message

```

Error messages from other noninteractive programs should look like this: 
```
program:sourcefile:lineno: message

```

when there is an appropriate source file, or like this: 
```
program: message

```

when there is no relevant source file. 

If you want to mention the column number, use this format: 
```
program:sourcefile:lineno:column: message

```

In an interactive program (one that is reading commands from a terminal), it is better not to include the program name in an error message. The place to indicate which program is running is in the prompt or with the screen layout. (When the same program runs with input from a source other than a terminal, it is not interactive and would do best to print error messages using the noninteractive style.) 

The string message should not begin with a capital letter when it follows a program name and/or file name, because that isn't the beginning of a sentence. (The sentence conceptually starts at the beginning of the line.) Also, it should not end with a period. 

Error messages from interactive programs, and other messages such as usage messages, should start with a capital letter. But they should not end with a period.

## 4.5 Standards for Interfaces Generally

Please don't make the behavior of a utility depend on the name used to invoke it. It is useful sometimes to make a link to a utility with a different name, and that should not change what it does. Thus, if you make foo a link to ls, the program should behave the same regardless of which of those names is used to invoke it. 

Instead, use a run time option or a compilation switch or both to select among the alternate behaviors. You can also build two versions of the program, with different default behaviors, and install them under two different names. 

Likewise, please don't make the behavior of a command-line program depend on the type of output device it gets as standard output or standard input. Device independence is an important principle of the system's design; do not compromise it merely to save someone from typing an option now and then. (Variation in error message syntax when using a terminal is ok, because that is a side issue that people do not depend on.) 

If you think one behavior is most useful when the output is to a terminal, and another is most useful when the output is a file or a pipe, then it is usually best to make the default behavior the one that is useful with output to a terminal, and have an option for the other behavior. You can also build two different versions of the program with different names. 

There is an exception for programs whose output in certain cases is binary data. Sending such output to a terminal is useless and can cause trouble. If such a program normally sends its output to stdout, it should detect, in these cases, when the output is a terminal and give an error message instead. The `-f` option should override this exception, thus permitting the output to go to the terminal. 

Compatibility requires certain programs to depend on the type of output device. It would be disastrous if `ls` or `sh` did not do so in the way all users expect. In some of these cases, we supplement the program with a preferred alternate version that does not depend on the output device type. For example, we provide a `dir` program much like `ls` except that its default output format is always multi-column format.

## 4.6 Finding the Program's Executable and Associated Files

A program may need to find the executable file it was started with, so as to relaunch the same program. It may need to find associated files, either source files or files constructed by building, that it uses at run time. 

The way to find them starts with looking at `argv[0]`. 

If that string contains a slash, it is by convention the file name of the executable and its directory part is the directory that contained the executable. This is the case when the program was not found through `PATH`, which normally means it was built but not installed, and run from the build directory. The program can use the `argv[0]` file name to relaunch itself, and can look in its directory part for associated files. If that file name is not absolute, then it is relative to the working directory in which the program started. 

If `argv[0]` does not contain a slash, it is a command name whose executable was found via `PATH`. The program should search for that name in the directories in `PATH`, interpreting . as the working directory that was current when the program started. 

If this procedure finds the executable, we call the directory it was found in the _invocation directory_. The program should check for the presence in that directory of the associated files it needs. 

If the program's executable is normally built in a subdirectory of the main build directory, and the main build directory contains associated files (perhaps including subdirectories), the program should look at the parent of the invocation directory, checking for the associated files and subdirectories the main build directory should contain. 

If the invocation directory doesn't contain what's needed, but the executable file name is a symbolic link, the program should try using the link target's containing directory as the invocation directory. 

If this procedure doesn't come up with an invocation directory that is valid—normally the case for an installed program that was found via `PATH`—the program should look for the associated files in the directories where the program's makefile installs them. See [Variables for Installation Directories](https://www.gnu.org/prep/standards/html_node/Directory-Variables.html). 

Providing valid information in `argv[0]` is a convention, not guaranteed. Well-behaved programs that launch other programs, such as shells, follow the convention; your code should follow it too, when launching other programs. But it is always possible to launch the program and give a nonsensical value in `argv[0]`. 

Therefore, any program that needs to know the location of its executable, or that of of other associated files, should offer the user environment variables to specify those locations explicitly. 

**Don't give special privilege, such as with the`setuid` bit, to programs that will search heuristically for associated files or for their own executables when invoked that way.** Limit that privilege to programs that find associated files in hard-coded installed locations such as under /usr and /etc. 

See [Bourne Shell Variables](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Variables.html#Bourne-Shell-Variables) in Bash Reference Manual, for more information about `PATH`.

## 4.7 Standards for Graphical Interfaces

When you write a program that provides a graphical user interface, please make it work with the X Window System, using the GTK+ toolkit or the GNUstep toolkit, unless the functionality specifically requires some alternative (for example, "displaying jpeg images while in console mode"). 

In addition, please provide a command-line interface to control the functionality. (In many cases, the graphical user interface can be a separate program which invokes the command-line program.) This is so that the same jobs can be done from scripts. 

Please also consider providing a D-bus interface for use from other running programs, such as within GNOME. (GNOME used to use CORBA for this, but that is being phased out.) In addition, consider providing a library interface (for use from C), and perhaps a keyboard-driven console interface (for use by users from console mode). Once you are doing the work to provide the functionality and the graphical interface, these won't be much extra work. 

Please make your program interoperate with access technology such as screen readers (see <https://www.gnu.org/accessibility/accessibility.html>). This should be automatic if you use GTK+.

## 4.8 Standards for Command Line Interfaces

It is a good idea to follow the POSIX guidelines for the command-line options of a program. The easiest way to do this is to use `getopt` to parse them. Note that the GNU version of `getopt` will normally permit options anywhere among the arguments unless the special argument '--' is used. This is not what POSIX specifies; it is a GNU extension. 

Please define long-named options that are equivalent to the single-letter Unix-style options. We hope to make GNU more user friendly this way. This is easy to do with the GNU function `getopt_long`. 

One of the advantages of long-named options is that they can be consistent from program to program. For example, users should be able to expect the "verbose" option of any GNU program which has one, to be spelled precisely '--verbose'. To achieve this uniformity, look at the table of common long-option names when you choose the option names for your program (see [Table of Long Options](https://www.gnu.org/prep/standards/html_node/Option-Table.html)). 

It is usually a good idea for file names given as ordinary arguments to be input files only; any output files would be specified using options (preferably '-o' or '--output'). Even if you allow an output file name as an ordinary argument for compatibility, try to provide an option as another way to specify it. This will lead to more consistency among GNU utilities, and fewer idiosyncrasies for users to remember. 

All programs should support two standard options: '--version' and '--help'. CGI programs should accept these as command-line options, and also if given as the `PATH_INFO`; for instance, visiting '`http://example.org/p.cgi/--help`' in a browser should output the same information as invoking 'p.cgi --help' from the command line. 
  * [--version](https://www.gnu.org/prep/standards/html_node/_002d_002dversion.html)
  * [--help](https://www.gnu.org/prep/standards/html_node/_002d_002dhelp.html)

## 4.9 Standards for Dynamic Plug-in Interfaces

Another aspect of keeping free programs free is encouraging development of free plug-ins, and discouraging development of proprietary plug-ins. Many GNU programs will not have anything like plug-ins at all, but those that do should follow these practices. 

First, the general plug-in architecture design should closely tie the plug-in to the original code, such that the plug-in and the base program are parts of one extended program. For GCC, for example, plug-ins receive and modify GCC's internal data structures, and so clearly form an extended program with the base GCC. 

Second, you should require plug-in developers to affirm that their plug-ins are released under an appropriate license. This should be enforced with a simple programmatic check. For GCC, again for example, a plug-in must define the global symbol `plugin_is_GPL_compatible`, thus asserting that the plug-in is released under a GPL-compatible license (see [Plugins](https://gcc.gnu.org/onlinedocs/gccint/Plugins.html#Plugins) in GCC Internals). 

By adding this check to your program you are not creating a new legal requirement. The GPL itself requires plug-ins to be free software, licensed compatibly. As long as you have followed the first rule above to keep plug-ins closely tied to your original program, the GPL and AGPL already require those plug-ins to be released under a compatible license. The symbol definition in the plug-in—or whatever equivalent works best in your program—makes it harder for anyone who might distribute proprietary plug-ins to legally defend themselves. If a case about this got to court, we can point to that symbol as evidence that the plug-in developer understood that the license had this requirement.

## 4.10 Table of Long Options

Here is a table of long options used by GNU programs. It is surely incomplete, but we aim to list all the options that a new program might want to be compatible with. If you use names not already in the table, please send bug-standards@gnu.org a list of them, with their meanings, so we can update the table.  

'after-date'
    
'-N' in `tar`.  

'all'
    
'-a' in `du`, `ls`, `nm`, `stty`, `uname`, and `unexpand`.  

'all-text'
    
'-a' in `diff`.  

'almost-all'
    
'-A' in `ls`.  

'append'
    
'-a' in `etags`, `tee`, `time`; '-r' in `tar`.  

'archive'
    
'-a' in `cp`.  

'archive-name'
    
'-n' in `shar`.  

'arglength'
    
'-l' in `m4`.  

'ascii'
    
'-a' in `diff`.  

'assign'
    
'-v' in `gawk`.  

'assume-new'
    
'-W' in `make`.  

'assume-old'
    
'-o' in `make`.  

'auto-check'
    
'-a' in `recode`.  

'auto-pager'
    
'-a' in `wdiff`.  

'auto-reference'
    
'-A' in `ptx`.  

'avoid-wraps'
    
'-n' in `wdiff`.  

'background'
    
For server programs, run in the background.  

'backward-search'
    
'-B' in `ctags`.  

'basename'
    
'-f' in `shar`.  

'batch'
    
Used in GDB.  

'baud'
    
Used in GDB.  

'before'
    
'-b' in `tac`.  

'binary'
    
'-b' in `cpio` and `diff`.  

'bits-per-code'
    
'-b' in `shar`.  

'block-size'
    
Used in `cpio` and `tar`.  

'blocks'
    
'-b' in `head` and `tail`.  

'break-file'
    
'-b' in `ptx`.  

'brief'
    
Used in various programs to make output shorter.  

'bytes'
    
'-c' in `head`, `split`, and `tail`.  

'c`++`'
    
'-C' in `etags`.  

'catenate'
    
'-A' in `tar`.  

'cd'
    
Used in various programs to specify the directory to use.  

'changes'
    
'-c' in `chgrp` and `chown`.  

'classify'
    
'-F' in `ls`.  

'colons'
    
'-c' in `recode`.  

'command'
    
'-c' in `su`; '-x' in GDB.  

'compare'
    
'-d' in `tar`.  

'compat'
    
Used in `gawk`.  

'compress'
    
'-Z' in `tar` and `shar`.  

'concatenate'
    
'-A' in `tar`.  

'confirmation'
    
'-w' in `tar`.  

'context'
    
Used in `diff`.  

'copyleft'
    
'-W copyleft' in `gawk`.  

'copyright'
    
'-C' in `ptx`, `recode`, and `wdiff`; '-W copyright' in `gawk`.  

'core'
    
Used in GDB.  

'count'
    
'-q' in `who`.  

'count-links'
    
'-l' in `du`.  

'create'
    
Used in `tar` and `cpio`.  

'cut-mark'
    
'-c' in `shar`.  

'cxref'
    
'-x' in `ctags`.  

'date'
    
'-d' in `touch`.  

'debug'
    
'-d' in `make` and `m4`; '-t' in Bison.  

'define'
    
'-D' in `m4`.  

'defines'
    
'-d' in Bison and `ctags`.  

'delete'
    
'-D' in `tar`.  

'dereference'
    
'-L' in `chgrp`, `chown`, `cpio`, `du`, `ls`, and `tar`.  

'dereference-args'
    
'-D' in `du`.  

'device'
    
Specify an I/O device (special file name).  

'diacritics'
    
'-d' in `recode`.  

'dictionary-order'
    
'-d' in `look`.  

'diff'
    
'-d' in `tar`.  

'digits'
    
'-n' in `csplit`.  

'directory'
    
Specify the directory to use, in various programs. In `ls`, it means to show directories themselves rather than their contents. In `rm` and `ln`, it means to not treat links to directories specially.  

'discard-all'
    
'-x' in `strip`.  

'discard-locals'
    
'-X' in `strip`.  

'dry-run'
    
'-n' in `make`.  

'ed'
    
'-e' in `diff`.  

'elide-empty-files'
    
'-z' in `csplit`.  

'end-delete'
    
'-x' in `wdiff`.  

'end-insert'
    
'-z' in `wdiff`.  

'entire-new-file'
    
'-N' in `diff`.  

'environment-overrides'
    
'-e' in `make`.  

'eof'
    
'-e' in `xargs`.  

'epoch'
    
Used in GDB.  

'error-limit'
    
Used in `makeinfo`.  

'error-output'
    
'-o' in `m4`.  

'escape'
    
'-b' in `ls`.  

'exclude-from'
    
'-X' in `tar`.  

'exec'
    
Used in GDB.  

'exit'
    
'-x' in `xargs`.  

'exit-0'
    
'-e' in `unshar`.  

'expand-tabs'
    
'-t' in `diff`.  

'expression'
    
'-e' in `sed`.  

'extern-only'
    
'-g' in `nm`.  

'extract'
    
'-i' in `cpio`; '-x' in `tar`.  

'faces'
    
'-f' in `finger`.  

'fast'
    
'-f' in `su`.  

'fatal-warnings'
    
'-E' in `m4`.  

'file'
    
'-f' in `gawk`, `info`, `make`, `mt`, `sed`, and `tar`.  

'field-separator'
    
'-F' in `gawk`.  

'file-prefix'
    
'-b' in Bison.  

'file-type'
    
'-F' in `ls`.  

'files-from'
    
'-T' in `tar`.  

'fill-column'
    
Used in `makeinfo`.  

'flag-truncation'
    
'-F' in `ptx`.  

'fixed-output-files'
    
'-y' in Bison.  

'follow'
    
'-f' in `tail`.  

'footnote-style'
    
Used in `makeinfo`.  

'force'
    
'-f' in `cp`, `ln`, `mv`, and `rm`.  

'force-prefix'
    
'-F' in `shar`.  

'foreground'
    
For server programs, run in the foreground; in other words, don't do anything special to run the server in the background.  

'format'
    
Used in `ls`, `time`, and `ptx`.  

'freeze-state'
    
'-F' in `m4`.  

'fullname'
    
Used in GDB.  

'gap-size'
    
'-g' in `ptx`.  

'get'
    
'-x' in `tar`.  

'graphic'
    
'-i' in `ul`.  

'graphics'
    
'-g' in `recode`.  

'group'
    
'-g' in `install`.  

'gzip'
    
'-z' in `tar` and `shar`.  

'hashsize'
    
'-H' in `m4`.  

'header'
    
'-h' in `objdump` and `recode` 

'heading'
    
'-H' in `who`.  

'help'
    
Used to ask for brief usage information.  

'here-delimiter'
    
'-d' in `shar`.  

'hide-control-chars'
    
'-q' in `ls`.  

'html'
    
In `makeinfo`, output HTML.  

'idle'
    
'-u' in `who`.  

'ifdef'
    
'-D' in `diff`.  

'ignore'
    
'-I' in `ls`; '-x' in `recode`.  

'ignore-all-space'
    
'-w' in `diff`.  

'ignore-backups'
    
'-B' in `ls`.  

'ignore-blank-lines'
    
'-B' in `diff`.  

'ignore-case'
    
'-f' in `look` and `ptx`; '-i' in `diff` and `wdiff`.  

'ignore-errors'
    
'-i' in `make`.  

'ignore-file'
    
'-i' in `ptx`.  

'ignore-indentation'
    
'-I' in `etags`.  

'ignore-init-file'
    
'-f' in Oleo.  

'ignore-interrupts'
    
'-i' in `tee`.  

'ignore-matching-lines'
    
'-I' in `diff`.  

'ignore-space-change'
    
'-b' in `diff`.  

'ignore-zeros'
    
'-i' in `tar`.  

'include'
    
'-i' in `etags`; '-I' in `m4`.  

'include-dir'
    
'-I' in `make`.  

'incremental'
    
'-G' in `tar`.  

'info'
    
'-i', '-l', and '-m' in Finger.  

'init-file'
    
In some programs, specify the name of the file to read as the user's init file.  

'initial'
    
'-i' in `expand`.  

'initial-tab'
    
'-T' in `diff`.  

'inode'
    
'-i' in `ls`.  

'interactive'
    
'-i' in `cp`, `ln`, `mv`, `rm`; '-e' in `m4`; '-p' in `xargs`; '-w' in `tar`.  

'intermix-type'
    
'-p' in `shar`.  

'iso-8601'
    
Used in `date` 

'jobs'
    
'-j' in `make`.  

'just-print'
    
'-n' in `make`.  

'keep-going'
    
'-k' in `make`.  

'keep-files'
    
'-k' in `csplit`.  

'kilobytes'
    
'-k' in `du` and `ls`.  

'language'
    
'-l' in `etags`.  

'less-mode'
    
'-l' in `wdiff`.  

'level-for-gzip'
    
'-g' in `shar`.  

'line-bytes'
    
'-C' in `split`.  

'lines'
    
Used in `split`, `head`, and `tail`.  

'link'
    
'-l' in `cpio`.  

'lint'


'lint-old'
    
Used in `gawk`.  

'list'
    
'-t' in `cpio`; '-l' in `recode`.  

'list'
    
'-t' in `tar`.  

'literal'
    
'-N' in `ls`.  

'load-average'
    
'-l' in `make`.  

'login'
    
Used in `su`.  

'machine'
    
Used in `uname`.  

'macro-name'
    
'-M' in `ptx`.  

'mail'
    
'-m' in `hello` and `uname`.  

'make-directories'
    
'-d' in `cpio`.  

'makefile'
    
'-f' in `make`.  

'mapped'
    
Used in GDB.  

'max-args'
    
'-n' in `xargs`.  

'max-chars'
    
'-n' in `xargs`.  

'max-lines'
    
'-l' in `xargs`.  

'max-load'
    
'-l' in `make`.  

'max-procs'
    
'-P' in `xargs`.  

'mesg'
    
'-T' in `who`.  

'message'
    
'-T' in `who`.  

'minimal'
    
'-d' in `diff`.  

'mixed-uuencode'
    
'-M' in `shar`.  

'mode'
    
'-m' in `install`, `mkdir`, and `mkfifo`.  

'modification-time'
    
'-m' in `tar`.  

'multi-volume'
    
'-M' in `tar`.  

'name-prefix'
    
'-a' in Bison.  

'nesting-limit'
    
'-L' in `m4`.  

'net-headers'
    
'-a' in `shar`.  

'new-file'
    
'-W' in `make`.  

'no-builtin-rules'
    
'-r' in `make`.  

'no-character-count'
    
'-w' in `shar`.  

'no-check-existing'
    
'-x' in `shar`.  

'no-common'
    
'-3' in `wdiff`.  

'no-create'
    
'-c' in `touch`.  

'no-defines'
    
'-D' in `etags`.  

'no-deleted'
    
'-1' in `wdiff`.  

'no-dereference'
    
'-d' in `cp`.  

'no-inserted'
    
'-2' in `wdiff`.  

'no-keep-going'
    
'-S' in `make`.  

'no-lines'
    
'-l' in Bison.  

'no-piping'
    
'-P' in `shar`.  

'no-prof'
    
'-e' in `gprof`.  

'no-regex'
    
'-R' in `etags`.  

'no-sort'
    
'-p' in `nm`.  

'no-splash'
    
Don't print a startup splash screen.  

'no-split'
    
Used in `makeinfo`.  

'no-static'
    
'-a' in `gprof`.  

'no-time'
    
'-E' in `gprof`.  

'no-timestamp'
    
'-m' in `shar`.  

'no-validate'
    
Used in `makeinfo`.  

'no-wait'
    
Used in `emacsclient`.  

'no-warn'
    
Used in various programs to inhibit warnings.  

'node'
    
'-n' in `info`.  

'nodename'
    
'-n' in `uname`.  

'nonmatching'
    
'-f' in `cpio`.  

'nstuff'
    
'-n' in `objdump`.  

'null'
    
'-0' in `xargs`.  

'number'
    
'-n' in `cat`.  

'number-nonblank'
    
'-b' in `cat`.  

'numeric-sort'
    
'-n' in `nm`.  

'numeric-uid-gid'
    
'-n' in `cpio` and `ls`.  

'nx'
    
Used in GDB.  

'old-file'
    
'-o' in `make`.  

'one-file-system'
    
'-x' in `cp` and `du`.  

'only-file'
    
'-o' in `ptx`.  

'only-prof'
    
'-f' in `gprof`.  

'only-time'
    
'-F' in `gprof`.  

'options'
    
'-o' in `getopt`, `fdlist`, `fdmount`, `fdmountd`, and `fdumount`.  

'output'
    
In various programs, specify the output file name.  

'output-prefix'
    
'-o' in `shar`.  

'override'
    
'-o' in `rm`.  

'overwrite'
    
'-c' in `unshar`.  

'owner'
    
'-o' in `install`.  

'paginate'
    
'-l' in `diff`.  

'paragraph-indent'
    
Used in `makeinfo`.  

'parents'
    
'-p' in `mkdir` and `rmdir`.  

'pass-all'
    
'-p' in `ul`.  

'pass-through'
    
'-p' in `cpio`.  

'port'
    
'-P' in `finger`.  

'portability'
    
'-c' in `cpio`.  

'posix'
    
Used in `gawk`.  

'prefix-builtins'
    
'-P' in `m4`.  

'prefix'
    
'-f' in `csplit`.  

'preserve'
    
Used in `tar` and `cp`.  

'preserve-environment'
    
'-p' in `su`.  

'preserve-modification-time'
    
'-m' in `cpio`.  

'preserve-order'
    
'-s' in `tar`.  

'preserve-permissions'
    
'-p' in `tar`.  

'print'
    
'-l' in `diff`.  

'print-chars'
    
'-L' in `cmp`.  

'print-data-base'
    
'-p' in `make`.  

'print-directory'
    
'-w' in `make`.  

'print-file-name'
    
'-o' in `nm`.  

'print-symdefs'
    
'-s' in `nm`.  

'printer'
    
'-p' in `wdiff`.  

'prompt'
    
'-p' in `ed`.  

'proxy'
    
Specify an HTTP proxy.  

'query-user'
    
'-X' in `shar`.  

'question'
    
'-q' in `make`.  

'quiet'
    
Used in many programs to inhibit the usual output. Every program accepting '--quiet' should accept '--silent' as a synonym.  

'quiet-unshar'
    
'-Q' in `shar` 

'quote-name'
    
'-Q' in `ls`.  

'rcs'
    
'-n' in `diff`.  

're-interval'
    
Used in `gawk`.  

'read-full-blocks'
    
'-B' in `tar`.  

'readnow'
    
Used in GDB.  

'recon'
    
'-n' in `make`.  

'record-number'
    
'-R' in `tar`.  

'recursive'
    
Used in `chgrp`, `chown`, `cp`, `ls`, `diff`, and `rm`.  

'reference'
    
'-r' in `touch`.  

'references'
    
'-r' in `ptx`.  

'regex'
    
'-r' in `tac` and `etags`.  

'release'
    
'-r' in `uname`.  

'reload-state'
    
'-R' in `m4`.  

'relocation'
    
'-r' in `objdump`.  

'rename'
    
'-r' in `cpio`.  

'replace'
    
'-i' in `xargs`.  

'report-identical-files'
    
'-s' in `diff`.  

'reset-access-time'
    
'-a' in `cpio`.  

'reverse'
    
'-r' in `ls` and `nm`.  

'reversed-ed'
    
'-f' in `diff`.  

'right-side-defs'
    
'-R' in `ptx`.  

'same-order'
    
'-s' in `tar`.  

'same-permissions'
    
'-p' in `tar`.  

'save'
    
'-g' in `stty`.  

'se'
    
Used in GDB.  

'sentence-regexp'
    
'-S' in `ptx`.  

'separate-dirs'
    
'-S' in `du`.  

'separator'
    
'-s' in `tac`.  

'sequence'
    
Used by `recode` to choose files or pipes for sequencing passes.  

'shell'
    
'-s' in `su`.  

'show-all'
    
'-A' in `cat`.  

'show-c-function'
    
'-p' in `diff`.  

'show-ends'
    
'-E' in `cat`.  

'show-function-line'
    
'-F' in `diff`.  

'show-tabs'
    
'-T' in `cat`.  

'silent'
    
Used in many programs to inhibit the usual output. Every program accepting '--silent' should accept '--quiet' as a synonym.  

'size'
    
'-s' in `ls`.  

'socket'
    
Specify a file descriptor for a network server to use for its socket, instead of opening and binding a new socket. This provides a way to run, in a non-privileged process, a server that normally needs a reserved port number.  

'sort'
    
Used in `ls`.  

'source'
    
'-W source' in `gawk`.  

'sparse'
    
'-S' in `tar`.  

'speed-large-files'
    
'-H' in `diff`.  

'split-at'
    
'-E' in `unshar`.  

'split-size-limit'
    
'-L' in `shar`.  

'squeeze-blank'
    
'-s' in `cat`.  

'start-delete'
    
'-w' in `wdiff`.  

'start-insert'
    
'-y' in `wdiff`.  

'starting-file'
    
Used in `tar` and `diff` to specify which file within a directory to start processing with.  

'statistics'
    
'-s' in `wdiff`.  

'stdin-file-list'
    
'-S' in `shar`.  

'stop'
    
'-S' in `make`.  

'strict'
    
'-s' in `recode`.  

'strip'
    
'-s' in `install`.  

'strip-all'
    
'-s' in `strip`.  

'strip-debug'
    
'-S' in `strip`.  

'submitter'
    
'-s' in `shar`.  

'suffix'
    
'-S' in `cp`, `ln`, `mv`.  

'suffix-format'
    
'-b' in `csplit`.  

'sum'
    
'-s' in `gprof`.  

'summarize'
    
'-s' in `du`.  

'symbolic'
    
'-s' in `ln`.  

'symbols'
    
Used in GDB and `objdump`.  

'synclines'
    
'-s' in `m4`.  

'sysname'
    
'-s' in `uname`.  

'tabs'
    
'-t' in `expand` and `unexpand`.  

'tabsize'
    
'-T' in `ls`.  

'terminal'
    
'-T' in `tput` and `ul`. '-t' in `wdiff`.  

'text'
    
'-a' in `diff`.  

'text-files'
    
'-T' in `shar`.  

'time'
    
Used in `ls` and `touch`.  

'timeout'
    
Specify how long to wait before giving up on some operation.  

'to-stdout'
    
'-O' in `tar`.  

'total'
    
'-c' in `du`.  

'touch'
    
'-t' in `make`, `ranlib`, and `recode`.  

'trace'
    
'-t' in `m4`.  

'traditional'
    
'-t' in `hello`; '-W traditional' in `gawk`; '-G' in `ed`, `m4`, and `ptx`.  

'tty'
    
Used in GDB.  

'typedefs'
    
'-t' in `ctags`.  

'typedefs-and-c++'
    
'-T' in `ctags`.  

'typeset-mode'
    
'-t' in `ptx`.  

'uncompress'
    
'-z' in `tar`.  

'unconditional'
    
'-u' in `cpio`.  

'undefine'
    
'-U' in `m4`.  

'undefined-only'
    
'-u' in `nm`.  

'update'
    
'-u' in `cp`, `ctags`, `mv`, `tar`.  

'usage'
    
Used in `gawk`; same as '--help'.  

'uuencode'
    
'-B' in `shar`.  

'vanilla-operation'
    
'-V' in `shar`.  

'verbose'
    
Print more information about progress. Many programs support this.  

'verify'
    
'-W' in `tar`.  

'version'
    
Print the version number.  

'version-control'
    
'-V' in `cp`, `ln`, `mv`.  

'vgrind'
    
'-v' in `ctags`.  

'volume'
    
'-V' in `tar`.  

'what-if'
    
'-W' in `make`.  

'whole-size-limit'
    
'-l' in `shar`.  

'width'
    
'-w' in `ls` and `ptx`.  

'word-regexp'
    
'-W' in `ptx`.  

'writable'
    
'-T' in `who`.  

'zeros'
    
'-z' in `gprof`.
```

## 4.12 Memory Usage

If a program typically uses just a few meg of memory, don't bother making any effort to reduce memory usage. For example, if it is impractical for other reasons to operate on files more than a few meg long, it is reasonable to read entire input files into memory to operate on them. 

However, for programs such as `cat` or `tail`, that can usefully operate on very large files, it is important to avoid using a technique that would artificially limit the size of files it can handle. If a program works by lines and could be applied to arbitrary user-supplied input files, it should keep only a line in memory, because this is not very hard and users will want to be able to operate on input files that are bigger than will fit in memory all at once. 

If your program creates complicated data structures, just make them in memory and give a fatal error if `malloc` returns `NULL`. 

Memory analysis tools such as `valgrind` can be useful, but don't complicate a program merely to avoid their false alarms. For example, if memory is used until just before a process exits, don't free it simply to silence such a tool.

## 4.13 File Usage

Programs should be prepared to operate when /usr and /etc are read-only file systems. Thus, if the program manages log files, lock files, backup files, score files, or any other files which are modified for internal purposes, these files should not be stored in /usr or /etc. 

There are two exceptions. /etc is used to store system configuration information; it is reasonable for a program to modify files in /etc when its job is to update the system configuration. Also, if the user explicitly asks to modify one file in a directory, it is reasonable for the program to store other files in the same directory.

