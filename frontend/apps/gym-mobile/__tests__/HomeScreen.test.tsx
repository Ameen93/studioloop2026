import { render, screen } from '@testing-library/react-native'
import HomeScreen from '../app/index'

describe('HomeScreen', () => {
  it('renders the main title', () => {
    render(<HomeScreen />)
    expect(screen.getByText('StudioLoop Gym')).toBeTruthy()
  })

  it('renders the welcome message', () => {
    render(<HomeScreen />)
    expect(screen.getByText('Welcome to the Gym Management App')).toBeTruthy()
  })
})
