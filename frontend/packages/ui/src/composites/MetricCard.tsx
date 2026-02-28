import React from 'react';
import { View, Text, type ViewProps } from 'react-native';

export interface MetricCardProps extends ViewProps {
  /** Icon element to render */
  icon?: React.ReactNode;
  /** Metric value (displayed large, thin weight) */
  value: string | number;
  /** Label below the value */
  label: string;
  /** Trend indicator: positive, negative, or neutral */
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string;
  };
  /** Additional className */
  className?: string;
}

const trendColors = {
  up: 'text-success',
  down: 'text-error',
  neutral: 'text-text-muted',
} as const;

const trendArrows = {
  up: '\u2191',
  down: '\u2193',
  neutral: '\u2192',
} as const;

export function MetricCard({
  icon,
  value,
  label,
  trend,
  className = '',
  ...props
}: MetricCardProps) {
  return (
    <View
      className={`bg-surface-1 border border-border-default rounded-lg p-4 ${className}`}
      {...props}
    >
      {icon ? <View className="mb-2">{icon}</View> : null}
      <Text className="text-2xl font-light text-text-primary">{value}</Text>
      <Text className="text-xs text-text-muted mt-1">{label}</Text>
      {trend ? (
        <Text className={`text-xs mt-1 ${trendColors[trend.direction]}`}>
          {trendArrows[trend.direction]} {trend.value}
        </Text>
      ) : null}
    </View>
  );
}

export default MetricCard;
