/**
 * StudioLoop Brand Colors
 * Design tokens for consistent color usage across all platforms
 *
 * Coral: consumer-facing accent
 * Gold: gym-facing accent
 * Gray: neutral scale (shared)
 */
export const colors = {
  coral: {
    50: '#fff5f2',
    100: '#ffe8e1',
    200: '#ffc9b8',
    300: '#ffa48a',
    400: '#ff8767',
    500: '#FF6B4A', // Consumer brand accent
    600: '#e55535',
    700: '#c44025',
    800: '#a3301a',
    900: '#7a2414',
  },
  gold: {
    50: '#fdf8eb',
    100: '#f9edd0',
    200: '#f1d99e',
    300: '#e8c36c',
    400: '#dead47',
    500: '#d4a855', // Gym brand accent
    600: '#b88d3a',
    700: '#96702d',
    800: '#755724',
    900: '#5a431c',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  success: {
    light: '#86efac',
    DEFAULT: '#22c55e',
    dark: '#16a34a',
  },
  warning: {
    light: '#fcd34d',
    DEFAULT: '#f59e0b',
    dark: '#d97706',
  },
  error: {
    light: '#fca5a5',
    DEFAULT: '#ef4444',
    dark: '#dc2626',
  },
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
} as const;

/** Surface tokens for light theme */
export const surfaceLight = {
  0: '#ffffff',
  1: '#f9fafb',
  2: '#f3f4f6',
  3: '#e5e7eb',
} as const;

/** Surface tokens for dark theme */
export const surfaceDark = {
  0: '#0a0a0a',
  1: '#1a1a1a',
  2: '#2a2a2a',
  3: '#3a3a3a',
} as const;

export type ColorKey = keyof typeof colors;
export type CoralShade = keyof typeof colors.coral;
export type GoldShade = keyof typeof colors.gold;
export type GrayShade = keyof typeof colors.gray;
export type SurfaceToken = keyof typeof surfaceLight;
