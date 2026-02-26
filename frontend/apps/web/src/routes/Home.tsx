import { useNavigate } from 'react-router';

export function Home() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/auth/login', { replace: true });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm p-8 text-center space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">You are signed in</h1>
        <p className="text-sm text-gray-600">
          Local auth tokens were stored successfully.
        </p>
        <button
          type="button"
          onClick={handleLogout}
          className="inline-flex justify-center rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
