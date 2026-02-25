import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  beforeEach(() => {
    localStorage.clear()
    window.history.replaceState({}, '', '/')
  })

  it('redirects authenticated users to the protected home route', () => {
    localStorage.setItem('access_token', 'token')
    render(<App />)
    expect(screen.getByText('You are signed in')).toBeInTheDocument()
  })

  it('renders the login page by default', () => {
    render(<App />)
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument()
  })

  it('renders the login form fields', () => {
    render(<App />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('supports logout from the protected home route', () => {
    localStorage.setItem('access_token', 'token')
    render(<App />)
    fireEvent.click(screen.getByRole('button', { name: /sign out/i }))
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument()
  })

  it('renders forgot password route', () => {
    window.history.replaceState({}, '', '/auth/forgot-password')
    render(<App />)
    expect(screen.getByText('Reset your password')).toBeInTheDocument()
  })

  it('renders resend verification route', () => {
    window.history.replaceState({}, '', '/auth/resend-verification')
    render(<App />)
    expect(screen.getByText('Resend verification email')).toBeInTheDocument()
  })
})
