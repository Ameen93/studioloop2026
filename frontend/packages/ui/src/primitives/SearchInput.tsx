import React, { useState, useCallback, useRef } from 'react';
import { View, TextInput, Pressable, Text, type TextInputProps } from 'react-native';

export interface SearchInputProps extends Omit<TextInputProps, 'onChangeText'> {
  /** Called with debounced search value */
  onSearch: (query: string) => void;
  /** Debounce delay in ms */
  debounceMs?: number;
  /** Placeholder text */
  placeholder?: string;
  /** Additional className */
  className?: string;
}

export function SearchInput({
  onSearch,
  debounceMs = 300,
  placeholder = 'Search...',
  className = '',
  ...props
}: SearchInputProps) {
  const [value, setValue] = useState('');
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleChange = useCallback(
    (text: string) => {
      setValue(text);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => {
        onSearch(text.trim());
      }, debounceMs);
    },
    [onSearch, debounceMs],
  );

  const handleClear = useCallback(() => {
    setValue('');
    onSearch('');
  }, [onSearch]);

  return (
    <View className={`flex-row items-center bg-surface-2 rounded-lg px-3 ${className}`}>
      {/* Search icon */}
      <Text className="text-text-muted mr-2 text-base">{'\u{1F50D}'}</Text>

      <TextInput
        className="flex-1 py-2.5 text-base text-text-primary"
        placeholder={placeholder}
        placeholderTextColor="#6b7280"
        value={value}
        onChangeText={handleChange}
        returnKeyType="search"
        autoCapitalize="none"
        autoCorrect={false}
        {...props}
      />

      {value.length > 0 ? (
        <Pressable onPress={handleClear} className="p-1">
          <Text className="text-text-muted text-lg">{'\u00D7'}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

export default SearchInput;
