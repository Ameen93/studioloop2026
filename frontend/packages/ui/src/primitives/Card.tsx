import React from 'react';
import { View, Text, type ViewProps } from 'react-native';

export interface CardProps extends ViewProps {
  /** Card content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'default' | 'elevated' | 'outlined';
  /** Additional className for styling */
  className?: string;
}

export interface CardHeaderProps extends ViewProps {
  /** Header content */
  children: React.ReactNode;
  /** Additional className for styling */
  className?: string;
}

export interface CardContentProps extends ViewProps {
  /** Content */
  children: React.ReactNode;
  /** Additional className for styling */
  className?: string;
}

export interface CardFooterProps extends ViewProps {
  /** Footer content */
  children: React.ReactNode;
  /** Additional className for styling */
  className?: string;
}

const baseCardClasses = 'bg-white rounded-lg overflow-hidden';

const variantClasses = {
  default: 'border border-gray-200',
  elevated: 'shadow-md',
  outlined: 'border-2 border-gray-300',
} as const;

/**
 * Card component with cross-platform support
 * Container for content with variants
 */
export function Card({
  children,
  variant = 'default',
  className = '',
  ...props
}: CardProps) {
  const cardClassName = [baseCardClasses, variantClasses[variant], className]
    .filter(Boolean)
    .join(' ');

  return (
    <View className={cardClassName} {...props}>
      {children}
    </View>
  );
}

/**
 * Card header section
 */
export function CardHeader({
  children,
  className = '',
  ...props
}: CardHeaderProps) {
  const headerClassName = ['px-4 py-3 border-b border-gray-200', className]
    .filter(Boolean)
    .join(' ');

  return (
    <View className={headerClassName} {...props}>
      {typeof children === 'string' ? (
        <Text className="text-lg font-semibold text-gray-900">{children}</Text>
      ) : (
        children
      )}
    </View>
  );
}

/**
 * Card content section
 */
export function CardContent({
  children,
  className = '',
  ...props
}: CardContentProps) {
  const contentClassName = ['px-4 py-4', className].filter(Boolean).join(' ');

  return (
    <View className={contentClassName} {...props}>
      {children}
    </View>
  );
}

/**
 * Card footer section
 */
export function CardFooter({
  children,
  className = '',
  ...props
}: CardFooterProps) {
  const footerClassName = [
    'px-4 py-3 border-t border-gray-200 bg-gray-50',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <View className={footerClassName} {...props}>
      {children}
    </View>
  );
}

export default Card;
