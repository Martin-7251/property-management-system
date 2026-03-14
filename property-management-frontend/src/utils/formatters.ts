import { format, parseISO, formatDistanceToNow } from 'date-fns';

/**
 * Format currency (KES)
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date, formatStr: string = 'MMM dd, yyyy'): string => {
  if (!date) return 'N/A';
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, formatStr);
};

/**
 * Format date and time
 */
export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'MMM dd, yyyy HH:mm');
};

/**
 * Format relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
  if (!date) return 'N/A';
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true });
};

/**
 * Format phone number
 */
export const formatPhoneNumber = (phone: string): string => {
  if (!phone) return 'N/A';
  // Format: +254 722 123 456
  if (phone.startsWith('+254')) {
    return phone.replace(/(\+254)(\d{3})(\d{3})(\d{3})/, '$1 $2 $3 $4');
  }
  return phone;
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Truncate text
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (!text || text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Get initials from name
 */
export const getInitials = (name: string): string => {
  if (!name) return '?';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

/**
 * Format status badge color
 */
export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    paid: 'badge-success',
    active: 'badge-success',
    matched: 'badge-success',
    unpaid: 'badge-warning',
    pending: 'badge-warning',
    unmatched: 'badge-warning',
    partially_paid: 'badge-info',
    overdue: 'badge-danger',
    moved_out: 'badge-gray',
    failed: 'badge-danger',
    duplicate: 'badge-gray',
  };
  return colors[status] || 'badge-gray';
};