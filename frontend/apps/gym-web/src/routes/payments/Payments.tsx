/**
 * Payments dashboard page (Story 12.11).
 *
 * Shows payment list, failed payments, and marketplace payouts.
 * Tabbed view with filtering capabilities.
 */

import { useState } from 'react';

type PaymentTab = 'all' | 'failed' | 'payouts';

interface Payment {
  id: string;
  member_name: string;
  amount: string;
  method: 'ozow' | 'payfast' | 'cash';
  status: 'paid' | 'failed' | 'pending' | 'refunded';
  description: string;
  date: string;
}

interface Payout {
  id: string;
  period: string;
  gross: string;
  platform_fee: string;
  net: string;
  status: 'paid' | 'pending' | 'processing';
  date: string;
}

const mockPayments: Payment[] = [
  { id: '1', member_name: 'Thabo Mokoena', amount: 'R 599.00', method: 'ozow', status: 'paid', description: 'Premium Monthly - Feb 2026', date: '15 Feb 2026' },
  { id: '2', member_name: 'Sarah Khumalo', amount: 'R 399.00', method: 'ozow', status: 'paid', description: 'Basic Monthly - Feb 2026', date: '15 Feb 2026' },
  { id: '3', member_name: 'Naledi Phiri', amount: 'R 399.00', method: 'ozow', status: 'failed', description: 'Basic Monthly - Feb 2026', date: '15 Feb 2026' },
  { id: '4', member_name: 'John Daniels', amount: 'R 5,400.00', method: 'payfast', status: 'paid', description: 'Premium Annual Renewal', date: '14 Feb 2026' },
  { id: '5', member_name: 'Amahle Nkosi', amount: 'R 250.00', method: 'ozow', status: 'paid', description: 'Class Pack (10)', date: '13 Feb 2026' },
  { id: '6', member_name: 'David Louw', amount: 'R 599.00', method: 'ozow', status: 'failed', description: 'Premium Monthly - Feb 2026', date: '15 Feb 2026' },
  { id: '7', member_name: 'Guest Booking', amount: 'R 150.00', method: 'ozow', status: 'paid', description: 'Marketplace Drop-in - Yoga Flow', date: '17 Feb 2026' },
];

const mockPayouts: Payout[] = [
  { id: '1', period: '1-15 Feb 2026', gross: 'R 4,350.00', platform_fee: 'R 435.00', net: 'R 3,915.00', status: 'processing', date: '18 Feb 2026' },
  { id: '2', period: '16-31 Jan 2026', gross: 'R 3,800.00', platform_fee: 'R 380.00', net: 'R 3,420.00', status: 'paid', date: '03 Feb 2026' },
  { id: '3', period: '1-15 Jan 2026', gross: 'R 2,900.00', platform_fee: 'R 290.00', net: 'R 2,610.00', status: 'paid', date: '18 Jan 2026' },
];

const methodStyles: Record<string, string> = {
  ozow: 'bg-indigo-100 text-indigo-800',
  payfast: 'bg-orange-100 text-orange-800',
  cash: 'bg-gray-100 text-gray-800',
};

const statusStyles: Record<string, string> = {
  paid: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  refunded: 'bg-gray-100 text-gray-800',
  processing: 'bg-blue-100 text-blue-800',
};

export function Payments() {
  const [activeTab, setActiveTab] = useState<PaymentTab>('all');

  const failedPayments = mockPayments.filter((p) => p.status === 'failed');
  const displayPayments = activeTab === 'failed' ? failedPayments : mockPayments;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
        <button className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-50 transition-colors">
          Export
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">This Month</p>
          <p className="text-2xl font-bold text-gray-900">R 87,450.00</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Successful</p>
          <p className="text-2xl font-bold text-green-600">R 85,452.00</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Failed</p>
          <p className="text-2xl font-bold text-red-600">R 1,998.00</p>
          <p className="text-xs text-red-500">{failedPayments.length} transaction(s)</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-500">Marketplace Payouts</p>
          <p className="text-2xl font-bold text-blue-600">R 3,915.00</p>
          <p className="text-xs text-gray-500">pending</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px space-x-8">
          {[
            { key: 'all' as PaymentTab, label: 'All Payments' },
            { key: 'failed' as PaymentTab, label: `Failed (${failedPayments.length})` },
            { key: 'payouts' as PaymentTab, label: 'Marketplace Payouts' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {activeTab !== 'payouts' ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                {activeTab === 'failed' && (
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {displayPayments.map((payment) => (
                <tr key={payment.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{payment.member_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{payment.description}</td>
                  <td className="px-6 py-4 text-sm text-gray-700 text-right">{payment.amount}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${methodStyles[payment.method]}`}>
                      {payment.method}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusStyles[payment.status]}`}>
                      {payment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{payment.date}</td>
                  {activeTab === 'failed' && (
                    <td className="px-6 py-4 text-right">
                      <button className="text-sm text-blue-600 hover:text-blue-800 mr-3">Retry</button>
                      <button className="text-sm text-gray-600 hover:text-gray-800">Contact</button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gross</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Platform Fee</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Net</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockPayouts.map((payout) => (
                <tr key={payout.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{payout.period}</td>
                  <td className="px-6 py-4 text-sm text-gray-700 text-right">{payout.gross}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 text-right">{payout.platform_fee}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900 text-right">{payout.net}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${statusStyles[payout.status]}`}>
                      {payout.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{payout.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
