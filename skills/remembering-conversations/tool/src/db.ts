import { ConversationExchange } from './types.js';
import { createRequire } from 'module';
import path from 'path';
import os from 'os';
import fs from 'fs';

type BetterSqliteDb = {
  prepare: (sql: string) => any;
  exec: (sql: string) => void;
  pragma: (sql: string) => any;
  close: () => void;
};

type BetterSqliteCtor = new (filename: string) => BetterSqliteDb;

const require = createRequire(import.meta.url);

function getBetterSqlite3Ctor(): BetterSqliteCtor {
  try {
    return require('better-sqlite3') as BetterSqliteCtor;
  } catch (error) {
    throw new Error(
      'Missing dependency: better-sqlite3. Install dependencies in skills/remembering-conversations/tool before using the indexing DB.',
      { cause: error as Error }
    );
  }
}

function getSqliteVec(): { load: (db: BetterSqliteDb) => void } {
  try {
    return require('sqlite-vec') as { load: (db: BetterSqliteDb) => void };
  } catch (error) {
    throw new Error(
      'Missing dependency: sqlite-vec. Install dependencies in skills/remembering-conversations/tool before using the indexing DB.',
      { cause: error as Error }
    );
  }
}

function getDbPath(): string {
  return process.env.TEST_DB_PATH || path.join(os.homedir(), '.clank', 'conversation-index', 'db.sqlite');
}

export function migrateSchema(db: BetterSqliteDb): void {
  const hasColumn = db.prepare(`
    SELECT COUNT(*) as count FROM pragma_table_info('exchanges')
    WHERE name='last_indexed'
  `).get() as { count: number };

  if (hasColumn.count === 0) {
    console.log('Migrating schema: adding last_indexed column...');
    db.prepare('ALTER TABLE exchanges ADD COLUMN last_indexed INTEGER').run();
    console.log('Migration complete.');
  }
}

export function initDatabase(): BetterSqliteDb {
  const dbPath = getDbPath();

  // Ensure directory exists
  const dbDir = path.dirname(dbPath);
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }

  const DatabaseCtor = getBetterSqlite3Ctor();
  const db = new DatabaseCtor(dbPath);

  // Load sqlite-vec extension
  getSqliteVec().load(db);

  // Enable WAL mode for better concurrency
  db.pragma('journal_mode = WAL');

  // Create exchanges table
  db.exec(`
    CREATE TABLE IF NOT EXISTS exchanges (
      id TEXT PRIMARY KEY,
      project TEXT NOT NULL,
      timestamp TEXT NOT NULL,
      user_message TEXT NOT NULL,
      assistant_message TEXT NOT NULL,
      archive_path TEXT NOT NULL,
      line_start INTEGER NOT NULL,
      line_end INTEGER NOT NULL,
      embedding BLOB
    )
  `);

  // Create vector search index
  db.exec(`
    CREATE VIRTUAL TABLE IF NOT EXISTS vec_exchanges USING vec0(
      id TEXT PRIMARY KEY,
      embedding FLOAT[384]
    )
  `);

  // Create index on timestamp for sorting
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_timestamp ON exchanges(timestamp DESC)
  `);

  // Run migrations
  migrateSchema(db);

  return db;
}

export function insertExchange(
  db: BetterSqliteDb,
  exchange: ConversationExchange,
  embedding: number[]
): void {
  const now = Date.now();

  const stmt = db.prepare(`
    INSERT OR REPLACE INTO exchanges
    (id, project, timestamp, user_message, assistant_message, archive_path, line_start, line_end, last_indexed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  stmt.run(
    exchange.id,
    exchange.project,
    exchange.timestamp,
    exchange.userMessage,
    exchange.assistantMessage,
    exchange.archivePath,
    exchange.lineStart,
    exchange.lineEnd,
    now
  );

  // Insert into vector table (delete first since virtual tables don't support REPLACE)
  const delStmt = db.prepare(`DELETE FROM vec_exchanges WHERE id = ?`);
  delStmt.run(exchange.id);

  const vecStmt = db.prepare(`
    INSERT INTO vec_exchanges (id, embedding)
    VALUES (?, ?)
  `);

  vecStmt.run(exchange.id, Buffer.from(new Float32Array(embedding).buffer));
}

export function getAllExchanges(db: BetterSqliteDb): Array<{ id: string; archivePath: string }> {
  const stmt = db.prepare(`SELECT id, archive_path as archivePath FROM exchanges`);
  return stmt.all() as Array<{ id: string; archivePath: string }>;
}

export function getFileLastIndexed(db: BetterSqliteDb, archivePath: string): number | null {
  const stmt = db.prepare(`
    SELECT MAX(last_indexed) as lastIndexed
    FROM exchanges
    WHERE archive_path = ?
  `);
  const row = stmt.get(archivePath) as { lastIndexed: number | null };
  return row.lastIndexed;
}

export function deleteExchange(db: BetterSqliteDb, id: string): void {
  // Delete from vector table
  db.prepare(`DELETE FROM vec_exchanges WHERE id = ?`).run(id);

  // Delete from main table
  db.prepare(`DELETE FROM exchanges WHERE id = ?`).run(id);
}
