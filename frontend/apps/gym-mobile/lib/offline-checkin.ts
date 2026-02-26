/**
 * Offline check-in queue using Expo SQLite.
 *
 * When the device is offline, check-ins are stored locally in SQLite.
 * When connectivity returns, queued check-ins are synced to the server.
 */

import * as SQLite from 'expo-sqlite';

const DB_NAME = 'gym_checkins.db';

interface PendingCheckin {
  id: number;
  consumerId: string;
  gymId: string;
  membershipId: string | null;
  checkinTime: string;
  method: 'qr' | 'manual';
  synced: boolean;
  createdAt: string;
}

let db: SQLite.SQLiteDatabase | null = null;

/**
 * Initialize the SQLite database and create the check-ins table.
 */
export async function initOfflineDb(): Promise<void> {
  db = await SQLite.openDatabaseAsync(DB_NAME);

  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS pending_checkins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      consumer_id TEXT NOT NULL,
      gym_id TEXT NOT NULL,
      membership_id TEXT,
      checkin_time TEXT NOT NULL,
      method TEXT NOT NULL DEFAULT 'qr',
      synced INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
  `);
}

/**
 * Queue a check-in for later sync.
 */
export async function queueCheckin(params: {
  consumerId: string;
  gymId: string;
  membershipId?: string;
  method: 'qr' | 'manual';
}): Promise<number> {
  if (!db) await initOfflineDb();

  const checkinTime = new Date().toISOString();

  const result = await db!.runAsync(
    `INSERT INTO pending_checkins (consumer_id, gym_id, membership_id, checkin_time, method)
     VALUES (?, ?, ?, ?, ?)`,
    [params.consumerId, params.gymId, params.membershipId ?? null, checkinTime, params.method],
  );

  return result.lastInsertRowId;
}

/**
 * Get all pending (unsynced) check-ins.
 */
export async function getPendingCheckins(): Promise<PendingCheckin[]> {
  if (!db) await initOfflineDb();

  const rows = await db!.getAllAsync<{
    id: number;
    consumer_id: string;
    gym_id: string;
    membership_id: string | null;
    checkin_time: string;
    method: string;
    synced: number;
    created_at: string;
  }>('SELECT * FROM pending_checkins WHERE synced = 0 ORDER BY created_at ASC');

  return rows.map((row) => ({
    id: row.id,
    consumerId: row.consumer_id,
    gymId: row.gym_id,
    membershipId: row.membership_id,
    checkinTime: row.checkin_time,
    method: row.method as 'qr' | 'manual',
    synced: row.synced === 1,
    createdAt: row.created_at,
  }));
}

/**
 * Mark a check-in as synced after successful server upload.
 */
export async function markCheckinSynced(id: number): Promise<void> {
  if (!db) await initOfflineDb();

  await db!.runAsync('UPDATE pending_checkins SET synced = 1 WHERE id = ?', [id]);
}

/**
 * Get count of pending check-ins.
 */
export async function getPendingCount(): Promise<number> {
  if (!db) await initOfflineDb();

  const result = await db!.getFirstAsync<{ count: number }>(
    'SELECT COUNT(*) as count FROM pending_checkins WHERE synced = 0',
  );

  return result?.count ?? 0;
}

/**
 * Clean up old synced check-ins (older than 7 days).
 */
export async function cleanupSyncedCheckins(): Promise<void> {
  if (!db) await initOfflineDb();

  await db!.runAsync(
    "DELETE FROM pending_checkins WHERE synced = 1 AND created_at < datetime('now', '-7 days')",
  );
}

/**
 * Sync all pending check-ins to the server.
 * Takes a callback that performs the actual API call for each check-in.
 */
export async function syncPendingCheckins(
  syncFn: (checkin: PendingCheckin) => Promise<boolean>,
): Promise<{ synced: number; failed: number }> {
  const pending = await getPendingCheckins();
  let synced = 0;
  let failed = 0;

  for (const checkin of pending) {
    try {
      const success = await syncFn(checkin);
      if (success) {
        await markCheckinSynced(checkin.id);
        synced++;
      } else {
        failed++;
      }
    } catch {
      failed++;
    }
  }

  // Clean up old synced records
  await cleanupSyncedCheckins();

  return { synced, failed };
}
