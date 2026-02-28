/**
 * Share class screen (Story 13.9).
 *
 * Allows consumers to share a class via link or invite friends via referral.
 */

import { useState } from 'react';
import { useParams, Link } from 'react-router';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  marketplaceGetReferralLink,
  marketplaceShareClassDetails,
  marketplaceTrackReferralSignup,
} from '@sl/api-client';
import { getAuthHeaders } from '../../lib/apiAuth';

export function ShareClass() {
  const { classId } = useParams();
  const [copied, setCopied] = useState(false);
  const [referralEmail, setReferralEmail] = useState('');
  const [referralSent, setReferralSent] = useState(false);
  const [referralError, setReferralError] = useState<string | null>(null);

  const shareClassQuery = useQuery({
    queryKey: ['share-class-details', classId],
    queryFn: async () => {
      if (!classId) {
        return null;
      }
      const response = await marketplaceShareClassDetails({
        path: { session_id: classId },
        headers: getAuthHeaders(),
      });
      return response.data;
    },
    enabled: Boolean(classId),
  });

  const referralLinkQuery = useQuery({
    queryKey: ['referral-link'],
    queryFn: async () => {
      const response = await marketplaceGetReferralLink({
        headers: getAuthHeaders(),
      });
      return response.data;
    },
  });

  const referralMutation = useMutation({
    mutationFn: async (email: string) => {
      const referralCode = referralLinkQuery.data?.referral_code;
      if (!referralCode) {
        throw new Error('Referral code unavailable');
      }
      await marketplaceTrackReferralSignup({
        headers: getAuthHeaders(),
        body: {
          referral_code: referralCode,
          email,
        },
      });
    },
    onSuccess: () => {
      setReferralError(null);
      setReferralSent(true);
      setReferralEmail('');
      setTimeout(() => setReferralSent(false), 3000);
    },
    onError: () => {
      setReferralError('Could not send invite right now. Please try again.');
    },
  });

  const shareUrl =
    shareClassQuery.data?.share_link ?? `${window.location.origin}/discover/${classId}`;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShareNative = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Check out this class on StudioLoop',
          text: 'I found a great class on StudioLoop. Join me!',
          url: shareUrl,
        });
      } catch {
        // User cancelled or share failed
      }
    }
  };

  const handleSendReferral = async () => {
    if (!referralEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(referralEmail)) {
      return;
    }
    referralMutation.mutate(referralEmail);
  };

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <Link
        to={`/discover/${classId}`}
        className="inline-flex items-center text-sm text-coral-600 hover:text-coral-500 font-medium mb-6"
      >
        &larr; Back to class
      </Link>

      <h1 className="text-2xl font-bold text-gray-900 mb-2">Share this class</h1>
      <p className="text-gray-600 mb-8">Invite friends to join you at this class.</p>

      {shareClassQuery.error && (
        <p className="mb-4 text-sm text-red-600">
          Could not load canonical share details. Using fallback link.
        </p>
      )}

      {/* Share link section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Share link</h2>
        <div className="flex items-center gap-2">
          <input
            type="text"
            readOnly
            value={shareUrl}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-600 bg-gray-50"
          />
          <button
            onClick={handleCopyLink}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              copied
                ? 'bg-green-100 text-green-700'
                : 'bg-coral-600 text-white hover:bg-coral-700'
            }`}
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>

        {typeof navigator.share === 'function' && (
          <button
            onClick={handleShareNative}
            className="mt-3 w-full py-2 px-4 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            Share via...
          </button>
        )}
      </div>

      {/* Referral invite */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-1">Invite a friend</h2>
        <p className="text-xs text-gray-500 mb-3">
          Send an invite email to a friend. Earn rewards when they sign up and book their first class!
        </p>

        <div className="flex items-center gap-2">
          <input
            type="email"
            value={referralEmail}
            onChange={(e) => setReferralEmail(e.target.value)}
            placeholder="friend@example.com"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500"
          />
          <button
            onClick={handleSendReferral}
            disabled={referralMutation.isPending}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-coral-600 text-white hover:bg-coral-700 transition-colors disabled:opacity-50"
          >
            {referralMutation.isPending ? 'Sending...' : 'Send'}
          </button>
        </div>

        {referralSent && (
          <p className="mt-2 text-sm text-green-600">Invite sent successfully!</p>
        )}
        {referralError && <p className="mt-2 text-sm text-red-600">{referralError}</p>}
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Share on social media</h2>
        <div className="flex items-center gap-3">
          <a
            href={`https://wa.me/?text=${encodeURIComponent(`Check out this class on StudioLoop: ${shareUrl}`)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-medium hover:bg-green-700 transition-colors"
          >
            WhatsApp
          </a>
          <a
            href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(`Check out this class on StudioLoop!`)}&url=${encodeURIComponent(shareUrl)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 text-white text-sm font-medium hover:bg-gray-900 transition-colors"
          >
            X / Twitter
          </a>
          <a
            href={`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Facebook
          </a>
        </div>
      </div>
    </div>
  );
}

export default ShareClass;
