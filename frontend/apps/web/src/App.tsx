import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './lib/configureApiClient';
import { Login } from './routes/auth/Login';
import { Register } from './routes/auth/Register';
import { VerifyEmail } from './routes/auth/VerifyEmail';
import { VerifyEmailSent } from './routes/auth/VerifyEmailSent';
import { Home } from './routes/Home';
import { AuthGuard } from './components/layout/AuthGuard';
import { ForgotPassword } from './routes/auth/ForgotPassword';
import { ResendVerification } from './routes/auth/ResendVerification';
import { Privacy } from './routes/Privacy';
import { Terms } from './routes/Terms';

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
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          <Route path="/auth/resend-verification" element={<ResendVerification />} />
          <Route path="/auth/verify-email" element={<VerifyEmail />} />
          <Route path="/auth/verify-email-sent" element={<VerifyEmailSent />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />

          {/* Protected route */}
          <Route
            path="/"
            element={
              <AuthGuard>
                <Home />
              </AuthGuard>
            }
          />

          {/* Catch all - 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
