import React from 'react';
import {
  View,
  Text,
  TextInput,
  type TextInputProps,
} from 'react-native';

export interface InputProps extends TextInputProps {
  /** Label text above the input */
  label?: string;
  /** Error message to display */
  error?: string;
  /** Helper text below the input */
  helperText?: string;
  /** Size of the input */
  size?: 'sm' | 'md' | 'lg';
  /** Additional container className */
  containerClassName?: string;
  /** Additional input className */
  className?: string;
  /** Additional label className */
  labelClassName?: string;
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-4 py-3 text-lg',
} as const;

const baseLabelClasses = 'text-sm font-medium text-gray-700 mb-1';
const baseInputClasses =
  'bg-white border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500';
const errorInputClasses = 'border-error focus:ring-error focus:border-error';
const normalInputClasses = 'border-gray-300';
const errorTextClasses = 'text-sm text-error mt-1';
const helperTextClasses = 'text-sm text-gray-500 mt-1';

/**
 * Input component with cross-platform support
 * Includes label, error, and helper text
 */
export function Input({
  label,
  error,
  helperText,
  size = 'md',
  containerClassName = '',
  className = '',
  labelClassName = '',
  placeholder,
  ...props
}: InputProps) {
  const inputClassName = [
    baseInputClasses,
    sizeClasses[size],
    error ? errorInputClasses : normalInputClasses,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const labelClasses = [baseLabelClasses, labelClassName].filter(Boolean).join(' ');

  return (
    <View className={`w-full ${containerClassName}`}>
      {label ? <Text className={labelClasses}>{label}</Text> : null}
      <TextInput
        className={inputClassName}
        placeholder={placeholder}
        placeholderTextColor="#9ca3af"
        accessibilityLabel={label || placeholder}
        {...props}
      />
      {error ? <Text className={errorTextClasses}>{error}</Text> : null}
      {helperText && !error ? (
        <Text className={helperTextClasses}>{helperText}</Text>
      ) : null}
    </View>
  );
}

export default Input;
