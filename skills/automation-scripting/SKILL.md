---
name: automation-scripting
short_description: >-
  Expert guidance for task automation, cron jobs, workflow automation, ETL
  pipelines, file watchers, and scripting best practices.
description: >
  Expert guidance for task automation, cron jobs, workflow automation, and
  scripting.


  Use when: building automated workflows, creating scheduled tasks, implementing
  file watchers,

  creating ETL pipelines, automating deployments, building API integrations,
  implementing

  batch processing jobs, or setting up event-driven automation.


  Keywords: automation, cron jobs, task scheduler, workflow automation, ETL
  pipeline,

  file watcher, batch processing, scheduled tasks, node-cron, chokidar, data
  processing,

  deployment automation, API integration, event-driven, idempotent scripts
when_to_use: >
  Use when building automated workflows, creating scheduled tasks or cron jobs,
  implementing file watchers, creating ETL pipelines,

  automating deployments, building API integrations, implementing batch
  processing jobs, or setting up event-driven automation.
version: 1.0.0
category: automation-and-scripting
---

# Automation & Scripting Skill

You are an automation expert with deep knowledge of task automation, cron jobs, workflow automation, and scripting best practices.

## Core Capabilities

### Workflow Automation
- Create automated workflows and pipelines
- Build scheduled tasks and cron jobs
- Implement file watching and event-driven automation
- Create data processing pipelines
- Build ETL (Extract, Transform, Load) processes

### Integration & Deployment
- Automate deployment and testing
- Implement email and notification automation
- Create web scraping and data collection scripts
- Build API integration and data synchronization
- Implement batch processing jobs

## Best Practices

### Script Design
- **Idempotency**: Make scripts safe to run multiple times
- **Error Handling**: Implement proper error handling and retries
- **Logging**: Log all automation activities with timestamps
- **Configuration**: Use configuration files for flexibility
- **Monitoring**: Implement health checks and monitoring

### Production Readiness
- Handle edge cases and failures gracefully
- Document automation workflows clearly
- Use environment variables for secrets
- Implement rate limiting for external APIs
- Test automation scripts thoroughly before deployment

## Code Patterns

### Task Scheduler with Node-Cron

```typescript
import cron from 'node-cron';
import { sendReport } from './email';
import { backupDatabase } from './backup';
import { cleanupOldFiles } from './cleanup';

// Run daily report at 8 AM
cron.schedule('0 8 * * *', async () => {
  console.log('Running daily report...');
  try {
    await sendReport();
    console.log('Daily report sent successfully');
  } catch (error) {
    console.error('Failed to send daily report:', error);
    // Implement retry logic or alerting here
  }
});

// Backup database every 6 hours
cron.schedule('0 */6 * * *', async () => {
  console.log('Starting database backup...');
  try {
    await backupDatabase();
    console.log('Database backup completed');
  } catch (error) {
    console.error('Database backup failed:', error);
    // Alert on backup failures
  }
});

// Cleanup old files weekly (Sunday at midnight)
cron.schedule('0 0 * * 0', async () => {
  console.log('Cleaning up old files...');
  try {
    const deleted = await cleanupOldFiles();
    console.log(`Cleaned up ${deleted} files`);
  } catch (error) {
    console.error('Cleanup failed:', error);
  }
});
```

**Cron Expression Reference:**
- `* * * * *` - Every minute
- `0 * * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `0 8 * * 1` - Every Monday at 8 AM
- `*/15 * * * *` - Every 15 minutes

### File Watcher Automation

```typescript
import chokidar from 'chokidar';
import { processFile } from './processor';

// Watch for new files in uploads directory
const watcher = chokidar.watch('uploads/**/*', {
  ignored: /(^|[\/\\])\../, // Ignore dotfiles
  persistent: true,
  ignoreInitial: true, // Don't process existing files on startup
});

watcher
  .on('add', async (path) => {
    console.log(`File ${path} has been added`);
    try {
      await processFile(path);
      console.log(`Successfully processed ${path}`);
    } catch (error) {
      console.error(`Failed to process ${path}:`, error);
      // Move to error directory or retry queue
    }
  })
  .on('change', (path) => {
    console.log(`File ${path} has been changed`);
    // Handle file modifications
  })
  .on('unlink', (path) => {
    console.log(`File ${path} has been removed`);
    // Clean up related resources
  })
  .on('error', (error) => {
    console.error('Watcher error:', error);
  });

// Graceful shutdown
process.on('SIGINT', async () => {
  await watcher.close();
  process.exit(0);
});
```

**File Watcher Use Cases:**
- Process uploaded files automatically
- Trigger builds on code changes
- Sync files between directories
- Monitor log files for errors
- Auto-process data files

### ETL Pipeline

```typescript
export class ETLPipeline {
  private readonly maxRetries = 3;

  async run() {
    console.log('Starting ETL pipeline...');
    const startTime = Date.now();

    try {
      // Extract
      const rawData = await this.extract();
      console.log(`Extracted ${Object.keys(rawData).length} datasets`);

      // Transform
      const transformedData = await this.transform(rawData);
      console.log(`Transformed data for loading`);

      // Load
      await this.load(transformedData);

      const duration = Date.now() - startTime;
      console.log(`ETL pipeline completed successfully in ${duration}ms`);

      return { success: true, duration };
    } catch (error) {
      console.error('ETL pipeline failed:', error);
      // Implement rollback logic if needed
      throw error;
    }
  }

  private async extract() {
    // Fetch data from multiple sources with retry logic
    const [users, orders, products] = await Promise.all([
      this.fetchWithRetry(() => this.fetchUsers()),
      this.fetchWithRetry(() => this.fetchOrders()),
      this.fetchWithRetry(() => this.fetchProducts()),
    ]);

    return { users, orders, products };
  }

  private async transform(data: any) {
    // Clean and transform data
    const users = data.users.map(u => ({
      id: u.id,
      email: u.email.toLowerCase().trim(),
      name: u.name.trim(),
      country: u.country || 'Unknown',
      createdAt: new Date(u.created_at),
    }));

    const orders = data.orders
      .filter(o => o.status === 'completed')
      .map(o => ({
        id: o.id,
        userId: o.user_id,
        total: parseFloat(o.total),
        items: o.items.length,
        date: new Date(o.created_at),
      }));

    // Validate transformed data
    this.validateData(users, orders);

    return { users, orders };
  }

  private async load(data: any) {
    // Load into data warehouse with transaction support
    try {
      await Promise.all([
        this.loadUsers(data.users),
        this.loadOrders(data.orders),
      ]);
    } catch (error) {
      // Rollback on failure
      await this.rollback();
      throw error;
    }
  }

  private async fetchWithRetry<T>(fn: () => Promise<T>): Promise<T> {
    for (let i = 0; i < this.maxRetries; i++) {
      try {
        return await fn();
      } catch (error) {
        if (i === this.maxRetries - 1) throw error;
        await this.delay(1000 * (i + 1)); // Exponential backoff
      }
    }
    throw new Error('Max retries exceeded');
  }

  private validateData(users: any[], orders: any[]) {
    if (!users.length) throw new Error('No users to load');
    if (!orders.length) throw new Error('No orders to load');
    // Add more validation as needed
  }

  private delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

**ETL Best Practices:**
- Use transactions for data consistency
- Implement retry logic with exponential backoff
- Validate data at each stage
- Log progress and errors
- Support incremental loads
- Handle schema changes gracefully

### Batch Processing with Queue

```typescript
import Queue from 'bull';
import { processDocument } from './processor';

const documentQueue = new Queue('documents', {
  redis: {
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379'),
  },
});

// Process jobs with concurrency
documentQueue.process(5, async (job) => {
  const { documentId, userId } = job.data;

  console.log(`Processing document ${documentId}`);

  try {
    // Update progress
    await job.progress(25);

    const result = await processDocument(documentId);

    await job.progress(100);

    return result;
  } catch (error) {
    console.error(`Failed to process document ${documentId}:`, error);
    throw error; // Job will be retried
  }
});

// Add jobs to queue
export async function queueDocument(documentId: string, userId: string) {
  await documentQueue.add(
    { documentId, userId },
    {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000,
      },
      removeOnComplete: true,
    }
  );
}

// Monitor queue health
documentQueue.on('completed', (job) => {
  console.log(`Job ${job.id} completed`);
});

documentQueue.on('failed', (job, error) => {
  console.error(`Job ${job.id} failed:`, error);
});
```

## Automation Workflow Checklist

When implementing automation:

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

## Common Pitfalls to Avoid

1. **Non-Idempotent Scripts**: Running twice causes problems
2. **Missing Error Handling**: Silent failures that go unnoticed
3. **No Logging**: Can't debug when things go wrong
4. **Hard-Coded Values**: Makes scripts inflexible
5. **No Rate Limiting**: Overwhelms external APIs
6. **Ignoring Failures**: Not implementing proper retry logic
7. **Missing Monitoring**: Can't detect when automation breaks
8. **No Testing**: Untested automation fails in production
9. **Poor Documentation**: Team can't maintain the automation
10. **No Cleanup**: Temporary files and resources accumulate

## Resources

### Libraries
- [Node-Cron](https://github.com/node-cron/node-cron) - Task scheduler for Node.js
- [Chokidar](https://github.com/paulmillr/chokidar) - Efficient file watcher
- [Bull Queue](https://github.com/OptimalBits/bull) - Redis-based queue for Node.js
- [Agenda](https://github.com/agenda/agenda) - Job scheduling for Node.js
- [BullMQ](https://github.com/taskforcesh/bullmq) - Modern queue system

### Cron Expression Tools
- [Crontab Guru](https://crontab.guru/) - Cron expression editor
- [Cron Expression Generator](https://www.freeformatter.com/cron-expression-generator-quartz.html)

### Documentation
- [Node.js Cluster Module](https://nodejs.org/api/cluster.html) - For parallel processing
- [PM2 Process Manager](https://pm2.keymetrics.io/) - Production process manager
