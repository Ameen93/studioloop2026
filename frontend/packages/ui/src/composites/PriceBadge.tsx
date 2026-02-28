import React from 'react';
import { View, Text, type ViewProps } from 'react-native';

export interface PriceBadgeProps extends Omit<ViewProps, 'children'> {
  /** Price type */
  type: 'included' | 'credit' | 'currency' | 'free';
  /** Number of credits (when type='credit') */
  credits?: number;
  /** Currency amount string (when type='currency'), e.g. "R 120" */
  amount?: string;
  /** Additional className */
  className?: string;
}

const typeConfig = {
  included: { label: 'Included', bg: 'bg-success/10', text: 'text-success-dark' },
  credit: { label: 'Credit', bg: 'bg-coral-50', text: 'text-coral-700' },
  currency: { label: '', bg: 'bg-surface-2', text: 'text-text-primary' },
  free: { label: 'Free', bg: 'bg-success/10', text: 'text-success-dark' },
} as const;

export function PriceBadge({
  type,
  credits,
  amount,
  className = '',
  ...props
}: PriceBadgeProps) {
  const config = typeConfig[type];

  let displayText: string;
  switch (type) {
    case 'included':
      displayText = 'Included';
      break;
    case 'credit':
      displayText = `${credits ?? 1} Credit${(credits ?? 1) > 1 ? 's' : ''}`;
      break;
    case 'currency':
      displayText = amount ?? '';
      break;
    case 'free':
      displayText = 'Free';
      break;
  }

  return (
    <View
      className={`px-2 py-1 rounded-full ${config.bg} ${className}`}
      {...props}
    >
      <Text className={`text-xs font-medium ${config.text}`}>
        {displayText}
      </Text>
    </View>
  );
}

export default PriceBadge;
