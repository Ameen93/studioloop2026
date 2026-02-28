import React, { useEffect, useRef } from 'react';
import { Text, Animated, type ViewProps } from 'react-native';

export interface StatusFlashProps extends Omit<ViewProps, 'children'> {
  /** Status determines the color */
  status: 'success' | 'warning' | 'error' | 'neutral';
  /** Main message */
  message: string;
  /** Sub-message */
  subMessage?: string;
  /** Auto-dismiss after ms (0 = no auto-dismiss) */
  duration?: number;
  /** Called when flash should close */
  onDismiss?: () => void;
  /** Whether the flash is visible */
  visible: boolean;
  /** Additional className */
  className?: string;
}

const statusConfig = {
  success: { bg: 'bg-success', icon: '\u2713' },
  warning: { bg: 'bg-warning', icon: '\u26A0' },
  error: { bg: 'bg-error', icon: '\u2717' },
  neutral: { bg: 'bg-gray-500', icon: '\u2139' },
} as const;

export function StatusFlash({
  status,
  message,
  subMessage,
  duration = 2000,
  onDismiss,
  visible,
  className = '',
  ...props
}: StatusFlashProps) {
  const opacity = useRef(new Animated.Value(0)).current;
  const scale = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.spring(scale, {
          toValue: 1,
          useNativeDriver: true,
        }),
      ]).start();

      if (duration > 0) {
        const timer = setTimeout(() => {
          Animated.timing(opacity, {
            toValue: 0,
            duration: 300,
            useNativeDriver: true,
          }).start(() => onDismiss?.());
        }, duration);
        return () => clearTimeout(timer);
      }
    } else {
      opacity.setValue(0);
      scale.setValue(0.8);
    }
  }, [visible, duration, opacity, scale, onDismiss]);

  if (!visible) return null;

  const config = statusConfig[status];

  return (
    <Animated.View
      className={`absolute inset-0 items-center justify-center ${config.bg} ${className}`}
      style={{ opacity, transform: [{ scale }] }}
      {...props}
    >
      <Text className="text-white text-6xl mb-4">{config.icon}</Text>
      <Text className="text-white text-2xl font-bold text-center px-8">
        {message}
      </Text>
      {subMessage ? (
        <Text className="text-white/80 text-base text-center mt-2 px-8">
          {subMessage}
        </Text>
      ) : null}
    </Animated.View>
  );
}

export default StatusFlash;
