import React from 'react';
import {
  Text,
  Pressable,
  ActivityIndicator,
  Platform,
  type PressableProps,
} from 'react-native';

export interface ButtonProps extends Omit<PressableProps, 'children'> {
  /** Button content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  /** Size of the button */
  size?: 'sm' | 'md' | 'lg';
  /** Show loading spinner */
  loading?: boolean;
  /** Disable the button */
  disabled?: boolean;
  /** Additional className for styling */
  className?: string;
  /** Additional text className for styling */
  textClassName?: string;
}

const variantClasses = {
  primary: 'bg-primary-500 active:bg-primary-600',
  secondary: 'bg-gray-200 active:bg-gray-300',
  outline: 'bg-transparent border border-primary-500 active:bg-primary-50',
  ghost: 'bg-transparent active:bg-gray-100',
} as const;

const variantTextClasses = {
  primary: 'text-white',
  secondary: 'text-gray-900',
  outline: 'text-primary-500',
  ghost: 'text-gray-700',
} as const;

const sizeClasses = {
  sm: 'px-3 py-1.5',
  md: 'px-4 py-2',
  lg: 'px-6 py-3',
} as const;

const textSizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
} as const;

const disabledClasses = 'opacity-50';

/**
 * Button component with cross-platform support
 * Uses NativeWind/Tailwind for consistent styling
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  textClassName = '',
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  const buttonClassName = [
    'flex-row items-center justify-center rounded-md',
    variantClasses[variant],
    sizeClasses[size],
    isDisabled ? disabledClasses : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const labelClassName = [
    'font-semibold text-center',
    variantTextClasses[variant],
    textSizeClasses[size],
    textClassName,
  ]
    .filter(Boolean)
    .join(' ');

  // For web, we can render a native button for better accessibility
  if (Platform.OS === 'web') {
    return (
      <Pressable
        className={buttonClassName}
        disabled={isDisabled}
        accessibilityRole="button"
        {...props}
      >
        {loading ? (
          <ActivityIndicator
            size="small"
            color={variant === 'primary' ? '#ffffff' : '#5b6ff2'}
            className="mr-2"
          />
        ) : null}
        <Text className={labelClassName}>{children}</Text>
      </Pressable>
    );
  }

  // Native mobile rendering
  return (
    <Pressable
      className={buttonClassName}
      disabled={isDisabled}
      accessibilityRole="button"
      {...props}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === 'primary' ? '#ffffff' : '#5b6ff2'}
          style={{ marginRight: 8 }}
        />
      ) : null}
      <Text className={labelClassName}>{children}</Text>
    </Pressable>
  );
}

export default Button;
