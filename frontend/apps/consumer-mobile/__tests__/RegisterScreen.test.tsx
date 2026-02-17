import { render, screen } from '@testing-library/react-native'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock expo-router
jest.mock('expo-router', () => ({
  router: {
    push: jest.fn(),
    replace: jest.fn(),
  },
}))

// Mock api-client
jest.mock('@sl/api-client', () => ({
  consumerAuthRegisterConsumer: jest.fn(),
}))

import RegisterScreen from '../app/(auth)/register'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
)

describe('RegisterScreen', () => {
  beforeEach(() => {
    queryClient.clear()
  })

  it('renders the main title', () => {
    render(<RegisterScreen />, { wrapper })
    expect(screen.getByText('Create your account')).toBeTruthy()
  })

  it('renders all form fields', () => {
    render(<RegisterScreen />, { wrapper })
    expect(screen.getByText('First name')).toBeTruthy()
    expect(screen.getByText('Last name')).toBeTruthy()
    expect(screen.getByText('Email address')).toBeTruthy()
    expect(screen.getByText('Password')).toBeTruthy()
    expect(screen.getByText('Confirm password')).toBeTruthy()
  })

  it('renders the submit button', () => {
    render(<RegisterScreen />, { wrapper })
    expect(screen.getByText('Create account')).toBeTruthy()
  })
})
