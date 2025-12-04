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

## 4.11 OID Allocations

The OID (object identifier) 1.3.6.1.4.1.11591 has been assigned to the GNU Project (thanks to Sergey Poznyakoff). These are used for SNMP, LDAP, X.509 certificates, and so on. The web site <https://www.alvestrand.no/objectid> has a (voluntary) listing of many OID assignments. 

If you need a new slot for your GNU package, write maintainers@gnu.org. Here is a list of arcs currently assigned: 
```

1.3.6.1.4.1.11591 GNU

1.3.6.1.4.1.11591.1 GNU Radius

1.3.6.1.4.1.11591.2 GnuPG
  1.3.6.1.4.1.11591.2.1   notation
  1.3.6.1.4.1.11591.2.1.1 pkaAddress

1.3.6.1.4.1.11591.3 GNU Radar

1.3.6.1.4.1.11591.4 GNU GSS

1.3.6.1.4.1.11591.5 GNU Mailutils

1.3.6.1.4.1.11591.6 GNU Shishi

1.3.6.1.4.1.11591.7 GNU Radio

1.3.6.1.4.1.11591.8 GNU Dico

1.3.6.1.4.1.11591.9 GNU Rush

1.3.6.1.4.1.11591.12 digestAlgorithm
  1.3.6.1.4.1.11591.12.2 TIGER/192

1.3.6.1.4.1.11591.13 encryptionAlgorithm
  1.3.6.1.4.1.11591.13.2 Serpent
    1.3.6.1.4.1.11591.13.2.1 Serpent-128-ECB
    1.3.6.1.4.1.11591.13.2.2 Serpent-128-CBC
    1.3.6.1.4.1.11591.13.2.3 Serpent-128-OFB
    1.3.6.1.4.1.11591.13.2.4 Serpent-128-CFB
    1.3.6.1.4.1.11591.13.2.21 Serpent-192-ECB
    1.3.6.1.4.1.11591.13.2.22 Serpent-192-CBC
    1.3.6.1.4.1.11591.13.2.23 Serpent-192-OFB
    1.3.6.1.4.1.11591.13.2.24 Serpent-192-CFB
    1.3.6.1.4.1.11591.13.2.41 Serpent-256-ECB
    1.3.6.1.4.1.11591.13.2.42 Serpent-256-CBC
    1.3.6.1.4.1.11591.13.2.43 Serpent-256-OFB
    1.3.6.1.4.1.11591.13.2.44 Serpent-256-CFB

1.3.6.1.4.1.11591.14 CRC algorithms
  1.3.6.1.4.1.11591.14.1 CRC 32

1.3.6.1.4.1.11591.15 ellipticCurve
  1.3.6.1.4.1.11591.15.1 Ed25519

```

## 4.12 Memory Usage

If a program typically uses just a few meg of memory, don't bother making any effort to reduce memory usage. For example, if it is impractical for other reasons to operate on files more than a few meg long, it is reasonable to read entire input files into memory to operate on them. 

However, for programs such as `cat` or `tail`, that can usefully operate on very large files, it is important to avoid using a technique that would artificially limit the size of files it can handle. If a program works by lines and could be applied to arbitrary user-supplied input files, it should keep only a line in memory, because this is not very hard and users will want to be able to operate on input files that are bigger than will fit in memory all at once. 

If your program creates complicated data structures, just make them in memory and give a fatal error if `malloc` returns `NULL`. 

Memory analysis tools such as `valgrind` can be useful, but don't complicate a program merely to avoid their false alarms. For example, if memory is used until just before a process exits, don't free it simply to silence such a tool.

## 4.13 File Usage

Programs should be prepared to operate when /usr and /etc are read-only file systems. Thus, if the program manages log files, lock files, backup files, score files, or any other files which are modified for internal purposes, these files should not be stored in /usr or /etc. 

There are two exceptions. /etc is used to store system configuration information; it is reasonable for a program to modify files in /etc when its job is to update the system configuration. Also, if the user explicitly asks to modify one file in a directory, it is reasonable for the program to store other files in the same directory.

