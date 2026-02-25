import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import App from './App';

describe('Gym Web App', () => {
  beforeEach(() => {
    cleanup();
    localStorage.clear();
    window.history.replaceState({}, '', '/');
  });

  it('renders login when unauthenticated', () => {
    render(<App />);
    expect(screen.getAllByText('Gym Management Portal').length).toBeGreaterThan(0);
  });

  it('renders dashboard when authenticated', () => {
    localStorage.setItem('gym_staff_access_token', 'token');
    render(<App />);
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0);
  });

  it('logs out and redirects to login from protected routes', () => {
    localStorage.setItem('gym_staff_access_token', 'token');
    localStorage.setItem('gym_staff_refresh_token', 'refresh-token');
    render(<App />);

    fireEvent.click(screen.getAllByRole('button', { name: /sign out/i })[0]);

    expect(screen.getByText('Gym Management Portal')).toBeInTheDocument();
    expect(localStorage.getItem('gym_staff_access_token')).toBeNull();
    expect(localStorage.getItem('gym_staff_refresh_token')).toBeNull();
  });
});
