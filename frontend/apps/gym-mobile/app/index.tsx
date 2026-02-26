/**
 * Index screen - redirects based on staff authentication state.
 *
 * Checks MMKV for stored tokens and redirects to either
 * the main dashboard tabs or the staff login screen.
 */

import { Redirect } from 'expo-router';
import { isAuthenticated } from '../lib/auth';

export default function IndexScreen() {
  if (isAuthenticated()) {
    return <Redirect href="/(tabs)" />;
  }

  return <Redirect href="/(auth)/login" />;
}
