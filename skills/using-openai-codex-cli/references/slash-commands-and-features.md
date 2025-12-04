Summary Table: Key Slash Commands
Command	Description	Available During Task	Handler Function / Event
/model	Choose model and reasoning effort	No	AppEvent::OpenReasoningPopup
/approvals	Choose approval policy	No	AppEvent::OpenApprovalsPopup
/review	Review current changes	No	AppEvent::OpenReviewCustomPrompt
/init	Create AGENTS.md	No	submit_init_agents_md_prompt
/diff	Show git diff	Yes	compute_and_show_diff
/status	Show session config and token usage	Yes	show_status_view
/mcp	List configured MCP tools	Yes	submit_mcp_list_tools_op
/quit	Exit Codex	Yes	AppEvent::ExitRequest
/p:name	Custom prompt (user-defined)	Yes	expand_if_numeric_with_positional_args