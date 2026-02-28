import React from 'react';
import { View, Animated, type ViewProps } from 'react-native';

export interface SkeletonLoaderProps extends ViewProps {
  /** Shape variant */
  variant?: 'text' | 'card' | 'metric' | 'avatar' | 'image';
  /** Width (for text/image) */
  width?: number | `${number}%`;
  /** Height override */
  height?: number;
  /** Number of text lines */
  lines?: number;
  /** Additional className */
  className?: string;
}

const variantDefaults = {
  text: { height: 16, className: 'rounded' },
  card: { height: 120, className: 'rounded-lg' },
  metric: { height: 80, className: 'rounded-lg' },
  avatar: { height: 48, className: 'rounded-full' },
  image: { height: 200, className: 'rounded-lg' },
} as const;

function SkeletonBlock({
  height,
  width,
  rounded,
  className = '',
}: {
  height: number;
  width?: number | `${number}%`;
  rounded: string;
  className?: string;
}) {
  const shimmerAnim = React.useRef(new Animated.Value(0.3)).current;

  React.useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(shimmerAnim, {
          toValue: 0.7,
          duration: 800,
          useNativeDriver: true,
        }),
        Animated.timing(shimmerAnim, {
          toValue: 0.3,
          duration: 800,
          useNativeDriver: true,
        }),
      ]),
    );
    animation.start();
    return () => animation.stop();
  }, [shimmerAnim]);

  return (
    <Animated.View
      className={`bg-surface-3 ${rounded} ${className}`}
      style={[
        {
          height,
          width: width ?? '100%',
          opacity: shimmerAnim,
        },
      ]}
    />
  );
}

export function SkeletonLoader({
  variant = 'text',
  width,
  height,
  lines = 3,
  className = '',
  ...props
}: SkeletonLoaderProps) {
  const defaults = variantDefaults[variant];
  const h = height ?? defaults.height;

  if (variant === 'text') {
    return (
      <View className={`gap-2 ${className}`} {...props}>
        {Array.from({ length: lines }).map((_, i) => (
          <SkeletonBlock
            key={i}
            height={h}
            width={i === lines - 1 ? '60%' as `${number}%` : undefined}
            rounded={defaults.className}
          />
        ))}
      </View>
    );
  }

  if (variant === 'avatar') {
    return (
      <SkeletonBlock
        height={h}
        width={h}
        rounded={defaults.className}
        className={className}
      />
    );
  }

  return (
    <SkeletonBlock
      height={h}
      width={width}
      rounded={defaults.className}
      className={className}
    />
  );
}

export default SkeletonLoader;
