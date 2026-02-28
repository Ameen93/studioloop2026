import React from 'react';
import { View, Text, Pressable, type ViewProps } from 'react-native';

export interface ActionItemCardProps extends Omit<ViewProps, 'children'> {
  /** Severity level determines the accent border color */
  severity: 'critical' | 'warning' | 'info';
  /** Icon element */
  icon?: React.ReactNode;
  /** Alert title */
  title: string;
  /** Count or detail text */
  count?: number | string;
  /** Description text */
  description?: string;
  /** Primary action */
  onAction?: () => void;
  /** Primary action label */
  actionLabel?: string;
  /** Additional className */
  className?: string;
}

const severityBorder = {
  critical: 'border-l-error',
  warning: 'border-l-warning',
  info: 'border-l-coral-500',
} as const;

export function ActionItemCard({
  severity,
  icon,
  title,
  count,
  description,
  onAction,
  actionLabel = 'View',
  className = '',
  ...props
}: ActionItemCardProps) {
  return (
    <View
      className={`bg-surface-1 border border-border-default border-l-4 ${severityBorder[severity]} rounded-lg p-4 ${className}`}
      {...props}
    >
      <View className="flex-row items-start">
        {icon ? <View className="mr-3 mt-0.5">{icon}</View> : null}
        <View className="flex-1">
          <View className="flex-row items-center justify-between">
            <Text className="text-sm font-semibold text-text-primary">{title}</Text>
            {count !== undefined ? (
              <Text className="text-sm font-bold text-text-primary">{count}</Text>
            ) : null}
          </View>
          {description ? (
            <Text className="text-xs text-text-muted mt-1">{description}</Text>
          ) : null}
        </View>
      </View>
      {onAction ? (
        <Pressable
          onPress={onAction}
          className="mt-3 self-end"
        >
          <Text className="text-sm font-medium text-accent-500">{actionLabel}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

export default ActionItemCard;
