import React from 'react';
import { View, Text, Image, Pressable, type ViewProps } from 'react-native';

export interface ClassCardProps extends Omit<ViewProps, 'children'> {
  /** Class name / title */
  title: string;
  /** Studio or gym name */
  studio: string;
  /** Instructor name */
  instructor?: string;
  /** Formatted time string */
  time: string;
  /** Hero image URI */
  imageUri?: string;
  /** Price display element (use PriceBadge) */
  priceBadge?: React.ReactNode;
  /** Spots remaining */
  spotsRemaining?: number;
  /** Called on card press */
  onPress?: () => void;
  /** Additional className */
  className?: string;
}

export function ClassCard({
  title,
  studio,
  instructor,
  time,
  imageUri,
  priceBadge,
  spotsRemaining,
  onPress,
  className = '',
  ...props
}: ClassCardProps) {
  return (
    <Pressable
      onPress={onPress}
      className={`bg-surface-1 border border-border-default rounded-lg overflow-hidden ${className}`}
      {...props}
    >
      {imageUri ? (
        <Image
          source={{ uri: imageUri }}
          className="w-full h-40"
          resizeMode="cover"
        />
      ) : (
        <View className="w-full h-40 bg-surface-3 items-center justify-center">
          <Text className="text-text-muted text-sm">No image</Text>
        </View>
      )}

      <View className="p-3">
        <View className="flex-row items-start justify-between">
          <View className="flex-1 mr-2">
            <Text className="text-base font-semibold text-text-primary" numberOfLines={1}>
              {title}
            </Text>
            <Text className="text-sm text-text-secondary mt-0.5" numberOfLines={1}>
              {studio}{instructor ? ` \u00B7 ${instructor}` : ''}
            </Text>
          </View>
          {priceBadge}
        </View>

        <View className="flex-row items-center justify-between mt-2">
          <Text className="text-sm text-text-muted">{time}</Text>
          {spotsRemaining !== undefined ? (
            <Text
              className={`text-xs font-medium ${
                spotsRemaining <= 3 ? 'text-error' : 'text-text-muted'
              }`}
            >
              {spotsRemaining} spot{spotsRemaining !== 1 ? 's' : ''} left
            </Text>
          ) : null}
        </View>
      </View>
    </Pressable>
  );
}

export default ClassCard;
