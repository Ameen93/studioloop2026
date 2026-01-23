/**
 * Index screen - redirects to appropriate initial screen.
 *
 * For now, redirects to registration. In the future, this
 * will check auth state and redirect accordingly.
 */

import { Redirect } from 'expo-router';

export default function IndexScreen() {
  // TODO: Check if user is authenticated and redirect to main app
  // For now, redirect to login
  return <Redirect href="/(auth)/login" />;
}
