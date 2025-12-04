## What is Fabric?

Fabric organizes prompts by real-world task, allowing people to create, collect, and organize their most important AI solutions in a single place. Fabric organizes prompts, which we call _Patterns_, into various parts of your life and work.

Fabric has Patterns for all sorts of activities, including:

- Extracting the most interesting parts of YouTube videos and podcasts
- Writing an essay in your own voice with just an idea as an input
- Summarizing opaque academic papers
- Creating perfectly matched AI art prompts for a piece of writing
- Rating the quality of content to see if you want to read/watch the whole thing
- Getting summaries of long, boring content
- Explaining code to you
- Turning bad documentation into usable documentation
- Creating social media posts from any content input
- And many more…

## Usage

View all available options:

```bash
fabric -h
```

```plaintext
Usage:
  fabric [OPTIONS]

Application Options:
  -p, --pattern=                    Choose a pattern from the available patterns
  -v, --variable=                   Values for pattern variables, e.g. -v=#role:expert -v=#points:30
  -C, --context=                    Choose a context from the available contexts
      --session=                    Choose a session from the available sessions
  -a, --attachment=                 Attachment path or URL (e.g. for OpenAI image recognition messages)
  -S, --setup                       Run setup for all reconfigurable parts of fabric
  -t, --temperature=                Set temperature (default: 0.7)
  -T, --topp=                       Set top P (default: 0.9)
  -s, --stream                      Stream
  -P, --presencepenalty=            Set presence penalty (default: 0.0)
  -r, --raw                         Use the defaults of the model without sending chat options (like
                                    temperature etc.) and use the user role instead of the system role for
                                    patterns.
  -F, --frequencypenalty=           Set frequency penalty (default: 0.0)
  -l, --listpatterns                List all patterns
  -L, --listmodels                  List all available models
  -x, --listcontexts                List all contexts
  -X, --listsessions                List all sessions
  -U, --updatepatterns              Update patterns
  -c, --copy                        Copy to clipboard
  -m, --model=                      Choose model
  -V, --vendor=                     Specify vendor for chosen model (e.g., -V "LM Studio" -m openai/gpt-oss-20b)
      --modelContextLength=         Model context length (only affects ollama)
  -o, --output=                     Output to file
      --output-session              Output the entire session (also a temporary one) to the output file
  -n, --latest=                     Number of latest patterns to list (default: 0)
  -d, --changeDefaultModel          Change default model
  -y, --youtube=                    YouTube video or play list "URL" to grab transcript, comments from it
                                    and send to chat or print it put to the console and store it in the
                                    output file
      --playlist                    Prefer playlist over video if both ids are present in the URL
      --transcript                  Grab transcript from YouTube video and send to chat (it is used per
                                    default).
      --transcript-with-timestamps  Grab transcript from YouTube video with timestamps and send to chat
      --comments                    Grab comments from YouTube video and send to chat
      --metadata                    Output video metadata
  -g, --language=                   Specify the Language Code for the chat, e.g. -g=en -g=zh
  -u, --scrape_url=                 Scrape website URL to markdown using Jina AI
  -q, --scrape_question=            Search question using Jina AI
  -e, --seed=                       Seed to be used for LMM generation
  -w, --wipecontext=                Wipe context
  -W, --wipesession=                Wipe session
      --printcontext=               Print context
      --printsession=               Print session
      --readability                 Convert HTML input into a clean, readable view
      --input-has-vars              Apply variables to user input
      --no-variable-replacement     Disable pattern variable replacement
      --dry-run                     Show what would be sent to the model without actually sending it
      --serve                       Serve the Fabric Rest API
      --serveOllama                 Serve the Fabric Rest API with ollama endpoints
      --address=                    The address to bind the REST API (default: :8080)
      --api-key=                    API key used to secure server routes
      --config=                     Path to YAML config file
      --version                     Print current version
      --listextensions              List all registered extensions
      --addextension=               Register a new extension from config file path
      --rmextension=                Remove a registered extension by name
      --strategy=                   Choose a strategy from the available strategies
      --liststrategies              List all strategies
      --listvendors                 List all vendors
      --shell-complete-list         Output raw list without headers/formatting (for shell completion)
      --search                      Enable web search tool for supported models (Anthropic, OpenAI, Gemini)
      --search-location=            Set location for web search results (e.g., 'America/Los_Angeles')
      --image-file=                 Save generated image to specified file path (e.g., 'output.png')
      --image-size=                 Image dimensions: 1024x1024, 1536x1024, 1024x1536, auto (default: auto)
      --image-quality=              Image quality: low, medium, high, auto (default: auto)
      --image-compression=          Compression level 0-100 for JPEG/WebP formats (default: not set)
      --image-background=           Background type: opaque, transparent (default: opaque, only for
                                    PNG/WebP)
      --suppress-think              Suppress text enclosed in thinking tags
      --think-start-tag=            Start tag for thinking sections (default: <think>)
      --think-end-tag=              End tag for thinking sections (default: </think>)
      --disable-responses-api       Disable OpenAI Responses API (default: false)
      --voice=                      TTS voice name for supported models (e.g., Kore, Charon, Puck)
                                    (default: Kore)
      --list-gemini-voices          List all available Gemini TTS voices
      --notification                Send desktop notification when command completes
      --notification-command=       Custom command to run for notifications (overrides built-in
                                    notifications)
      --yt-dlp-args=                Additional arguments to pass to yt-dlp (e.g. '--cookies-from-browser brave')
      --thinking=                   Set reasoning/thinking level (e.g., off, low, medium, high, or
                                    numeric tokens for Anthropic or Google Gemini)
      --debug=                     Set debug level (0: off, 1: basic, 2: detailed, 3: trace)
Help Options:
  -h, --help                        Show this help message
```

### Debug Levels

Use the `--debug` flag to control runtime logging:

- `0`: off (default)
- `1`: basic debug info
- `2`: detailed debugging
- `3`: trace level

### Extensions

Fabric supports extensions that can be called within patterns. See the [Extension Guide](internal/plugins/template/Examples/README.md) for complete documentation.

**Important:** Extensions only work within pattern files, not via direct stdin. See the guide for details and examples.

## Our approach to prompting

Fabric _Patterns_ are different than most prompts you'll see.

- **First, we use `Markdown` to help ensure maximum readability and editability**. This not only helps the creator make a good one, but also anyone who wants to deeply understand what it does. _Importantly, this also includes the AI you're sending it to!_

Here's an example of a Fabric Pattern.

```bash
# IDENTITY and PURPOSE

You extract surprising, insightful, and interesting information from text content. You are interested in insights related to the purpose and meaning of life, human flourishing, the role of technology in the future of humanity, artificial intelligence and its affect on humans, memes, learning, reading, books, continuous improvement, and similar topics.

Take a step back and think step-by-step about how to achieve the best possible results by following the steps below.

# STEPS

- Extract a summary of the content in 25 words, including who is presenting and the content being discussed into a section called SUMMARY.

- Extract 20 to 50 of the most surprising, insightful, and/or interesting ideas from the input in a section called IDEAS:. If there are less than 50 then collect all of them. Make sure you extract at least 20.

- Extract 10 to 20 of the best insights from the input and from a combination of the raw input and the IDEAS above into a section called INSIGHTS. These INSIGHTS should be fewer, more refined, more insightful, and more abstracted versions of the best ideas in the content. 

- Extract 15 to 30 of the most surprising, insightful, and/or interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input. Include the name of the speaker of the quote at the end.

- Extract 15 to 30 of the most practical and useful personal habits of the speakers, or mentioned by the speakers, in the content into a section called HABITS. Examples include but aren't limited to: sleep schedule, reading habits, things they always do, things they always avoid, productivity tips, diet, exercise, etc.

- Extract 15 to 30 of the most surprising, insightful, and/or interesting valid facts about the greater world that were mentioned in the content into a section called FACTS:.

- Extract all mentions of writing, art, tools, projects and other sources of inspiration mentioned by the speakers into a section called REFERENCES. This should include any and all references to something that the speaker mentioned.

- Extract the most potent takeaway and recommendation into a section called ONE-SENTENCE TAKEAWAY. This should be a 15-word sentence that captures the most important essence of the content.

- Extract the 15 to 30 of the most surprising, insightful, and/or interesting recommendations that can be collected from the content into a section called RECOMMENDATIONS.

# OUTPUT INSTRUCTIONS

- Only output Markdown.

- Write the IDEAS bullets as exactly 16 words.

- Write the RECOMMENDATIONS bullets as exactly 16 words.

- Write the HABITS bullets as exactly 16 words.

- Write the FACTS bullets as exactly 16 words.

- Write the INSIGHTS bullets as exactly 16 words.

- Extract at least 25 IDEAS from the content.

- Extract at least 10 INSIGHTS from the content.

- Extract at least 20 items for the other output sections.

- Do not give warnings or notes; only output the requested sections.

- You use bulleted lists for output, not numbered lists.

- Do not repeat ideas, insights, quotes, habits, facts, or references.

- Do not start items with the same opening words.

- Ensure you follow ALL these instructions when creating your output.

# INPUT

INPUT:
```

- **Next, we are extremely clear in our instructions**, and we use the Markdown structure to emphasize what we want the AI to do, and in what order.

- **And finally, we tend to use the System section of the prompt almost exclusively**. In over a year of being heads-down with this stuff, we've just seen more efficacy from doing that. If that changes, or we're shown data that says otherwise, we will adjust.

## Examples

> The following examples use the macOS `pbpaste` to paste from the clipboard. See the [pbpaste](#pbpaste) section below for Windows and Linux alternatives.

Now let's look at some things you can do with Fabric.

1. Run the `summarize` Pattern based on input from `stdin`. In this case, the body of an article.

    ```bash
    pbpaste | fabric --pattern summarize
    ```

2. Run the `analyze_claims` Pattern with the `--stream` option to get immediate and streaming results.

    ```bash
    pbpaste | fabric --stream --pattern analyze_claims
    ```

3. Run the `extract_wisdom` Pattern with the `--stream` option to get immediate and streaming results from any      Youtube video (much like in the original introduction video).

    ```bash
    fabric -y "https://youtube.com/watch?v=uXs-zPc63kM" --stream --pattern extract_wisdom
    ```

4. Create patterns- you must create a .md file with the pattern and save it to `~/.config/fabric/patterns/[yourpatternname]`.

5. Run a `analyze_claims` pattern on a website. Fabric uses Jina AI to scrape the URL into markdown format before sending it to the model.

    ```bash
    fabric -u https://github.com/danielmiessler/fabric/ -p analyze_claims
    ```

## Just use the Patterns

<img width="1173" alt="fabric-patterns-screenshot" src="https://github.com/danielmiessler/fabric/assets/50654/9186a044-652b-4673-89f7-71cf066f32d8">

<br />
<br />

If you're not looking to do anything fancy, and you just want a lot of great prompts, you can navigate to the [`/patterns`](https://github.com/danielmiessler/fabric/tree/main/data/patterns) directory and start exploring!

### Prompt Strategies

Fabric also implements prompt strategies like "Chain of Thought" or "Chain of Draft" which can
be used in addition to the basic patterns.

See the [Thinking Faster by Writing Less](https://arxiv.org/pdf/2502.18600) paper and
the [Thought Generation section of Learn Prompting](https://learnprompting.org/docs/advanced/thought_generation/introduction) for examples of prompt strategies.

Each strategy is available as a small `json` file in the [`/strategies`](https://github.com/danielmiessler/fabric/tree/main/data/strategies) directory.

The prompt modification of the strategy is applied to the system prompt and passed on to the
LLM in the chat session.

Use `fabric -S` and select the option to install the strategies in your `~/.config/fabric` directory.

## Custom Patterns

You may want to use Fabric to create your own custom Patterns—but not share them with others. No problem!

Fabric now supports a dedicated custom patterns directory that keeps your personal patterns separate from the built-in ones. This means your custom patterns won't be overwritten when you update Fabric's built-in patterns.

### Setting Up Custom Patterns

1. Run the Fabric setup:

   ```bash
   fabric --setup
   ```

2. Select the "Custom Patterns" option from the Tools menu and enter your desired directory path (e.g., `~/my-custom-patterns`)

3. Fabric will automatically create the directory if it does not exist.

### Using Custom Patterns

1. Create your custom pattern directory structure:

   ```bash
   mkdir -p ~/my-custom-patterns/my-analyzer
   ```

2. Create your pattern file

   ```bash
   echo "You are an expert analyzer of ..." > ~/my-custom-patterns/my-analyzer/system.md
   ```

3. **Use your custom pattern:**

   ```bash
   fabric --pattern my-analyzer "analyze this text"
   ```

### How It Works

- **Priority System**: Custom patterns take precedence over built-in patterns with the same name
- **Seamless Integration**: Custom patterns appear in `fabric --listpatterns` alongside built-in ones
- **Update Safe**: Your custom patterns are never affected by `fabric --updatepatterns`
- **Private by Default**: Custom patterns remain private unless you explicitly share them

Your custom patterns are completely private and won't be affected by Fabric updates!

## Helper Apps

Fabric also makes use of some core helper apps (tools) to make it easier to integrate with your various workflows. Here are some examples:

### `to_pdf`

`to_pdf` is a helper command that converts LaTeX files to PDF format. You can use it like this:

```bash
to_pdf input.tex
```

This will create a PDF file from the input LaTeX file in the same directory.

You can also use it with stdin which works perfectly with the `write_latex` pattern:

```bash
echo "ai security primer" | fabric --pattern write_latex | to_pdf
```

This will create a PDF file named `output.pdf` in the current directory.

### `code_helper`

`code_helper` is used in conjunction with the `create_coding_feature` pattern.
It generates a `json` representation of a directory of code that can be fed into an AI model
with instructions to create a new feature or edit the code in a specified way.

See [the Create Coding Feature Pattern README](./data/patterns/create_coding_feature/README.md) for details.

## pbpaste

The [examples](#examples) use the macOS program `pbpaste` to paste content from the clipboard to pipe into `fabric` as the input. `pbpaste` is not available on Windows or Linux, but there are alternatives.

On Windows, you can use the PowerShell command `Get-Clipboard` from a PowerShell command prompt. If you like, you can also alias it to `pbpaste`. If you are using classic PowerShell, edit the file `~\Documents\WindowsPowerShell\.profile.ps1`, or if you are using PowerShell Core, edit `~\Documents\PowerShell\.profile.ps1` and add the alias,

```powershell
Set-Alias pbpaste Get-Clipboard
```

On Linux, you can use `xclip -selection clipboard -o` to paste from the clipboard. You will likely need to install `xclip` with your package manager. For Debian based systems including Ubuntu,

```sh
sudo apt update
sudo apt install xclip -y
```

You can also create an alias by editing `~/.bashrc` or `~/.zshrc` and adding the alias,

```sh
alias pbpaste='xclip -selection clipboard -o'
```

## Web Interface (Fabric Web App)

Fabric now includes a built-in web interface that provides a GUI alternative to the command-line interface. Refer to [Web App README](/web/README.md) for installation instructions and an overview of features.
