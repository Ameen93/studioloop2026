import React from 'react';
import {
  View,
  Text,
  TextInput,
  type TextInputProps,
} from 'react-native';

export interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helperText?: string;
  size?: 'sm' | 'md' | 'lg';
  containerClassName?: string;
  className?: string;
  labelClassName?: string;
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-4 py-3 text-lg',
} as const;

const baseLabelClasses = 'text-sm font-medium text-text-secondary mb-1';
const baseInputClasses =
  'bg-surface-1 border rounded-md focus:outline-none focus:ring-2 focus:ring-coral-500 focus:border-coral-500 text-text-primary';
const errorInputClasses = 'border-error focus:ring-error focus:border-error';
const normalInputClasses = 'border-border-default';
const errorTextClasses = 'text-sm text-error mt-1';
const helperTextClasses = 'text-sm text-text-muted mt-1';

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
        placeholderTextColor="#6b7280"
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
