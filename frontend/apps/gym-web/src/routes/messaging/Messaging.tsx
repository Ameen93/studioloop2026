import { useState, type FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  notificationsSendGymMessageRoute,
  type GymMessagePublic,
} from '@sl/api-client';
import { getAuthHeaders, getStoredStaffInfo } from '../../lib/apiAuth';

type ComposeChannel = 'in_app' | 'email' | 'push' | 'whatsapp';

const channelStyles: Record<string, string> = {
  in_app: 'bg-gray-100 text-gray-800',
  email: 'bg-gold-100 text-gold-800',
  push: 'bg-purple-100 text-purple-800',
  whatsapp: 'bg-green-100 text-green-800',
};

export function Messaging() {
  const gymId = getStoredStaffInfo()?.gym_id ?? null;
  const [showCompose, setShowCompose] = useState(false);
  const [channel, setChannel] = useState<ComposeChannel>('in_app');
  const [messages, setMessages] = useState<GymMessagePublic[]>([]);
  const [sendError, setSendError] = useState<string | null>(null);

  const sendMessageMutation = useMutation({
    mutationFn: async (payload: {
      subject: string;
      body: string;
      recipient_filter: string;
      channels: Array<string>;
    }) => {
      if (!gymId) {
        throw new Error('Missing gym context');
      }
      const response = await notificationsSendGymMessageRoute({
        path: { gym_id: gymId },
        body: {
          ...payload,
          recipient_ids: [],
        },
        headers: getAuthHeaders(),
        throwOnError: true,
      });
      return response.data;
    },
    onSuccess: (data) => {
      if (data) {
        setMessages((prev) => [data, ...prev]);
      }
      setSendError(null);
      setShowCompose(false);
    },
    onError: () => {
      setSendError('Could not send message.');
    },
  });

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const subject = String(formData.get('subject') ?? '').trim();
    const body = String(formData.get('body') ?? '').trim();
    const recipientFilter = String(formData.get('recipientFilter') ?? 'all');

    if (!subject || !body) {
      setSendError('Subject and message body are required.');
      return;
    }

    sendMessageMutation.mutate({
      subject,
      body,
      recipient_filter: recipientFilter,
      channels: [channel],
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Messaging</h1>
        <button
          onClick={() => setShowCompose((v) => !v)}
          className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 transition-colors"
        >
          {showCompose ? 'Cancel' : 'Compose Message'}
        </button>
      </div>

      {!gymId && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
          Missing gym session context. Please sign in again.
        </div>
      )}

      <div className="rounded-lg border border-gold-200 bg-gold-50 p-4 text-sm text-gold-800">
        Server-side message history endpoint is not available yet. This screen shows
        messages sent in the current session.
      </div>

      {sendError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {sendError}
        </div>
      )}

      {showCompose && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">New Message</h2>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Channel</label>
              <div className="flex gap-3">
                {(['in_app', 'whatsapp', 'email', 'push'] as ComposeChannel[]).map((ch) => (
                  <button
                    key={ch}
                    type="button"
                    onClick={() => setChannel(ch)}
                    className={`px-4 py-2 text-sm font-medium rounded-md border capitalize transition-colors ${
                      channel === ch
                        ? 'bg-gold-600 text-white border-gold-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {ch === 'in_app'
                      ? 'In App'
                      : ch === 'whatsapp'
                        ? 'WhatsApp'
                        : ch === 'push'
                          ? 'Push Notification'
                          : 'Email'}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Recipients</label>
              <select
                name="recipientFilter"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm"
              >
                <option value="all">All Active Members</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
              <input
                name="subject"
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
                placeholder="Message subject"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
              <textarea
                name="body"
                rows={5}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold-500 focus:border-gold-500 sm:text-sm"
                placeholder="Type your message..."
                required
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={sendMessageMutation.isPending}
                className="px-4 py-2 bg-gold-600 text-white text-sm font-medium rounded-md hover:bg-gold-700 disabled:opacity-50"
              >
                {sendMessageMutation.isPending ? 'Sending...' : 'Send Message'}
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

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Session Message History</h2>
        </div>

        {messages.length === 0 ? (
          <div className="p-6 text-sm text-gray-500">No messages sent in this session yet.</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Subject
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Channel(s)
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Recipients
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                  Delivered
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Sent
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {messages.map((msg) => (
                <tr key={msg.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{msg.subject}</td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {msg.channels.map((ch) => (
                        <span
                          key={ch}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${channelStyles[ch] ?? 'bg-gray-100 text-gray-800'}`}
                        >
                          {ch}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 text-right">
                    {msg.total_recipients}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 text-right">
                    {msg.delivered_count}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {msg.sent_at ? new Date(msg.sent_at).toLocaleString('en-ZA') : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
