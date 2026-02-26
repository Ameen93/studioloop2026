/**
 * Main application layout with sidebar navigation.
 *
 * Provides the persistent chrome for all authenticated pages:
 * sidebar with nav links, top header bar, and main content area.
 */

import { NavLink, Outlet } from 'react-router';
import { useAuth } from '../../hooks/useAuth';

interface NavItem {
  label: string;
  path: string;
  icon: string;
}

const navItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: 'grid' },
  { label: 'Members', path: '/members', icon: 'users' },
  { label: 'Schedule', path: '/schedule', icon: 'calendar' },
  { label: 'Check-in', path: '/checkin', icon: 'check-circle' },
  { label: 'Reports', path: '/reports', icon: 'bar-chart' },
  { label: 'Staff', path: '/staff', icon: 'user-plus' },
  { label: 'Settings', path: '/settings', icon: 'settings' },
  { label: 'Messaging', path: '/messaging', icon: 'message-circle' },
  { label: 'Payments', path: '/payments', icon: 'credit-card' },
];

function NavIcon({ name }: { name: string }) {
  const icons: Record<string, string> = {
    grid: 'M4 4h6v6H4V4zm10 0h6v6h-6V4zM4 14h6v6H4v-6zm10 0h6v6h-6v-6z',
    users:
      'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zm11 10v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75',
    calendar:
      'M19 4H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V6a2 2 0 00-2-2zM16 2v4M8 2v4M3 10h18',
    'check-circle': 'M22 11.08V12a10 10 0 11-5.93-9.14M22 4L12 14.01l-3-3',
    'bar-chart': 'M12 20V10M18 20V4M6 20v-4',
    'user-plus': 'M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M8.5 11a4 4 0 100-8 4 4 0 000 8zM20 8v6M23 11h-6',
    settings:
      'M12 15a3 3 0 100-6 3 3 0 000 6zM19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z',
    'message-circle':
      'M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z',
    'credit-card':
      'M1 4h22v16H1V4zm0 6h22M5 14h4',
  };

  return (
    <svg
      className="w-5 h-5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={icons[name] || icons.grid} />
    </svg>
  );
}

export function AppLayout() {
  const { staffInfo, logout } = useAuth();

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold">StudioLoop</h1>
          <p className="text-sm text-gray-400 mt-1">Gym Management</p>
        </div>

        <nav className="flex-1 py-4">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-6 py-2.5 text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-gray-800 text-white border-r-2 border-blue-500'
                        : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                    }`
                  }
                >
                  <NavIcon name={item.icon} />
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-800">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-md transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
            </svg>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {staffInfo?.gym_name || 'Gym Dashboard'}
            </h2>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {staffInfo?.full_name || 'Staff Member'}
            </span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
              {staffInfo?.role || 'staff'}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
