Headless Session Storage
Headless sessions follow the same storage mechanism as interactive sessions, but are distinguished by their SessionSource field. protocol.rs:957-968

Sessions are categorized by source:

Interactive sources: Cli and VSCode (defined in INTERACTIVE_SESSION_SOURCES) mod.rs:7-8
Headless sources: Exec and Mcp protocol.rs:964-965
Storage Location
All sessions, regardless of source, are stored in the same location: ~/.codex/sessions/YYYY/MM/DD/rollout-YYYY-MM-DDThh-mm-ss-<uuid>.jsonl. recorder.rs:304-340 The hierarchical date-based directory structure is created by create_log_file() which organizes sessions by year, month, and day. recorder.rs:308-316

Session Metadata
Each session file begins with a SessionMeta line that includes the source field: protocol.rs:970-980

id: Conversation UUID
timestamp: Session start time
cwd: Working directory
originator: Process that created the session
cli_version: Codex version
source: One of Cli, VSCode, Exec, Mcp, or Unknown
Filtering by Source
When listing sessions, you can filter by source. For example, the session listing API accepts an allowed_sources parameter to show only interactive sessions or include all sessions: list.rs:107-112

Tests demonstrate this filtering behavior - headless Exec sessions can be excluded from interactive session lists while still being stored in the same directory structure. tests.rs:873-927

Notes
The key difference between headless and interactive sessions is purely metadata-based (the source field). Both use identical storage formats and locations. The SessionSource enum defaults to VSCode but is explicitly set based on how the session was initiated. protocol.rs:960-968 Headless sessions from codex exec are marked with SessionSource::Exec, while MCP server sessions use SessionSource::Mcp.

Wiki pages you might want to explore: