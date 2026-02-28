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
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'accent';
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
  primary: 'bg-coral-500 active:bg-coral-600',
  secondary: 'bg-surface-2 active:bg-surface-3',
  outline: 'bg-transparent border border-coral-500 active:bg-coral-50',
  ghost: 'bg-transparent active:bg-surface-2',
  accent: 'bg-accent-500 active:bg-accent-600',
} as const;

const variantTextClasses = {
  primary: 'text-white',
  secondary: 'text-text-primary',
  outline: 'text-coral-500',
  ghost: 'text-text-secondary',
  accent: 'text-white',
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

  const spinnerColor = variant === 'primary' || variant === 'accent' ? '#ffffff' : '#FF6B4A';

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
            color={spinnerColor}
            className="mr-2"
          />
        ) : null}
        <Text className={labelClassName}>{children}</Text>
      </Pressable>
    );
  }

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
          color={spinnerColor}
          style={{ marginRight: 8 }}
        />
      ) : null}
      <Text className={labelClassName}>{children}</Text>
    </Pressable>
  );
}

export default Button;
