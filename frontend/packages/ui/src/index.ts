// Primitive Components
export { Button } from './primitives/Button';
export type { ButtonProps } from './primitives/Button';

export { Input } from './primitives/Input';
export type { InputProps } from './primitives/Input';

export { Card, CardHeader, CardContent, CardFooter } from './primitives/Card';
export type {
  CardProps,
  CardHeaderProps,
  CardContentProps,
  CardFooterProps,
} from './primitives/Card';

export { Modal } from './primitives/Modal';
export type { ModalProps } from './primitives/Modal';

export { SkeletonLoader } from './primitives/SkeletonLoader';
export type { SkeletonLoaderProps } from './primitives/SkeletonLoader';

export { FilterChips } from './primitives/FilterChips';
export type { FilterChipsProps, FilterChip } from './primitives/FilterChips';

export { SearchInput } from './primitives/SearchInput';
export type { SearchInputProps } from './primitives/SearchInput';

// Composite Components
export { MetricCard } from './composites/MetricCard';
export type { MetricCardProps } from './composites/MetricCard';

export { ClassCard } from './composites/ClassCard';
export type { ClassCardProps } from './composites/ClassCard';

export { PriceBadge } from './composites/PriceBadge';
export type { PriceBadgeProps } from './composites/PriceBadge';

export { StickyBottomCTA } from './composites/StickyBottomCTA';
export type { StickyBottomCTAProps } from './composites/StickyBottomCTA';

export { ActionItemCard } from './composites/ActionItemCard';
export type { ActionItemCardProps } from './composites/ActionItemCard';

export { StatusFlash } from './composites/StatusFlash';
export type { StatusFlashProps } from './composites/StatusFlash';

// Design Tokens
export * from './tokens/colors';
export * from './tokens/spacing';
export * from './tokens/typography';

// Package version
export const UI_VERSION = '0.2.0';
