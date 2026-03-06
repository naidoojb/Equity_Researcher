/**
 * Type definitions for navigation params.
 * With expo-router the actual navigation is handled via file-based routing,
 * but these types are exported for compatibility with screen components.
 */

export type RootStackParamList = {
  Home: undefined;
  Stock: { ticker: string };
  Research: { ticker: string };
};
