/**
 * Messaging page (Story 12.10).
 *
 * Compose and send messages to members (WhatsApp, email, push).
 * View message history and delivery status.
 */

import { useState } from 'react';

type MessageChannel = 'whatsapp' | 'email' | 'push';

interface SentMessage {
  id: string;
  subject: string;
  channel: MessageChannel;
  recipients: number;
  delivered: number;
  sent_at: string;
  status: 'delivered' | 'sending' | 'failed';
}

const mockMessages: SentMessage[] = [
  { id: '1', subject: 'February Schedule Changes', channel: 'whatsapp', recipients: 342, delivered: 338, sent_at: '17 Feb 2026, 09:00', status: 'delivered' },
  { id: '2', subject: 'Valentine\'s Day Special Offer', channel: 'email', recipients: 342, delivered: 320, sent_at: '14 Feb 2026, 08:00', status: 'delivered' },
  { id: '3', subject: 'Maintenance: Gym Closed Saturday AM', channel: 'push', recipients: 342, delivered: 310, sent_at: '12 Feb 2026, 18:00', status: 'delivered' },
  { id: '4', subject: 'New Yoga Class Added', channel: 'whatsapp', recipients: 150, delivered: 0, sent_at: '18 Feb 2026, 10:00', status: 'sending' },
];

const channelStyles: Record<string, string> = {
  whatsapp: 'bg-green-100 text-green-800',
  email: 'bg-blue-100 text-blue-800',
  push: 'bg-purple-100 text-purple-800',
};

const statusStyles: Record<string, string> = {
  delivered: 'bg-green-100 text-green-800',
  sending: 'bg-yellow-100 text-yellow-800',
  failed: 'bg-red-100 text-red-800',
};

export function Messaging() {
  const [showCompose, setShowCompose] = useState(false);
  const [channel, setChannel] = useState<MessageChannel>('whatsapp');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Messaging</h1>
        <button
          onClick={() => setShowCompose(!showCompose)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          {showCompose ? 'Cancel' : 'Compose Message'}
        </button>
      </div>

      {/* Compose form */}
      {showCompose && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">New Message</h2>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
              <div className="flex gap-3">
                {(['whatsapp', 'email', 'push'] as MessageChannel[]).map((ch) => (
                  <button
                    key={ch}
                    type="button"
                    onClick={() => setChannel(ch)}
                    className={`px-4 py-2 text-sm font-medium rounded-md border capitalize transition-colors ${
                      channel === ch
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {ch === 'push' ? 'Push Notification' : ch === 'whatsapp' ? 'WhatsApp' : 'Email'}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipients</label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm">
                <option>All Active Members (342)</option>
                <option>Premium Members (197)</option>
                <option>Basic Members (120)</option>
                <option>Expiring This Week (8)</option>
                <option>Class Pack Holders (25)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Message subject"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                rows={5}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Type your message..."
              />
            </div>
            <div className="flex gap-3">
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700">
                Send Message
              </button>
              <button
                type="button"
                onClick={() => setShowCompose(false)}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Message history */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Message History</h2>
        </div>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Channel</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Recipients</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Delivered</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mockMessages.map((msg) => (
              <tr key={msg.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{msg.subject}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${channelStyles[msg.channel]}`}>
                    {msg.channel}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500 text-right">{msg.recipients}</td>
                <td className="px-6 py-4 text-sm text-gray-500 text-right">{msg.delivered}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{msg.sent_at}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusStyles[msg.status]}`}>
                    {msg.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
