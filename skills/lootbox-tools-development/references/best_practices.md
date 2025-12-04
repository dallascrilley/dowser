⏺ Design Principles for LLM-Accessible Tools

  1. Consistent Return Patterns

  Every function returns structured data that's easy to chain:

  // Base pattern: Always include metadata for context
  interface BaseResult {
    success: boolean;
    _meta?: {
      source: string;      // "github" | "linear" | "s3"
      operation: string;   // What was done
      timestamp: number;
    };
  }

  2. Resource Identifiers as First-Class

  Use consistent ID patterns so outputs flow into inputs:

  // GitHub uses: owner/repo, issue numbers, PR numbers
  // Linear uses: issue IDs (e.g., "ENG-123")
  // S3 uses: bucket + key

  // Functions return IDs that can feed into other functions
  interface GitHubIssue {
    id: string;           // "owner/repo#123" - composite ID
    number: number;
    repo: string;
    // ...
  }

  3. Layered Architecture

  ┌─────────────────────────────────────────────────┐
  │         COMPOUND FUNCTIONS (workflows.ts)       │
  │   reviewPR(), triageIssues(), deployRelease()   │
  ├─────────────────────────────────────────────────┤
  │              BASE FUNCTIONS                      │
  │   github.ts    linear.ts    s3.ts               │
  ├─────────────────────────────────────────────────┤
  │              SHARED UTILITIES                    │
  │   Pagination, rate limiting, error handling     │
  └─────────────────────────────────────────────────┘

  ---
  Base Functions Design

  github.ts - Core Operations

  // ============================================================
  // GITHUB TOOL - Core GitHub API operations for LLM agents
  // ============================================================

  import { Octokit } from "https://esm.sh/@octokit/rest@20.0.2";

  const octokit = new Octokit({
    auth: Deno.env.get("GITHUB_TOKEN"),
  });

  // ----- ISSUES -----

  export interface ListIssuesArgs {
    repo: string;              // "owner/repo" format
    state?: "open" | "closed" | "all";
    labels?: string[];
    assignee?: string;
    limit?: number;
  }

  export interface Issue {
    id: string;                // "owner/repo#123"
    number: number;
    title: string;
    body: string | null;
    state: "open" | "closed";
    labels: string[];
    assignee: string | null;
    url: string;
    createdAt: string;
  }

  export interface ListIssuesResult {
    issues: Issue[];
    total: number;
  }

  export async function listIssues(args: ListIssuesArgs): Promise<ListIssuesResult> {
    const [owner, repo] = args.repo.split("/");

    const { data } = await octokit.issues.listForRepo({
      owner,
      repo,
      state: args.state || "open",
      labels: args.labels?.join(","),
      assignee: args.assignee,
      per_page: args.limit || 30,
    });

    return {
      issues: data.map(issue => ({
        id: `${args.repo}#${issue.number}`,
        number: issue.number,
        title: issue.title,
        body: issue.body,
        state: issue.state as "open" | "closed",
        labels: issue.labels.map(l => typeof l === "string" ? l : l.name || ""),
        assignee: issue.assignee?.login || null,
        url: issue.html_url,
        createdAt: issue.created_at,
      })),
      total: data.length,
    };
  }

  export interface CreateIssueArgs {
    repo: string;
    title: string;
    body?: string;
    labels?: string[];
    assignees?: string[];
  }

  export interface CreateIssueResult {
    issue: Issue;
  }

  export async function createIssue(args: CreateIssueArgs): Promise<CreateIssueResult> {
    const [owner, repo] = args.repo.split("/");

    const { data } = await octokit.issues.create({
      owner,
      repo,
      title: args.title,
      body: args.body,
      labels: args.labels,
      assignees: args.assignees,
    });

    return {
      issue: {
        id: `${args.repo}#${data.number}`,
        number: data.number,
        title: data.title,
        body: data.body,
        state: data.state as "open" | "closed",
        labels: data.labels.map(l => typeof l === "string" ? l : l.name || ""),
        assignee: data.assignee?.login || null,
        url: data.html_url,
        createdAt: data.created_at,
      },
    };
  }

  // ----- PULL REQUESTS -----

  export interface GetPRArgs {
    repo: string;
    prNumber: number;
  }

  export interface PullRequest {
    id: string;
    number: number;
    title: string;
    body: string | null;
    state: "open" | "closed" | "merged";
    author: string;
    branch: string;
    baseBranch: string;
    additions: number;
    deletions: number;
    changedFiles: number;
    mergeable: boolean | null;
    url: string;
  }

  export interface GetPRResult {
    pr: PullRequest;
  }

  export async function getPR(args: GetPRArgs): Promise<GetPRResult> {
    const [owner, repo] = args.repo.split("/");

    const { data } = await octokit.pulls.get({
      owner,
      repo,
      pull_number: args.prNumber,
    });

    return {
      pr: {
        id: `${args.repo}#${data.number}`,
        number: data.number,
        title: data.title,
        body: data.body,
        state: data.merged ? "merged" : data.state as "open" | "closed",
        author: data.user?.login || "unknown",
        branch: data.head.ref,
        baseBranch: data.base.ref,
        additions: data.additions,
        deletions: data.deletions,
        changedFiles: data.changed_files,
        mergeable: data.mergeable,
        url: data.html_url,
      },
    };
  }

  export interface GetPRDiffArgs {
    repo: string;
    prNumber: number;
  }

  export interface GetPRDiffResult {
    diff: string;
    files: Array<{
      filename: string;
      status: string;
      additions: number;
      deletions: number;
    }>;
  }

  export async function getPRDiff(args: GetPRDiffArgs): Promise<GetPRDiffResult> {
    const [owner, repo] = args.repo.split("/");

    const { data: files } = await octokit.pulls.listFiles({
      owner,
      repo,
      pull_number: args.prNumber,
    });

    // Get raw diff
    const diffResponse = await octokit.pulls.get({
      owner,
      repo,
      pull_number: args.prNumber,
      mediaType: { format: "diff" },
    });

    return {
      diff: diffResponse.data as unknown as string,
      files: files.map(f => ({
        filename: f.filename,
        status: f.status,
        additions: f.additions,
        deletions: f.deletions,
      })),
    };
  }

  // ----- CODE SEARCH -----

  export interface SearchCodeArgs {
    query: string;
    repo?: string;           // Limit to specific repo
    path?: string;           // Limit to path
    language?: string;
    limit?: number;
  }

  export interface CodeMatch {
    repo: string;
    path: string;
    url: string;
    textMatches: string[];
  }

  export interface SearchCodeResult {
    matches: CodeMatch[];
    total: number;
  }

  export async function searchCode(args: SearchCodeArgs): Promise<SearchCodeResult> {
    let q = args.query;
    if (args.repo) q += ` repo:${args.repo}`;
    if (args.path) q += ` path:${args.path}`;
    if (args.language) q += ` language:${args.language}`;

    const { data } = await octokit.search.code({
      q,
      per_page: args.limit || 20,
    });

    return {
      matches: data.items.map(item => ({
        repo: item.repository.full_name,
        path: item.path,
        url: item.html_url,
        textMatches: item.text_matches?.map(m => m.fragment || "") || [],
      })),
      total: data.total_count,
    };
  }

  ---
  linear.ts - Core Operations

  // ============================================================
  // LINEAR TOOL - Linear issue tracking for LLM agents
  // ============================================================

  const LINEAR_API = "https://api.linear.app/graphql";
  const LINEAR_TOKEN = Deno.env.get("LINEAR_API_KEY");

  async function linearQuery<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
    const response = await fetch(LINEAR_API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": LINEAR_TOKEN || "",
      },
      body: JSON.stringify({ query, variables }),
    });

    const json = await response.json();
    if (json.errors) {
      throw new Error(json.errors[0].message);
    }
    return json.data;
  }

  // ----- ISSUES -----

  export interface ListLinearIssuesArgs {
    teamKey?: string;           // e.g., "ENG"
    state?: string;             // e.g., "In Progress", "Done"
    assigneeId?: string;
    limit?: number;
  }

  export interface LinearIssue {
    id: string;
    identifier: string;         // "ENG-123"
    title: string;
    description: string | null;
    state: string;
    priority: number;
    assignee: string | null;
    url: string;
    createdAt: string;
  }

  export interface ListLinearIssuesResult {
    issues: LinearIssue[];
    total: number;
  }

  export async function listIssues(args: ListLinearIssuesArgs): Promise<ListLinearIssuesResult> {
    const data = await linearQuery<{ issues: { nodes: any[] } }>(`
      query($teamKey: String, $limit: Int) {
        issues(
          filter: { team: { key: { eq: $teamKey } } }
          first: $limit
        ) {
          nodes {
            id
            identifier
            title
            description
            state { name }
            priority
            assignee { name }
            url
            createdAt
          }
        }
      }
    `, { teamKey: args.teamKey, limit: args.limit || 50 });

    return {
      issues: data.issues.nodes.map(issue => ({
        id: issue.id,
        identifier: issue.identifier,
        title: issue.title,
        description: issue.description,
        state: issue.state?.name || "Unknown",
        priority: issue.priority,
        assignee: issue.assignee?.name || null,
        url: issue.url,
        createdAt: issue.createdAt,
      })),
      total: data.issues.nodes.length,
    };
  }

  export interface CreateLinearIssueArgs {
    teamId: string;
    title: string;
    description?: string;
    priority?: number;          // 0=none, 1=urgent, 2=high, 3=medium, 4=low
    labelIds?: string[];
  }

  export interface CreateLinearIssueResult {
    issue: LinearIssue;
  }

  export async function createIssue(args: CreateLinearIssueArgs): Promise<CreateLinearIssueResult> {
    const data = await linearQuery<{ issueCreate: { issue: any } }>(`
      mutation($input: IssueCreateInput!) {
        issueCreate(input: $input) {
          issue {
            id
            identifier
            title
            description
            state { name }
            priority
            assignee { name }
            url
            createdAt
          }
        }
      }
    `, {
      input: {
        teamId: args.teamId,
        title: args.title,
        description: args.description,
        priority: args.priority,
        labelIds: args.labelIds,
      },
    });

    const issue = data.issueCreate.issue;
    return {
      issue: {
        id: issue.id,
        identifier: issue.identifier,
        title: issue.title,
        description: issue.description,
        state: issue.state?.name || "Unknown",
        priority: issue.priority,
        assignee: issue.assignee?.name || null,
        url: issue.url,
        createdAt: issue.createdAt,
      },
    };
  }

  export interface UpdateLinearIssueArgs {
    issueId: string;
    stateId?: string;
    priority?: number;
    assigneeId?: string;
    title?: string;
    description?: string;
  }

  export interface UpdateLinearIssueResult {
    success: boolean;
    issue: LinearIssue;
  }

  export async function updateIssue(args: UpdateLinearIssueArgs): Promise<UpdateLinearIssueResult> {
    const data = await linearQuery<{ issueUpdate: { issue: any } }>(`
      mutation($id: String!, $input: IssueUpdateInput!) {
        issueUpdate(id: $id, input: $input) {
          issue {
            id
            identifier
            title
            description
            state { name }
            priority
            assignee { name }
            url
            createdAt
          }
        }
      }
    `, {
      id: args.issueId,
      input: {
        stateId: args.stateId,
        priority: args.priority,
        assigneeId: args.assigneeId,
        title: args.title,
        description: args.description,
      },
    });

    const issue = data.issueUpdate.issue;
    return {
      success: true,
      issue: {
        id: issue.id,
        identifier: issue.identifier,
        title: issue.title,
        description: issue.description,
        state: issue.state?.name || "Unknown",
        priority: issue.priority,
        assignee: issue.assignee?.name || null,
        url: issue.url,
        createdAt: issue.createdAt,
      },
    };
  }

  ---
  s3.ts - Core Operations

  // ============================================================
  // S3 TOOL - AWS S3 operations for LLM agents
  // ============================================================

  import { S3Client, ListObjectsV2Command, GetObjectCommand, PutObjectCommand, DeleteObjectCommand } from
  "https://esm.sh/@aws-sdk/client-s3@3.400.0";

  const s3 = new S3Client({
    region: Deno.env.get("AWS_REGION") || "us-east-1",
  });

  // ----- LIST -----

  export interface ListObjectsArgs {
    bucket: string;
    prefix?: string;
    limit?: number;
    continuationToken?: string;
  }

  export interface S3Object {
    key: string;
    size: number;
    lastModified: string;
    etag: string;
  }

  export interface ListObjectsResult {
    objects: S3Object[];
    total: number;
    nextToken: string | null;
    truncated: boolean;
  }

  export async function listObjects(args: ListObjectsArgs): Promise<ListObjectsResult> {
    const command = new ListObjectsV2Command({
      Bucket: args.bucket,
      Prefix: args.prefix,
      MaxKeys: args.limit || 100,
      ContinuationToken: args.continuationToken,
    });

    const response = await s3.send(command);

    return {
      objects: (response.Contents || []).map(obj => ({
        key: obj.Key || "",
        size: obj.Size || 0,
        lastModified: obj.LastModified?.toISOString() || "",
        etag: obj.ETag || "",
      })),
      total: response.KeyCount || 0,
      nextToken: response.NextContinuationToken || null,
      truncated: response.IsTruncated || false,
    };
  }

  // ----- GET -----

  export interface GetObjectArgs {
    bucket: string;
    key: string;
    asText?: boolean;       // Return as string (default: true for text files)
  }

  export interface GetObjectResult {
    content: string;
    contentType: string;
    size: number;
    lastModified: string;
  }

  export async function getObject(args: GetObjectArgs): Promise<GetObjectResult> {
    const command = new GetObjectCommand({
      Bucket: args.bucket,
      Key: args.key,
    });

    const response = await s3.send(command);
    const content = await response.Body?.transformToString() || "";

    return {
      content,
      contentType: response.ContentType || "application/octet-stream",
      size: response.ContentLength || 0,
      lastModified: response.LastModified?.toISOString() || "",
    };
  }

  // ----- PUT -----

  export interface PutObjectArgs {
    bucket: string;
    key: string;
    content: string;
    contentType?: string;
    metadata?: Record<string, string>;
  }

  export interface PutObjectResult {
    success: boolean;
    key: string;
    etag: string;
    versionId: string | null;
  }

  export async function putObject(args: PutObjectArgs): Promise<PutObjectResult> {
    const command = new PutObjectCommand({
      Bucket: args.bucket,
      Key: args.key,
      Body: args.content,
      ContentType: args.contentType || "text/plain",
      Metadata: args.metadata,
    });

    const response = await s3.send(command);

    return {
      success: true,
      key: args.key,
      etag: response.ETag || "",
      versionId: response.VersionId || null,
    };
  }

  // ----- DELETE -----

  export interface DeleteObjectArgs {
    bucket: string;
    key: string;
  }

  export interface DeleteObjectResult {
    success: boolean;
    key: string;
  }

  export async function deleteObject(args: DeleteObjectArgs): Promise<DeleteObjectResult> {
    const command = new DeleteObjectCommand({
      Bucket: args.bucket,
      Key: args.key,
    });

    await s3.send(command);

    return {
      success: true,
      key: args.key,
    };
  }

  ---

⏺ Compound Functions Architecture

  The key insight: Compound functions compose base functions to create workflows LLMs naturally want.

  workflows.ts - Cross-Tool Compositions

  // ============================================================
  // WORKFLOWS - Compound functions that compose base tools
  // ============================================================

  // Import base tools (in LLM script context, these are available via tools.*)
  // In a real implementation, import from the base modules

  // ----- GITHUB + LINEAR: Sync Issues -----

  export interface SyncGitHubToLinearArgs {
    githubRepo: string;          // "owner/repo"
    linearTeamId: string;
    labels?: string[];           // Only sync issues with these labels
    addGitHubLabel?: string;     // Label to add after syncing
  }

  export interface SyncResult {
    synced: Array<{
      githubIssue: string;       // "owner/repo#123"
      linearIssue: string;       // "ENG-456"
      title: string;
    }>;
    skipped: Array<{
      githubIssue: string;
      reason: string;
    }>;
    total: number;
  }

  export async function syncGitHubToLinear(args: SyncGitHubToLinearArgs): Promise<SyncResult> {
    // 1. List GitHub issues
    const ghIssues = await tools.github.listIssues({
      repo: args.githubRepo,
      state: "open",
      labels: args.labels,
    });

    const synced: SyncResult["synced"] = [];
    const skipped: SyncResult["skipped"] = [];

    for (const issue of ghIssues.issues) {
      // 2. Check if already synced (look for Linear link in body)
      if (issue.body?.includes("linear.app")) {
        skipped.push({ githubIssue: issue.id, reason: "Already linked to Linear" });
        continue;
      }

      // 3. Create Linear issue
      const linearResult = await tools.linear.createIssue({
        teamId: args.linearTeamId,
        title: issue.title,
        description: `From GitHub: ${issue.url}\n\n${issue.body || ""}`,
      });

      // 4. Optionally label in GitHub
      if (args.addGitHubLabel) {
        // Add label to mark as synced
      }

      synced.push({
        githubIssue: issue.id,
        linearIssue: linearResult.issue.identifier,
        title: issue.title,
      });
    }

    return { synced, skipped, total: ghIssues.total };
  }

  // ----- GITHUB + S3: Backup/Snapshot -----

  export interface BackupPRToS3Args {
    repo: string;
    prNumber: number;
    bucket: string;
    keyPrefix?: string;
  }

  export interface BackupPRResult {
    success: boolean;
    location: string;           // S3 key
    includes: {
      metadata: boolean;
      diff: boolean;
      comments: boolean;
    };
  }

  export async function backupPRToS3(args: BackupPRToS3Args): Promise<BackupPRResult> {
    // 1. Get PR metadata
    const pr = await tools.github.getPR({
      repo: args.repo,
      prNumber: args.prNumber,
    });

    // 2. Get diff
    const diff = await tools.github.getPRDiff({
      repo: args.repo,
      prNumber: args.prNumber,
    });

    // 3. Bundle everything
    const backup = {
      timestamp: new Date().toISOString(),
      pr: pr.pr,
      diff: diff.diff,
      files: diff.files,
    };

    // 4. Save to S3
    const key = `${args.keyPrefix || "pr-backups"}/${args.repo.replace("/", "-")}/${args.prNumber}.json`;

    await tools.s3.putObject({
      bucket: args.bucket,
      key,
      content: JSON.stringify(backup, null, 2),
      contentType: "application/json",
    });

    return {
      success: true,
      location: `s3://${args.bucket}/${key}`,
      includes: {
        metadata: true,
        diff: true,
        comments: false, // Could add
      },
    };
  }

  // ----- FULL CONTEXT: PR Review Helper -----

  export interface GetPRContextArgs {
    repo: string;
    prNumber: number;
  }

  export interface PRContext {
    pr: {
      title: string;
      body: string | null;
      author: string;
      branch: string;
      baseBranch: string;
      stats: { additions: number; deletions: number; files: number };
    };
    diff: {
      raw: string;
      files: Array<{ filename: string; status: string; additions: number; deletions: number }>;
    };
    linkedIssues: Array<{ number: number; title: string; state: string }>;
    relatedCode: Array<{ path: string; repo: string }>;
  }

  export interface GetPRContextResult {
    context: PRContext;
  }

  export async function getPRContext(args: GetPRContextArgs): Promise<GetPRContextResult> {
    // Parallel fetch for speed
    const [prResult, diffResult] = await Promise.all([
      tools.github.getPR({ repo: args.repo, prNumber: args.prNumber }),
      tools.github.getPRDiff({ repo: args.repo, prNumber: args.prNumber }),
    ]);

    // Extract issue references from PR body (e.g., "Fixes #123")
    const issueRefs = (prResult.pr.body || "").match(/#(\d+)/g) || [];
    const linkedIssues = [];

    for (const ref of issueRefs.slice(0, 5)) { // Limit to 5
      const issueNum = parseInt(ref.replace("#", ""));
      try {
        const issues = await tools.github.listIssues({ repo: args.repo });
        const issue = issues.issues.find(i => i.number === issueNum);
        if (issue) {
          linkedIssues.push({ number: issue.number, title: issue.title, state: issue.state });
        }
      } catch { /* ignore */ }
    }

    return {
      context: {
        pr: {
          title: prResult.pr.title,
          body: prResult.pr.body,
          author: prResult.pr.author,
          branch: prResult.pr.branch,
          baseBranch: prResult.pr.baseBranch,
          stats: {
            additions: prResult.pr.additions,
            deletions: prResult.pr.deletions,
            files: prResult.pr.changedFiles,
          },
        },
        diff: {
          raw: diffResult.diff,
          files: diffResult.files,
        },
        linkedIssues,
        relatedCode: [], // Could search for related code
      },
    };
  }

  ---

⏺ Summary: Making Tools LLM-Accessible

  Key Patterns

  | Pattern               | Why It Works                                               |
  |-----------------------|------------------------------------------------------------|
  | Consistent ID formats | owner/repo#123 → LLMs can parse and reuse IDs across calls |
  | Single args object    | No positional args confusion - everything named            |
  | Structured returns    | Objects with named fields > raw strings                    |
  | Parallel-safe         | Base functions are independent, can be called in parallel  |
  | Composable by default | Return types match input types of related functions        |

  Accessibility Principles

  1. Self-documenting names: syncGitHubToLinear not sync
  2. Predictable return shapes: Always know what you'll get back
  3. Error messages include context: "Issue ENG-123 not found" not "404"
  4. Optional parameters have sane defaults: limit defaults to reasonable values
  5. Cross-tool IDs are portable: GitHub issue ID works in Linear description

  Suggested Tool Files

  .lootbox/tools/
  ├── github.ts         # Base GitHub operations
  ├── linear.ts         # Base Linear operations
  ├── s3.ts             # Base S3 operations
  └── workflows.ts      # Compound functions that combine the above