Passing Multiple Files/Images
You can attach multiple files or images to Codex using the -i/--image flag with comma-separated paths: getting-started.md:82-87

codex -i screenshot.png "Explain this error"  
codex --image img1.png,img2.jpg "Summarize these diagrams"

Using Custom Prompts (Reusable Templates)
If you want to reuse prompt templates, Codex supports custom prompts stored as Markdown files in $CODEX_HOME/prompts/ (defaults to ~/.codex/prompts/). prompts.md:5-11

Custom prompts support:

Positional arguments: Use $1-$9 for the first nine arguments, or $ARGUMENTS for all arguments joined by spaces prompts.md:30
Named placeholders: Use $FILE, $TICKET_ID, etc., and pass them as KEY=value pairs prompts.md:31
Quoted values: Use double quotes for values with spaces, e.g., TICKET_TITLE="Fix logging" prompts.md:32
Example usage:

/prompts:my-prompt USER=Alice BRANCH=main
chat_composer.rs:2902-2903

The custom prompts system discovers .md files in the prompts directory custom_prompts.rs:43-50 and expands placeholders when you invoke them. chat_composer.rs:2893-2912

Passing a Single Prompt to codex exec
For non-interactive mode, you can pass a prompt as an argument or via stdin: lib.rs:84-116

# Direct argument  
codex exec "Fix the tests"  
  
# Via stdin  
echo "Fix the build" | codex exec  
  
# Explicit stdin mode  
codex exec -


Notes
The --image flag is specifically for attaching image files to your prompt, not for passing multiple text prompts
Custom prompts are the recommended way to create reusable prompt templates with variable substitution
In codex exec, you can only pass one prompt at a time, but you can use custom prompts with arguments to achieve similar flexibility
The @ symbol in the TUI triggers fuzzy file search to reference files in your prompt getting-started.md:76-78
Wiki pages you might want to explore:

Architecture Overview (openai/codex)
Headless Execution Mode (openai/codex)



