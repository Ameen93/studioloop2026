/**
 * QR code data cache using MMKV for offline access.
 *
 * Caches the consumer's QR code data so it can be displayed
 * even without network connectivity (offline-first).
 */

import { createMMKV } from 'react-native-mmkv';

const QR_STORAGE_ID = 'consumer-qr-storage';
const storage = createMMKV({ id: QR_STORAGE_ID });

const KEYS = {
  QR_DATA: 'qr_data',
  QR_CONSUMER_ID: 'qr_consumer_id',
  QR_UPDATED_AT: 'qr_updated_at',
  QR_MEMBERSHIP_ID: 'qr_membership_id',
} as const;

export interface QrCodeData {
  /** The consumer ID to encode in the QR code */
  consumerId: string;
  /** Active membership ID (if any) */
  membershipId?: string;
  /** Timestamp when the QR data was last updated */
  updatedAt: string;
}

/**
 * Cache QR code data in MMKV for offline display.
 */
export function cacheQrData(data: QrCodeData): void {
  // Store a JSON payload as the QR value
  const qrPayload = JSON.stringify({
    type: 'studioloop_checkin',
    consumer_id: data.consumerId,
    membership_id: data.membershipId,
    ts: data.updatedAt,
  });

  storage.set(KEYS.QR_DATA, qrPayload);
  storage.set(KEYS.QR_CONSUMER_ID, data.consumerId);
  storage.set(KEYS.QR_UPDATED_AT, data.updatedAt);
  if (data.membershipId) {
    storage.set(KEYS.QR_MEMBERSHIP_ID, data.membershipId);
  }
}

/**
 * Get cached QR code data from MMKV.
 * Returns null if no QR data is cached.
 */
export function getCachedQrData(): string | null {
  return storage.getString(KEYS.QR_DATA) ?? null;
}

/**
 * Get metadata about the cached QR code.
 */
export function getCachedQrMeta(): QrCodeData | null {
  const consumerId = storage.getString(KEYS.QR_CONSUMER_ID);
  const updatedAt = storage.getString(KEYS.QR_UPDATED_AT);

  if (!consumerId || !updatedAt) return null;

  return {
    consumerId,
    membershipId: storage.getString(KEYS.QR_MEMBERSHIP_ID),
    updatedAt,
  };
}

/**
 * Clear cached QR data (e.g., on logout).
 */
export function clearQrCache(): void {
  storage.delete(KEYS.QR_DATA);
  storage.delete(KEYS.QR_CONSUMER_ID);
  storage.delete(KEYS.QR_UPDATED_AT);
  storage.delete(KEYS.QR_MEMBERSHIP_ID);
}
