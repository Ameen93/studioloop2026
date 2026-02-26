import { render } from '@testing-library/react-native'

jest.mock('react-native-mmkv', () => ({
  createMMKV: () => ({
    getString: jest.fn(),
    set: jest.fn(),
    remove: jest.fn(),
    getBoolean: jest.fn(),
    getNumber: jest.fn(),
  }),
}))

const mockRedirect = jest.fn((_props: { href: string }) => null)

jest.mock('expo-router', () => ({
  Redirect: (props: { href: string }) => mockRedirect(props),
}))

const mockIsAuthenticated = jest.fn()

jest.mock('../lib/auth', () => ({
  isAuthenticated: () => mockIsAuthenticated(),
}))

import HomeScreen from '../app/index'

describe('HomeScreen', () => {
  beforeEach(() => {
    mockRedirect.mockClear()
    mockIsAuthenticated.mockReset()
  })

  it('redirects unauthenticated staff to login', () => {
    mockIsAuthenticated.mockReturnValue(false)

    render(<HomeScreen />)

    expect(mockRedirect).toHaveBeenCalledWith({ href: '/(auth)/login' })
  })

  it('redirects authenticated staff to tabs', () => {
    mockIsAuthenticated.mockReturnValue(true)

    render(<HomeScreen />)

    expect(mockRedirect).toHaveBeenCalledWith({ href: '/(tabs)' })
  })
})
