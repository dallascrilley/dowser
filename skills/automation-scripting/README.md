# Automation & Scripting Skill

Expert guidance for task automation, cron jobs, workflow automation, and scripting.

## Overview

This skill provides comprehensive knowledge and code patterns for building automated workflows, scheduled tasks, file watchers, ETL pipelines, and batch processing jobs using Node.js and TypeScript.

## What This Skill Covers

### Core Capabilities
- **Workflow Automation**: Build automated workflows and pipelines
- **Task Scheduling**: Create cron jobs and scheduled tasks
- **Event-Driven Automation**: Implement file watchers and event handlers
- **Data Processing**: Build ETL pipelines and batch processing jobs
- **Integration**: Automate deployments, API integrations, and notifications

### Key Technologies
- **Node-Cron**: Task scheduling with cron expressions
- **Chokidar**: Efficient file watching
- **Bull Queue**: Redis-based job queue for batch processing
- **TypeScript**: Type-safe automation scripts

## When to Use This Skill

Use this skill when you need help with:

- Building automated workflows
- Creating scheduled tasks (cron jobs)
- Implementing file watchers
- Creating ETL (Extract, Transform, Load) pipelines
- Automating deployments and testing
- Building API integrations and data synchronization
- Implementing batch processing jobs
- Setting up event-driven automation

**Keywords**: automation, cron jobs, task scheduler, workflow automation, ETL pipeline, file watcher, batch processing, scheduled tasks, node-cron, chokidar, data processing, deployment automation, API integration, event-driven, idempotent scripts

## Installation

### Option 1: Personal Installation (All Projects)

Install to your personal Claude Code skills directory:

```bash
# Copy the skill folder
cp -r generated-skills/automation-scripting ~/.claude/skills/

# Or extract from ZIP
unzip automation-scripting.zip -d ~/.claude/skills/
```

### Option 2: Project Installation (Single Project)

Install to a specific project's skills directory:

```bash
# Copy the skill folder
cp -r generated-skills/automation-scripting /path/to/your/project/.claude/skills/

# Or extract from ZIP
unzip automation-scripting.zip -d /path/to/your/project/.claude/skills/
```

### Verify Installation

After installation, restart Claude Code or reload skills. The skill will be automatically loaded when you work on automation-related tasks.

## Usage Examples

### Example 1: Create a Daily Report Cron Job

**Prompt**: "I need to send a daily report every morning at 8 AM"

Claude will provide:
- Node-cron implementation
- Error handling and retry logic
- Logging best practices
- Email/notification integration

### Example 2: File Watcher for Upload Processing

**Prompt**: "Watch the uploads directory and process new files automatically"

Claude will provide:
- Chokidar file watcher setup
- Event handlers (add, change, unlink)
- File processing pipeline
- Error handling and retry queue

### Example 3: ETL Pipeline for Data Warehouse

**Prompt**: "Build an ETL pipeline to extract data from APIs, transform it, and load into our data warehouse"

Claude will provide:
- ETL class structure
- Extract logic with retry
- Transform/validation logic
- Load with transaction support
- Error handling and rollback

### Example 4: Batch Job Queue

**Prompt**: "Process documents in batches with retry logic and progress tracking"

Claude will provide:
- Bull Queue setup with Redis
- Job processor with concurrency
- Progress tracking
- Retry with exponential backoff
- Queue health monitoring

## Code Patterns Included

### 1. Task Scheduler with Node-Cron
- Daily, hourly, and weekly schedules
- Error handling and retry logic
- Cron expression reference

### 2. File Watcher Automation
- Watch for file changes
- Process files automatically
- Handle errors gracefully
- Graceful shutdown

### 3. ETL Pipeline
- Extract from multiple sources
- Transform and validate data
- Load with transaction support
- Retry logic with exponential backoff

### 4. Batch Processing with Queue
- Redis-based job queue
- Concurrent processing
- Progress tracking
- Retry with backoff
- Queue monitoring

## Best Practices Enforced

- **Idempotency**: Scripts safe to run multiple times
- **Error Handling**: Comprehensive error handling and retries
- **Logging**: All automation activities logged
- **Configuration**: Environment variables for flexibility
- **Monitoring**: Health checks and alerting
- **Testing**: Thorough testing before deployment
- **Documentation**: Clear workflow documentation
- **Security**: Environment variables for secrets
- **Rate Limiting**: Protection for external APIs

## Requirements

### Node.js Dependencies

```bash
npm install node-cron chokidar bull
```

Or with TypeScript types:

```bash
npm install --save-dev @types/node-cron @types/bull
```

### Optional Dependencies

- **Redis**: Required for Bull Queue (batch processing)
- **PM2**: Recommended for production deployment

## Automation Workflow Checklist

When implementing automation, this skill ensures you:

- [ ] Define clear success/failure criteria
- [ ] Implement comprehensive error handling
- [ ] Add logging for all significant events
- [ ] Set up monitoring and alerting
- [ ] Test with edge cases and failures
- [ ] Document the automation workflow
- [ ] Implement graceful shutdown
- [ ] Add health check endpoints
- [ ] Use environment variables for configuration
- [ ] Implement rate limiting for external APIs
- [ ] Add retry logic with exponential backoff
- [ ] Validate inputs and outputs
- [ ] Make scripts idempotent
- [ ] Set up proper permissions and security
- [ ] Plan for rollback scenarios

## Common Pitfalls Avoided

This skill helps you avoid:

1. **Non-Idempotent Scripts**: Running twice causes problems
2. **Missing Error Handling**: Silent failures
3. **No Logging**: Can't debug issues
4. **Hard-Coded Values**: Inflexible scripts
5. **No Rate Limiting**: Overwhelming external APIs
6. **Ignoring Failures**: Not implementing retry logic
7. **Missing Monitoring**: Can't detect breakages
8. **No Testing**: Failures in production
9. **Poor Documentation**: Hard to maintain
10. **No Cleanup**: Resource accumulation

## Resources

### Libraries
- [Node-Cron](https://github.com/node-cron/node-cron) - Task scheduler for Node.js
- [Chokidar](https://github.com/paulmillr/chokidar) - Efficient file watcher
- [Bull Queue](https://github.com/OptimalBits/bull) - Redis-based queue
- [Agenda](https://github.com/agenda/agenda) - Job scheduling
- [BullMQ](https://github.com/taskforcesh/bullmq) - Modern queue system

### Tools
- [Crontab Guru](https://crontab.guru/) - Cron expression editor
- [Cron Expression Generator](https://www.freeformatter.com/cron-expression-generator-quartz.html)
- [PM2](https://pm2.keymetrics.io/) - Production process manager

### Documentation
- [Node.js Cluster Module](https://nodejs.org/api/cluster.html) - For parallel processing

## Support

For questions, issues, or contributions:
- Refer to the main repository documentation
- Open a GitHub issue
- Check the Skills Factory documentation

## Version

**Version**: 1.0.0
**Created**: 2025-11-10
**Skill Type**: Knowledge domain
**Language**: TypeScript/JavaScript
