import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './lib/configureApiClient';
import { Login } from './routes/auth/Login';
import { ForgotPassword } from './routes/auth/ForgotPassword';
import { ResetPassword } from './routes/auth/ResetPassword';
import { ResendVerification } from './routes/auth/ResendVerification';
import { VerifyEmail } from './routes/auth/VerifyEmail';
import { VerifyEmailSent } from './routes/auth/VerifyEmailSent';
import { AuthGuard } from './components/layout/AuthGuard';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './routes/Dashboard';
import { GymList } from './routes/gyms/GymList';
import { GymDetail } from './routes/gyms/GymDetail';
import { ComplaintList } from './routes/complaints/ComplaintList';
import { AuditLogs } from './routes/audit-logs/AuditLogs';
import { Privacy } from './routes/Privacy';
import { Terms } from './routes/Terms';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Auth routes — kept for backend email links (reset-password, verify-email) */}
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          <Route path="/auth/resend-verification" element={<ResendVerification />} />
          <Route path="/auth/verify-email" element={<VerifyEmail />} />
          <Route path="/auth/verify-email-sent" element={<VerifyEmailSent />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />

          {/* Admin routes — superuser only */}
          <Route element={<AuthGuard />}>
            <Route element={<AppLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="gyms" element={<GymList />} />
              <Route path="gyms/:gymId" element={<GymDetail />} />
              <Route path="complaints" element={<ComplaintList />} />
              <Route path="audit-logs" element={<AuditLogs />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
