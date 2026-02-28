import React from 'react';
import {
  View,
  Text,
  Modal as RNModal,
  Pressable,
  Platform,
  type ModalProps as RNModalProps,
  KeyboardAvoidingView,
  ScrollView,
} from 'react-native';

export interface ModalProps extends Omit<RNModalProps, 'visible'> {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  className?: string;
  overlayClassName?: string;
  size?: 'sm' | 'md' | 'lg' | 'full';
  closeOnOverlayPress?: boolean;
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  full: 'max-w-full mx-4',
} as const;

const baseOverlayClasses = 'flex-1 bg-black/50 justify-center items-center';
const baseModalClasses = 'bg-surface-1 rounded-lg w-full mx-4 overflow-hidden';

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  className = '',
  overlayClassName = '',
  size = 'md',
  closeOnOverlayPress = true,
  animationType = 'fade',
  ...props
}: ModalProps) {
  const overlayClasses = [baseOverlayClasses, overlayClassName]
    .filter(Boolean)
    .join(' ');

  const modalClasses = [baseModalClasses, sizeClasses[size], className]
    .filter(Boolean)
    .join(' ');

  const handleOverlayPress = () => {
    if (closeOnOverlayPress) {
      onClose();
    }
  };

  const keyboardBehavior = Platform.OS === 'ios' ? 'padding' : 'height';

  return (
    <RNModal
      visible={isOpen}
      transparent
      animationType={animationType}
      onRequestClose={onClose}
      statusBarTranslucent
      {...props}
    >
      <KeyboardAvoidingView
        behavior={keyboardBehavior}
        className="flex-1"
      >
        <Pressable
          className={overlayClasses}
          onPress={handleOverlayPress}
        >
          <Pressable
            className={modalClasses}
            onPress={(e) => e.stopPropagation()}
          >
            {title ? (
              <View className="flex-row items-center justify-between px-4 py-3 border-b border-border-default">
                <Text className="text-lg font-semibold text-text-primary">
                  {title}
                </Text>
                <Pressable
                  onPress={onClose}
                  className="p-1 rounded-full active:bg-surface-2"
                  accessibilityLabel="Close modal"
                  accessibilityRole="button"
                >
                  <Text className="text-2xl text-text-muted leading-none">
                    ×
                  </Text>
                </Pressable>
              </View>
            ) : null}

            <ScrollView className="max-h-96">
              <View className="p-4">{children}</View>
            </ScrollView>
          </Pressable>
        </Pressable>
      </KeyboardAvoidingView>
    </RNModal>
  );
}

export default Modal;
