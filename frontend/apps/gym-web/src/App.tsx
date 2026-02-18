import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Login } from './routes/auth/Login';
import { AuthGuard } from './components/layout/AuthGuard';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './routes/Dashboard';
import { MemberList } from './routes/members/MemberList';
import { MemberDetail } from './routes/members/MemberDetail';
import { Schedule } from './routes/schedule/Schedule';
import { CheckIn } from './routes/checkin/CheckIn';
import { Reports } from './routes/reports/Reports';
import { StaffManagement } from './routes/staff/StaffManagement';
import { Settings } from './routes/settings/Settings';
import { Messaging } from './routes/messaging/Messaging';
import { Payments } from './routes/payments/Payments';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Auth routes */}
          <Route path="/login" element={<Login />} />

          {/* Protected routes */}
          <Route element={<AuthGuard />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/members" element={<MemberList />} />
              <Route path="/members/:memberId" element={<MemberDetail />} />
              <Route path="/schedule" element={<Schedule />} />
              <Route path="/checkin" element={<CheckIn />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/staff" element={<StaffManagement />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/messaging" element={<Messaging />} />
              <Route path="/payments" element={<Payments />} />
            </Route>
          </Route>

          {/* Catch all - 404 */}
          <Route
            path="*"
            element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900">404</h1>
                  <p className="mt-2 text-gray-600">Page not found</p>
                </div>
              </div>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
