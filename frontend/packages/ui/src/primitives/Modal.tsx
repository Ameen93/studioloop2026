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
  /** Whether the modal is open */
  isOpen: boolean;
  /** Called when the modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal content */
  children: React.ReactNode;
  /** Additional className for the modal container */
  className?: string;
  /** Additional className for the overlay */
  overlayClassName?: string;
  /** Size of the modal */
  size?: 'sm' | 'md' | 'lg' | 'full';
  /** Whether clicking the overlay closes the modal */
  closeOnOverlayPress?: boolean;
}

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  full: 'max-w-full mx-4',
} as const;

const baseOverlayClasses = 'flex-1 bg-black/50 justify-center items-center';
const baseModalClasses = 'bg-white rounded-lg w-full mx-4 overflow-hidden';

/**
 * Modal component with cross-platform support
 * Renders an overlay with centered content
 */
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
            {/* Header */}
            {title ? (
              <View className="flex-row items-center justify-between px-4 py-3 border-b border-gray-200">
                <Text className="text-lg font-semibold text-gray-900">
                  {title}
                </Text>
                <Pressable
                  onPress={onClose}
                  className="p-1 rounded-full active:bg-gray-100"
                  accessibilityLabel="Close modal"
                  accessibilityRole="button"
                >
                  <Text className="text-2xl text-gray-500 leading-none">
                    ×
                  </Text>
                </Pressable>
              </View>
            ) : null}

            {/* Content */}
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
