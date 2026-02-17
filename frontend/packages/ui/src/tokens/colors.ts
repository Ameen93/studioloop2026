/**
 * StudioLoop Brand Colors
 * Design tokens for consistent color usage across all platforms
 */
export const colors = {
  primary: {
    50: '#f0f5ff',
    100: '#e0ebff',
    200: '#c7d7fe',
    300: '#a4bbfc',
    400: '#7c96f8',
    500: '#5b6ff2', // Primary brand color
    600: '#4650e6',
    700: '#3a3fd3',
    800: '#3235ab',
    900: '#2d3288',
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

export type ColorKey = keyof typeof colors;
export type PrimaryShade = keyof typeof colors.primary;
export type GrayShade = keyof typeof colors.gray;
