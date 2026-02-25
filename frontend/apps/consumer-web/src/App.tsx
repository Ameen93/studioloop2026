import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './lib/configureApiClient';
import { Login } from './routes/auth/Login';
import { Register } from './routes/auth/Register';
import { ForgotPassword } from './routes/auth/ForgotPassword';
import { Home } from './routes/Home';
import { QRCode } from './routes/QRCode';
import { Discover } from './routes/discover/Discover';
import { ClassDetail } from './routes/discover/ClassDetail';
import { ShareClass } from './routes/discover/ShareClass';
import { Bookings } from './routes/bookings/Bookings';
import { Memberships } from './routes/memberships/Memberships';
import { Profile } from './routes/profile/Profile';
import { AppLayout } from './components/layout/AppLayout';
import { AuthGuard } from './components/layout/AuthGuard';

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
          {/* Public auth routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Protected routes with app shell layout */}
          <Route
            element={
              <AuthGuard>
                <AppLayout />
              </AuthGuard>
            }
          >
            <Route path="/" element={<Home />} />
            <Route path="/discover" element={<Discover />} />
            <Route path="/discover/:classId" element={<ClassDetail />} />
            <Route path="/discover/:classId/share" element={<ShareClass />} />
            <Route path="/bookings" element={<Bookings />} />
            <Route path="/memberships" element={<Memberships />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/qr-code" element={<QRCode />} />
          </Route>

          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
