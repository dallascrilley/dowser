Core Concepts
Relevant source files
Purpose and Scope
This page introduces three foundational concepts that span the entire Codex codebase:

The Op/Event Protocol - The asynchronous communication pattern used between user interfaces and the core agent system
Configuration System - How configuration is loaded, merged, and applied throughout the system
Model Families and Capabilities - How different AI models are characterized and configured
These concepts form the architectural foundation upon which all user interfaces (TUI, exec, MCP server) and the core agent system are built. For detailed information about specific subsystems:

For the protocol's implementation details, see Protocol Layer (Op/Event System)
For configuration file structure and loading, see Configuration System
For model-specific configurations, see Model Families and Capabilities
For how these concepts are used in the core agent, see Core Agent System
The Op/Event Protocol
The Op/Event protocol implements a Submission Queue (SQ) / Event Queue (EQ) pattern for asynchronous communication between user interfaces and the Codex core agent system. This pattern decouples input submission from output consumption, enabling non-blocking interaction with the AI model.

Architecture Overview

Key Characteristics:

Aspect	Implementation
Input Direction	User → Core via Op enum
Output Direction	Core → User via EventMsg enum
Concurrency Model	Bounded sender, unbounded receiver
Correlation	Each Event carries the id of its originating Submission
State Management	Stateless protocol; state lives in Codex session manager
Submission Operations (Op)
The Op enum defines all possible operations that can be submitted to the core. Each operation is wrapped in a Submission struct with a unique id for correlation.

Primary Operations:

Op::UserInput        - Submit text/images from user
Op::UserTurn         - Submit with full turn context (cwd, policies, model)
Op::Interrupt        - Abort current task
Op::ExecApproval     - Approve/reject a command execution
Op::PatchApproval    - Approve/reject a code patch
Op::Shutdown         - Terminate the session
Context Management:

Op::OverrideTurnContext  - Update default policies without enqueuing input
Sources: 
codex-rs/protocol/src/protocol.rs
42-181

Event Messages (EventMsg)
The EventMsg enum defines all possible events emitted by the core. Events are wrapped in an Event struct that includes the correlation id.

Lifecycle Events:

EventMsg::TaskStarted      - Agent begins processing
EventMsg::TaskComplete     - Agent finishes processing
EventMsg::TurnAborted      - Task was interrupted
EventMsg::Error            - Fatal error occurred
Streaming Content:

EventMsg::AgentMessage      - Complete agent response
EventMsg::AgentMessageDelta - Incremental agent output
EventMsg::AgentReasoning    - Model reasoning/thinking
Tool Execution:

EventMsg::ExecCommandBegin    - Shell command starting
EventMsg::ExecCommandEnd      - Shell command finished
EventMsg::McpToolCallBegin    - MCP tool starting
EventMsg::McpToolCallEnd      - MCP tool finished
EventMsg::PatchApplyBegin     - File patch starting
EventMsg::PatchApplyEnd       - File patch finished
Approval Requests:

EventMsg::ExecApprovalRequest      - Request approval for command
EventMsg::ApplyPatchApprovalRequest - Request approval for patch
Sources: 
codex-rs/protocol/src/protocol.rs
412-527

Communication Flow
Key Implementation Details:

Submissions are sent via conversation.submit(Op) which returns an event ID
Events are consumed via conversation.next_event() which blocks until available
The core maintains an ActiveTurn context during processing
Interrupts are handled by checking a cancellation token during stream processing
Sources: 
codex-rs/protocol/src/protocol.rs
1-5
 
codex-rs/mcp-server/src/codex_tool_runner.rs
152-314
 
codex-rs/exec/src/lib.rs
280-403

Configuration System
The configuration system implements a hierarchical merge strategy where settings from multiple sources are combined with a well-defined precedence order. This allows users to specify defaults globally while overriding them per-session or per-command.

Configuration Precedence









Precedence Rule: CLI Overrides > Profile Settings > config.toml > Defaults

Configuration Sources
Source	Location	Format	Applied By
CLI Arguments	Command-line flags	Flags like --model gpt-4	ConfigOverrides
-c Overrides	CLI key-value pairs	-c key.subkey=value	apply_toml_override()
Active Profile	~/.codex/config.toml	[profiles.NAME] table	Profile resolution
Base Config	~/.codex/config.toml	Root TOML entries	TOML deserialization
Defaults	Compiled-in constants	Rust constants	Fallback values
The Config Struct
The Config struct is the resolved, runtime configuration used throughout the system:

Config {
    // Model Configuration
    model: String                          - Active model name
    model_family: ModelFamily              - Derived capabilities
    model_provider: ModelProviderInfo      - API configuration
    model_reasoning_effort: Option<_>      - Reasoning parameter
    
    // Security & Sandboxing
    approval_policy: AskForApproval        - When to ask for approval
    sandbox_policy: SandboxPolicy          - Filesystem/network restrictions
    
    // Paths & Context
    cwd: PathBuf                           - Working directory
    codex_home: PathBuf                    - ~/.codex location
    
    // MCP Integration
    mcp_servers: HashMap<String, _>        - Configured MCP servers
    
    // Model Providers
    model_providers: HashMap<String, _>    - Available API providers
    
    // Features
    features: Features                     - Feature flags
}
Sources: 
codex-rs/core/src/config.rs
76-257

Configuration Loading Flow










Key Functions:

find_codex_home() - Locates ~/.codex or respects $CODEX_HOME
load_config_layers_with_overrides() - Reads TOML file and splits into layers
apply_overlays() - Merges layers with CLI overrides
apply_toml_override() - Handles dotted-path overrides like -c model.provider=custom
load_from_base_config_with_overrides() - Applies ConfigOverrides struct
Sources: 
codex-rs/core/src/config.rs
260-308
 
codex-rs/core/src/config.rs
765-806

ConfigOverrides Struct
CLI-level overrides are expressed via the ConfigOverrides struct, which is applied after TOML deserialization:

ConfigOverrides {
    model: Option<String>
    approval_policy: Option<AskForApproval>
    sandbox_mode: Option<SandboxMode>
    cwd: Option<PathBuf>
    config_profile: Option<String>
    base_instructions: Option<String>
    include_plan_tool: Option<bool>
    // ... other overrides
}
This allows interfaces (TUI, exec, MCP server) to programmatically override config without modifying config.toml.

Sources: 
codex-rs/tui/src/lib.rs
166-182
 
codex-rs/exec/src/lib.rs
168-185
 
codex-rs/mcp-server/src/codex_tool_config.rs
132-168

Key Configuration Fields
Field	Type	Purpose	Example Values
approval_policy	AskForApproval	When to request approval	UnlessTrusted, OnRequest, Never
sandbox_policy	SandboxPolicy	Execution restrictions	ReadOnly, WorkspaceWrite, DangerFullAccess
model_provider_id	String	Which API provider	"openai", "oss", custom key
mcp_servers	HashMap	MCP server configs	Server name → transport config
features	Features	Feature flags	Centralized feature gating
Sources: 
codex-rs/core/src/config.rs
101-236

Model Families and Capabilities
The ModelFamily concept abstracts model-specific behaviors and capabilities, allowing the system to adapt prompts, tools, and features based on which AI model is being used.

Model Family Abstraction

Model Detection and Resolution
The system uses a two-step process to determine the active model family:

Model Selection: User specifies model name via config, CLI, or defaults
Family Lookup: System maps model name to ModelFamily enum
Model Name               →  ModelFamily
─────────────────────────────────────────
"gpt-5-codex"           →  Gpt5Codex
"gpt-4o"                →  Gpt4o  
"o3"                    →  O3
"gpt-oss:*"             →  OpenSource
(unknown)               →  derive_default_model_family()
Sources: 
codex-rs/core/src/config.rs
27-28

ModelFamily Struct
Each ModelFamily encapsulates:

ModelFamily {
    // Prompt Configuration
    base_instructions: String           - System-level prompt
    
    // Tool Availability
    tools_config: ToolsConfig          - Which tools to expose
    
    // API Capabilities
    supports_streaming: bool           - SSE support
    supports_reasoning: bool           - reasoning.effort parameter
    reasoning_summary_format: Option<_> - How summaries are structured
    
    // Context Management
    default_context_window: Option<u64> - Token limit
}
Tools Configuration by Model Family
Different models have different tool preferences. The ToolsConfig struct (derived from ModelFamily) controls which tools are available:

Tool	GPT-5-Codex	GPT-4o	O3	OSS
read_file	✓	✓	✓	✓
list_dir	✓	✓	✓	✓
exec_command	✓	✓	✓	✓
apply_patch	✓	Optional	Optional	✗
plan	Optional	Optional	Optional	✗
MCP Tools	✓	✓	✓	✓
Tool Selection Logic:

Some models benefit from structured apply_patch calls instead of raw edits
The plan tool is experimental and can be enabled via config
MCP tools are universally supported but require server configuration

Base Instructions
Each ModelFamily defines default system instructions that are prepended to every conversation. These instructions:

Define the agent's identity and purpose
Specify available tools and their usage patterns
Set expectations for output format
Can be overridden via config.base_instructions or ConfigOverrides
The instructions adapt based on:

Active ToolsConfig (which tools are mentioned)
SandboxPolicy (what restrictions apply)
User-provided AGENTS.md files (project-specific context)
Sources: 
codex-rs/core/src/config.rs
122-125

Reasoning Configuration
Models that support reasoning (e.g., O3, GPT-5-Codex) accept additional parameters:

Parameter	Type	Purpose	Values
model_reasoning_effort	ReasoningEffort	Thinking depth	low, medium, high
model_reasoning_summary	ReasoningSummary	Summary format	none, auto, titled-sections
model_verbosity	Verbosity	Output detail	concise, normal, verbose
These are configured in Config and passed through Op::UserTurn to the model client.

Sources: 
codex-rs/core/src/config.rs
199-207
 
codex-rs/protocol/src/protocol.rs
87-92

Integration Points
These three concepts integrate across the entire system:



Cross-Cutting Concerns:

Protocol: All interfaces use Op/Event to communicate with core
Configuration: All interfaces load Config and apply ConfigOverrides
Model Family: Core uses ModelFamily to adapt behavior for active model