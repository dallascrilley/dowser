# Fabric Pattern Database

Complete reference of 242+ Fabric patterns organized by category.

> **Quick Pattern Lookup**: Use `fabric --list` or `fabric --pattern suggest_pattern` to get AI-powered pattern recommendations based on your task.

## Table of Contents

- [AI Patterns](#ai-patterns)
- [Analysis Patterns](#analysis-patterns)
- [Extraction Patterns](#extraction-patterns)
- [Summarization Patterns](#summarization-patterns)
- [Writing Patterns](#writing-patterns)
- [Development Patterns](#development-patterns)
- [Security Patterns](#security-patterns)
- [Business Patterns](#business-patterns)
- [Learning Patterns](#learning-patterns)
- [Visualization Patterns](#visualization-patterns)
- [Conversion Patterns](#conversion-patterns)
- [Research Patterns](#research-patterns)
- [Review Patterns](#review-patterns)
- [Critical Thinking Patterns](#critical-thinking-patterns)
- [Strategy Patterns](#strategy-patterns)
- [Creativity Patterns](#creativity-patterns)
- [Gaming Patterns](#gaming-patterns)
- [Wellness Patterns](#wellness-patterns)
- [Personal Development Patterns](#personal-development-patterns)
- [Other Patterns](#other-patterns)

---

## AI Patterns

Patterns for working with AI, prompts, and model outputs.

### ai
Provide concise, insightful answers in brief bullets focused on core concepts.

**Usage**: `fabric --pattern ai`

### create_art_prompt
Transform concepts into detailed AI art prompts with style references.

**Usage**: `fabric --pattern create_art_prompt`

### create_pattern
Design structured patterns for AI prompts with identity, purpose, steps, output.

**Usage**: `fabric --pattern create_pattern`

### create_prediction_block
Format predictions for tracking/verification in markdown prediction logs.

**Usage**: `fabric --pattern create_prediction_block`

### extract_wisdom_agents
Extract insights from AI agent interactions, focusing on learning.

**Usage**: `fabric --pattern extract_wisdom_agents`

### improve_prompt
Enhance AI prompts by refining clarity and specificity.

**Usage**: `fabric --pattern improve_prompt`

### judge_output
Evaluate AI outputs for quality and accuracy.

**Usage**: `fabric --pattern judge_output`

### rate_ai_response
Evaluate AI responses for quality and effectiveness.

**Usage**: `fabric --pattern rate_ai_response`

### rate_ai_result
Assess AI outputs against criteria, providing scores and feedback.

**Usage**: `fabric --pattern rate_ai_result`

### raw_query
Process direct queries by interpreting intent.

**Usage**: `fabric --pattern raw_query`

### suggest_pattern
**⭐ KEY PATTERN** - Recommend Fabric patterns based on user requirements.

**Usage**: `echo "I want to extract insights from a research paper" | fabric --pattern suggest_pattern`

---

## Analysis Patterns

Patterns for analyzing, evaluating, and assessing content.

### analyze_answers
Evaluate student responses providing detailed feedback adapted to levels.

### analyze_bill / analyze_bill_short
Analyze legislative bills and implications. Short version is condensed.

### analyze_candidates
Compare candidate positions, policy differences and backgrounds.

### analyze_cfp_submission
Evaluate conference submissions for content, speaker qualifications and educational value.

### analyze_claims
**⭐ POPULAR** - Evaluate truth claims by analyzing evidence and logical fallacies.

**Usage**: `pbpaste | fabric --stream --pattern analyze_claims`

### analyze_comments
Analyze user comments for sentiment, extract praise/criticism, and summarize reception.

### analyze_debate
Analyze debates identifying arguments, agreements, and emotional intensity.

### analyze_interviewer_techniques
Study interviewer questions/methods to identify effective interview techniques.

### analyze_military_strategy
Examine battles analyzing strategic decisions to extract military lessons.

### analyze_mistakes
Analyze past errors to prevent similar mistakes in predictions/decisions.

### analyze_paper / analyze_paper_simple
Analyze scientific papers to identify findings and assess conclusion. Simple version is more concise.

### analyze_patent
Analyze patents to evaluate novelty and technical advantages.

### analyze_personality
Psychological analysis by examining language to reveal personality traits.

### analyze_presentation
Evaluate presentations scoring novelty, value for feedback.

### analyze_product_feedback
Process user feedback to identify themes and prioritize insights.

### analyze_proposition
Examine ballot propositions to assess purpose and potential impact.

### analyze_prose / analyze_prose_json / analyze_prose_pinker
Evaluate writing quality by rating novelty, clarity, and style. JSON version provides structured output. Pinker version uses Pinker's principles.

### analyze_sales_call
Evaluate sales calls analyzing pitch, fundamentals, and customer interaction.

### analyze_spiritual_text
Compare religious texts with KJV, identifying claims and doctrinal variations.

### analyze_tech_impact
Evaluate tech projects' societal impact across dimensions.

### analyze_terraform_plan
Analyze Terraform plans for infrastructure changes, security risks, and cost implications.

### check_agreement
Review contract to identify stipulations, issues, and changes for negotiation.

### compare_and_contrast
Create comparisons table, highlighting key differences and similarities.

**Usage**: `fabric --pattern compare_and_contrast < comparison.md`

---

## Extraction Patterns

Patterns for extracting specific types of information from content.

### create_aphorisms
Compile relevant, attributed aphorisms from historical figures on topics.

### create_upgrade_pack
Extract world model updates/algorithms to improve decision-making.

### create_video_chapters
Organize video content into timestamped chapters highlighting key topics.

### extract_algorithm_update_recommendations
Extract recommendations for improving algorithms, focusing on steps.

### extract_alpha
**⭐ ADVANCED** - Extracts the most novel and surprising ideas ("alpha") from content, inspired by information theory.

### extract_article_wisdom
Extract wisdom from articles, organizing into actionable takeaways.

### extract_book_ideas
Extract novel ideas from books to inspire new projects.

### extract_book_recommendations
Extract/prioritize practical advice from books.

### extract_characters
Identify all characters (human and non-human), resolve their aliases and pronouns into canonical names.

### extract_controversial_ideas
Analyze contentious viewpoints while maintaining objective analysis.

### extract_core_message
Distill the fundamental message into a single, impactful sentence.

### extract_domains
Extract key content and source.

### extract_extraordinary_claims
Identify/extract claims contradicting scientific consensus.

### extract_ideas
**⭐ POPULAR** - Extract/organize concepts and applications into idea collections.

### extract_insights / extract_insights_dm
Extract insights about life, tech, presenting as bullet points. DM version for direct messages.

### extract_instructions
Extract procedures into clear instructions for implementation.

### extract_jokes
Extract/categorize jokes, puns, and witty remarks.

### extract_latest_video
Extract info from the latest video, including title and content.

### extract_main_activities
Extract and list main events from transcripts.

### extract_main_idea
Identify key idea, providing core concept and recommendation.

### extract_mcp_servers
Analyzes content to identify and extract detailed information about Model Context Protocol (MCP) servers.

### extract_most_redeeming_thing
Identify the most positive aspect from content.

### extract_patterns
Extract patterns and themes to create reusable templates.

### extract_predictions
Identify/analyze predictions, claims, confidence, and verification.

### extract_primary_problem
Identify/analyze the core problem / root causes.

### extract_primary_solution
Identify/analyze the main solution proposed in content.

### extract_product_features
Extract/categorize product features into a structured list.

### extract_questions
Extract/categorize questions to create Q&A resources.

### extract_recipe
Extract/format recipes into instructions with ingredients and steps.

### extract_recommendations
**⭐ POPULAR** - Extract recommendations, organizing into actionable guidance.

### extract_references
Extract/format citations into a structured reference list.

### extract_skills
Extract/classify hard/soft skills from job descriptions into skill inventory.

### extract_song_meaning
Analyze song lyrics to uncover deeper meanings and themes.

### extract_sponsors
Extract/organize sponsorship info, including names and messages.

### extract_videoid
Extract/parse video IDs and URLs to create video lists.

### extract_wisdom
**⭐ MOST POPULAR** - Extract insightful ideas and recommendations focusing on life wisdom.

**Usage**:
```bash
pbpaste | fabric --pattern extract_wisdom
fabric -y "https://youtube.com/watch?v=VIDEO_ID" --pattern extract_wisdom
```

### extract_wisdom_dm / extract_wisdom_nometa / extract_wisdom_short
Extract learnings from DMs (dm), pure wisdom without metadata (nometa), condensed version (short).

---

## Summarization Patterns

Patterns for creating summaries at various levels of detail.

### capture_thinkers_work
**⭐ POPULAR** - Extract key concepts, background, and ideas from notable thinkers' work.

### create_5_sentence_summary
Generate concise summaries of content in five levels, five words to one.

### create_micro_summary
Generate concise summaries with one-sentence overview and key points.

### create_summary
Generate concise summaries by extracting key points and main ideas.

### summarize
**⭐ POPULAR** - Generate summaries capturing key points and details.

**Usage**: `pbpaste | fabric --pattern summarize`

### summarize_board_meeting
Convert board meeting transcripts into formal meeting notes for corporate records.

### summarize_debate
Summarize debates highlighting arguments and agreements.

### summarize_lecture
Summarize lectures capturing key concepts and takeaways.

### summarize_legislation
Summarize legislation highlighting key provisions and implications.

### summarize_meeting
Summarize meetings capturing discussions and decisions.

### summarize_micro
Generate extremely concise summaries of content.

### summarize_newsletter
Summarize newsletters highlighting updates and trends.

### summarize_paper
Summarize papers highlighting objectives and findings.

### summarize_prompt
Summarize AI prompts to identify instructions and outputs.

### summarize_pull-requests
Summarize pull requests highlighting code changes.

### summarize_rpg_session
Summarize RPG sessions capturing story events and decisions.

### youtube_summary
**⭐ POPULAR** - Summarize YouTube videos with key points and timestamps.

**Usage**: `fabric -y "VIDEO_URL" --pattern youtube_summary`

---

## Writing Patterns

Patterns for creating and improving written content.

### clean_text
Format/clean text by fixing breaks, punctuation, preserving content/meaning.

### create_academic_paper
Transform content into academic papers using LaTeX layout.

### create_diy
Create step-by-step DIY tutorials with clear instructions and materials.

### create_formal_email
Compose professional emails with proper tone and structure.

**Usage**: `echo "Need meeting about project" | fabric --pattern create_formal_email`

### create_keynote
Design TED-style presentations with narrative, slides and notes.

### create_newsletter_entry
Write concise newsletter content focusing on key insights.

### create_show_intro
Craft compelling podcast/show intros to engage audience.

### create_story_about_people_interaction
Analyze two personas, compare their dynamics, and craft a realistic, character-driven story.

### create_story_explanation
Transform complex concepts into clear, engaging narratives.

### enrich_blog_post
Enhance blog posts by improving structure and visuals for static sites.

### explain_docs
Transform technical docs into clearer explanations with examples.

### explain_terms
Create glossaries of advanced terms with definitions and analogies.

### fix_typos
Proofreads and corrects typos, spelling, grammar, and punctuation errors.

### humanize
Transform technical content into approachable language.

### improve_academic_writing
Enhance academic writing by improving clarity and structure.

### improve_writing
**⭐ POPULAR** - Enhance writing by improving clarity, flow, and style.

**Usage**: `pbpaste | fabric --pattern improve_writing`

### md_callout
Generate markdown callout blocks to highlight info.

### t_create_opening_sentences
Generate compelling opening sentences for content.

### t_give_encouragement
Generate personalized messages of encouragement.

### transcribe_minutes
Convert meeting recordings into structured minutes.

### tweet
**⭐ POPULAR** - Transform content into concise tweets.

**Usage**: `fabric -u "BLOG_URL" --pattern tweet`

### write_essay / write_essay_pg
Write essays on given topics. PG version follows Paul Graham's style.

### write_latex
Generate LaTeX documents with proper formatting.

### write_micro_essay
Create concise essays presenting a single key idea.

---

## Development Patterns

Patterns for software development workflows.

### agility_story
Generate agile user stories and acceptance criteria following agile formats.

### analyze_logs
Examine server logs to identify patterns and potential system issues.

### answer_interview_question
Generate appropriate responses to technical interview questions.

### ask_uncle_duke
Expert software dev guidance focusing on Java, Spring, frontend, and best practices.

### coding_master
Explain coding concepts/languages for beginners.

### create_coding_feature
Generate secure and composable code features using latest technology and best practices.

### create_coding_project
Design coding projects with clear architecture, steps, and best practices.

### create_design_document
Create software architecture docs using C4 model.

### create_git_diff_commit
**⭐ POPULAR** - Generate clear git commit messages and commands for code changes.

**Usage**: `git diff --staged | fabric --pattern create_git_diff_commit`

### create_loe_document
Create detailed Level of Effort (LOE) estimation documents.

### create_prd
Create Product Requirements Documents (PRDs) from input specs.

### create_user_story
Write clear user stories with descriptions and acceptance criteria.

### explain_code
**⭐ POPULAR** - Analyze/explain code, security tool outputs, and configs.

**Usage**: `pbpaste | fabric --pattern explain_code`

### explain_project
Create project overviews with instructions and usage examples.

### extract_poc
Extract/document proof-of-concept demos from technical content.

### generate_code_rules
Extracts a list of best practices rules for AI coding assisted tools.

### official_pattern_template
Define pattern templates with sections for consistent creation.

### recommend_pipeline_upgrades
Suggest CI/CD pipeline improvements for efficiency and security.

### refine_design_document
Enhance design docs by improving clarity and accuracy.

### review_code
**⭐ POPULAR** - Performs a comprehensive code review, providing detailed feedback.

**Usage**: `git diff | fabric --pattern review_code`

### review_design
Evaluate software designs for scalability and security.

### summarize_git_changes / summarize_git_diff
Summarize git changes highlighting key modifications.

### write_pull-request
Create pull request descriptions with summaries of changes.

---

## Security Patterns

Patterns for cybersecurity analysis and threat modeling.

### analyze_email_headers
Analyze email authentication headers to assess security and provide recommendations.

### analyze_incident
Extract info from breach articles, including attack details and impact.

### analyze_malware
**⭐ SECURITY** - Analyze malware behavior, extract IOCs, MITRE ATT&CK, provide recommendations.

### analyze_risk
Assess vendor security compliance to determine risk levels.

### analyze_threat_report / analyze_threat_report_cmds / analyze_threat_report_trends
Extract/analyze insights, trends, and recommendations from threat reports. Commands version interprets commands. Trends version focuses on patterns.

### ask_secure_by_design_questions
Generate security-focused questions to guide secure system design.

### create_command
Generate precise CLI commands for penetration testing tools based on docs.

### create_cyber_summary
Summarize incidents, vulnerabilities into concise intelligence briefings.

### create_network_threat_landscape
Analyze network ports/services to create threat reports with recommendations.

### create_report_finding
Document security findings with descriptions, recommendations, and evidence.

### create_security_update
Compile security newsletters covering threats, advisories, developments with links.

### create_sigma_rules
Extract TTPs and translate them into YAML Sigma detection rules.

### create_stride_threat_model
**⭐ SECURITY** - Generate threat models using STRIDE to prioritize security threats.

**Usage**: `fabric --pattern create_stride_threat_model < design.md`

### create_threat_scenarios
Develop realistic security threat scenarios based on risk analysis.

### create_ttrc_graph / create_ttrc_narrative
Generate time-series for visualizing vulnerability remediation metrics (graph). Create narratives for security program improvements (narrative).

### extract_ctf_writeup
Extract techniques from CTF writeups to create learning resources.

### improve_report_finding
Enhance security report by improving clarity and accuracy.

### t_threat_model_plans
Analyze plans through a security lens to identify threats.

### write_hackerone_report
Create vulnerability reports following HackerOne's format.

### write_nuclei_template_rule
Generate Nuclei scanning templates with detection logic.

### write_semgrep_rule
Create Semgrep rules for static code analysis.

---

## Business Patterns

Patterns for business workflows and communications.

### create_hormozi_offer
Create compelling business offers using Alex Hormozi's methodology.

### extract_business_ideas
Identify business opportunities and insights.

### t_check_metrics
Analyze metrics, tracking progress and identifying trends.

### t_create_h3_career
Generate career plans using the Head, Heart, Hands framework.

### t_visualize_mission_goals_projects
Visualize missions and goals to clarify relationships.

### t_year_in_review
Generate annual reviews by analyzing achievements and learnings.

---

## Learning Patterns

Patterns for education and knowledge transfer.

### create_flash_cards / to_flashcards
Generate flashcards for key concepts and definitions.

### create_quiz
Generate review questions adapting difficulty to student levels.

### create_reading_plan
Design three-phase reading plans to build knowledge of topics.

### dialog_with_socrates
Engage in Socratic dialogue to explore ideas via questioning.

### explain_math
Explain math concepts for students using step-by-step instructions.

---

## Visualization Patterns

Patterns for creating diagrams and visual content.

### create_conceptmap
Transform unstructured text or markdown content into interactive HTML concept maps using Vis.js.

### create_excalidraw_visualization
Create visualizations using Excalidraw.

### create_graph_from_input
Transform security metrics to CSV for visualizing progress over time.

### create_idea_compass
Organize thoughts analyzing definitions, evidence, relationships, implications.

### create_investigation_visualization
Create Graphviz vis. of investigation data showing relationships and findings.

### create_logo
Generate minimalist logo prompts capturing brand essence via vector graphics.

### create_markmap_visualization
**⭐ VISUALIZATION** - Transform complex ideas into mind maps using Markmap syntax.

### create_mermaid_visualization / create_mermaid_visualization_for_github
**⭐ POPULAR** - Transform concepts into visual diagrams using Mermaid syntax. GitHub version optimized for GitHub markdown.

**Usage**: `echo "authentication flow" | fabric --pattern create_mermaid_visualization`

### create_visualization
Transform concepts to ASCII art with explanations of relationships.

---

## Conversion Patterns

Patterns for format conversion and transformation.

### convert_to_markdown
Convert content to markdown, preserving original content and structure.

### export_data_as_csv
Extract data and convert to CSV, preserving data integrity.

### get_youtube_rss
Generate RSS feed URLs for YouTube channels.

### sanitize_broken_html_to_markdown
Clean/convert malformed HTML to markdown.

### translate
Convert content between languages while preserving meaning.

---

## Research Patterns

Patterns for academic and research workflows.

### identify_dsrp_distinctions / identify_dsrp_perspectives / identify_dsrp_relationships / identify_dsrp_systems
Analyze content using DSRP framework (Distinctions, Systems, Relationships, Perspectives).

### prepare_7s_strategy
Apply McKinsey 7S framework to analyze organizational alignment.

---

## Review Patterns

Patterns for evaluating and rating content.

### get_wow_per_minute
Calculate frequency of impressive moments to measure engagement.

### label_and_rate
**⭐ POPULAR** - Categorize/evaluate content by assigning labels and ratings.

### rate_content
Evaluate content quality across dimensions, providing scoring.

### rate_value
Assess practical value of content by evaluating utility.

---

## Critical Thinking Patterns

Patterns for logical analysis and bias detection.

### find_hidden_message
Analyze content to uncover concealed meanings and implications.

### find_logical_fallacies
**⭐ CRITICAL** - Identify/analyze logical fallacies to evaluate argument validity.

### t_check_dunning_kruger
Analyze cognitive biases to identify overconfidence using Dunning-Kruger principles.

### t_find_blindspots
Identify blind spots in thinking to improve awareness.

### t_find_negative_thinking
Identify negative thinking patterns to recognize distortions.

### t_red_team_thinking
Apply adversarial thinking to identify weaknesses.

---

## Strategy Patterns

Patterns for strategic analysis and planning.

### create_better_frame
Develop positive mental frameworks for challenging situations.

### create_recursive_outline
Break down tasks into hierarchical, actionable components via decomposition.

### t_analyze_challenge_handling
Evaluate challenge handling by analyzing response strategies.

### t_find_neglected_goals
Identify neglected goals to surface opportunities.

---

## Creativity Patterns

Patterns for creative content generation.

### create_mnemonic_phrases
Create memorable mnemonic sentences using given words in exact order for memory aids.

### create_tags
Generate single-word tags for content categorization and mind mapping.

---

## Gaming Patterns

Patterns for RPG and gaming content.

### create_npc
Generate detailed D&D 5E NPC characters with backgrounds and game stats.

### create_rpg_summary
Summarize RPG sessions capturing events, combat, and narrative.

---

## Wellness Patterns

Patterns for personal health and well-being.

### recommend_yoga_practice
Provides personalized yoga sequences, meditation guidance, and holistic lifestyle advice.

---

## Personal Development Patterns

Patterns for self-improvement and growth.

### create_story_about_person
Infer everyday challenges and realistic coping strategies from a psychological profile.

### find_female_life_partner
Clarify and summarize partner criteria in direct language.

### heal_person
Analyze a psychological profile, pinpoint issues and strengths, deliver structured strategies for improvement.

### model_as_sherlock_freud
Builds psychological models using detective reasoning and psychoanalytic insight.

### predict_person_actions
Predicts behavioral responses based on psychological profiles and challenges.

### provide_guidance
Offer expert advice tailored to situations, providing steps.

### recommend_artists
Suggest artists based on user preferences and style.

### recommend_talkpanel_topics
Generate discussion topics for panel talks based on interests.

---

## Other Patterns

Miscellaneous patterns.

### apply_ul_tags
Apply standardized content tags to categorize topics like AI, cybersecurity, politics, and culture.

### identify_job_stories
Extract/analyze user job stories to understand motivations.

---

## Pattern Categories Quick Reference

**Most Popular Patterns:**
- `extract_wisdom` - Universal insight extraction
- `summarize` - General summarization
- `analyze_claims` - Fact checking
- `improve_writing` - Writing enhancement
- `review_code` - Code review
- `create_git_diff_commit` - Commit messages
- `suggest_pattern` - Pattern recommendations

**Best for Beginners:**
- `summarize`
- `extract_main_idea`
- `create_micro_summary`
- `clean_text`
- `tweet`

**Advanced Patterns:**
- `extract_alpha`
- `capture_thinkers_work`
- `create_stride_threat_model`
- `analyze_malware`
- `create_sigma_rules`

**Multi-Step Workflows:**
1. Research: `extract_wisdom` → `capture_thinkers_work` → `label_and_rate`
2. Security: `analyze_threat_report` → `create_sigma_rules` → `create_stride_threat_model`
3. Content: `extract_ideas` → `create_story_explanation` → `improve_writing`
4. Code: `explain_code` → `review_code` → `create_git_diff_commit`

---

## Usage Examples by Category

### Content Analysis
```bash
# Extract insights from article
fabric -u "ARTICLE_URL" --pattern extract_wisdom

# Analyze claims in article
fabric -u "ARTICLE_URL" --pattern analyze_claims

# Get quick summary
pbpaste | fabric --pattern create_micro_summary
```

### Development
```bash
# Explain code snippet
pbpaste | fabric --pattern explain_code

# Review code changes
git diff | fabric --pattern review_code

# Generate commit message
git diff --staged | fabric --pattern create_git_diff_commit
```

### Security
```bash
# Threat model
fabric --pattern create_stride_threat_model < design.md

# Analyze malware report
fabric --pattern analyze_malware < report.txt
```

### Writing
```bash
# Improve writing
pbpaste | fabric --pattern improve_writing

# Create tweet
fabric -u "BLOG_URL" --pattern tweet

# Professional email
echo "need meeting" | fabric --pattern create_formal_email
```

---

## Custom Pattern Categories

You can create your own custom patterns in:
`~/.config/fabric/patterns/your-pattern-name/system.md`

Use the `create_pattern` pattern to help design new ones:
```bash
echo "I need a pattern that does X" | fabric --pattern create_pattern
```

---

## Pattern Update

Keep patterns current:
```bash
fabric --updatepatterns
```

Check pattern version:
```bash
fabric --version
```

---

*Last updated: Generated from Fabric official pattern database*
