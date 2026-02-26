import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import App from './App';

describe('Consumer Web App', () => {
  beforeEach(() => {
    cleanup();
    localStorage.clear();
    window.history.replaceState({}, '', '/');
  });

  it('renders login when unauthenticated', () => {
    render(<App />);
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
  });

  it('renders protected home when authenticated', () => {
    localStorage.setItem('consumer_access_token', 'token');
    render(<App />);
    expect(screen.getByText('My Activity')).toBeInTheDocument();
  });

  it('logs out and redirects to login from protected routes', () => {
    localStorage.setItem('consumer_access_token', 'token');
    localStorage.setItem('consumer_refresh_token', 'refresh-token');
    render(<App />);

    fireEvent.click(screen.getAllByRole('button', { name: /sign out/i })[0]);

    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
    expect(localStorage.getItem('consumer_access_token')).toBeNull();
    expect(localStorage.getItem('consumer_refresh_token')).toBeNull();
  });
});
