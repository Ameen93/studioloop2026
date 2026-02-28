import React from 'react';
import { Text, Pressable, ScrollView, type ViewProps } from 'react-native';

export interface FilterChip {
  id: string;
  label: string;
}

export interface FilterChipsProps extends Omit<ViewProps, 'children'> {
  /** Available filter options */
  chips: FilterChip[];
  /** Currently selected chip IDs */
  selected: string[];
  /** Called when selection changes */
  onSelectionChange: (selected: string[]) => void;
  /** Allow multiple selections */
  multiSelect?: boolean;
  /** Additional className */
  className?: string;
}

export function FilterChips({
  chips,
  selected,
  onSelectionChange,
  multiSelect = false,
  className = '',
  ...props
}: FilterChipsProps) {
  const handlePress = (chipId: string) => {
    if (multiSelect) {
      const newSelection = selected.includes(chipId)
        ? selected.filter((id) => id !== chipId)
        : [...selected, chipId];
      onSelectionChange(newSelection);
    } else {
      onSelectionChange(selected.includes(chipId) ? [] : [chipId]);
    }
  };

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      className={className}
      contentContainerStyle={{ gap: 8 }}
      {...props}
    >
      {chips.map((chip) => {
        const isSelected = selected.includes(chip.id);
        return (
          <Pressable
            key={chip.id}
            onPress={() => handlePress(chip.id)}
            className={`px-4 py-2 rounded-full border ${
              isSelected
                ? 'bg-accent-500 border-accent-500'
                : 'bg-surface-1 border-border-default'
            }`}
          >
            <Text
              className={`text-sm font-medium ${
                isSelected ? 'text-white' : 'text-text-secondary'
              }`}
            >
              {chip.label}
            </Text>
          </Pressable>
        );
      })}
    </ScrollView>
  );
}

export default FilterChips;
