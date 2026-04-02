import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

// Mock the loginTestToken API call used by AuthGuard
vi.mock('@sl/api-client', async () => {
  const actual = await vi.importActual('@sl/api-client');
  return {
    ...actual,
    loginTestToken: vi.fn().mockResolvedValue({
      data: { id: '1', email: 'admin@test.com', is_superuser: true, is_active: true },
    }),
  };
});

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    window.history.replaceState({}, '', '/')
  })

  it('redirects unauthenticated users to the login page', () => {
    render(<App />)
    expect(screen.getByText('StudioLoop Admin')).toBeInTheDocument()
  })

  it('renders the login form fields', () => {
    render(<App />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('renders forgot password route', () => {
    window.history.replaceState({}, '', '/auth/forgot-password')
    render(<App />)
    expect(screen.getByText('Reset your password')).toBeInTheDocument()
  })

  it('renders set-password form when token is provided', () => {
    window.history.replaceState({}, '', '/reset-password?token=abc123')
    render(<App />)
    expect(screen.getByText('Set your password')).toBeInTheDocument()
    expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
  })

  it('renders invalid-link message when token is missing', () => {
    window.history.replaceState({}, '', '/reset-password')
    render(<App />)
    expect(screen.getByText('Invalid link')).toBeInTheDocument()
  })

  it('renders resend verification route', () => {
    window.history.replaceState({}, '', '/auth/resend-verification')
    render(<App />)
    expect(screen.getByText('Resend verification email')).toBeInTheDocument()
  })
})
