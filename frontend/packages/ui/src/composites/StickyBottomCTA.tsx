import React from 'react';
import { View, Text, Platform, type ViewProps } from 'react-native';

export interface StickyBottomCTAProps extends ViewProps {
  /** Context text shown to the left of the button */
  contextText?: string;
  /** CTA button element */
  children: React.ReactNode;
  /** Additional className */
  className?: string;
}

export function StickyBottomCTA({
  contextText,
  children,
  className = '',
  ...props
}: StickyBottomCTAProps) {
  const paddingBottom = Platform.OS === 'ios' ? 'pb-8' : 'pb-4';

  return (
    <View
      className={`bg-surface-1 border-t border-border-default px-4 pt-3 ${paddingBottom} ${className}`}
      style={Platform.OS === 'web' ? { position: 'sticky' as unknown as 'relative', bottom: 0 } : undefined}
      {...props}
    >
      <View className="flex-row items-center justify-between">
        {contextText ? (
          <Text className="text-sm text-text-secondary flex-1 mr-3" numberOfLines={2}>
            {contextText}
          </Text>
        ) : null}
        <View className={contextText ? '' : 'flex-1'}>{children}</View>
      </View>
    </View>
  );
}

export default StickyBottomCTA;
