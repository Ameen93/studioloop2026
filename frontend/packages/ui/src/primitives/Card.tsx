import React from 'react';
import { View, Text, type ViewProps } from 'react-native';

export interface CardProps extends ViewProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  className?: string;
}

export interface CardHeaderProps extends ViewProps {
  children: React.ReactNode;
  className?: string;
}

export interface CardContentProps extends ViewProps {
  children: React.ReactNode;
  className?: string;
}

export interface CardFooterProps extends ViewProps {
  children: React.ReactNode;
  className?: string;
}

const baseCardClasses = 'bg-surface-1 rounded-lg overflow-hidden';

const variantClasses = {
  default: 'border border-border-default',
  elevated: 'shadow-md',
  outlined: 'border-2 border-border-default',
} as const;

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

export function CardHeader({
  children,
  className = '',
  ...props
}: CardHeaderProps) {
  const headerClassName = ['px-4 py-3 border-b border-border-default', className]
    .filter(Boolean)
    .join(' ');

  return (
    <View className={headerClassName} {...props}>
      {typeof children === 'string' ? (
        <Text className="text-lg font-semibold text-text-primary">{children}</Text>
      ) : (
        children
      )}
    </View>
  );
}

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

export function CardFooter({
  children,
  className = '',
  ...props
}: CardFooterProps) {
  const footerClassName = [
    'px-4 py-3 border-t border-border-default bg-surface-2',
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
