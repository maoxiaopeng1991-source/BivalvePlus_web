import en from './en.json';
import pt from './pt.json';

const translations = { en, pt } as const;

export type Locale = keyof typeof translations;
export const defaultLocale: Locale = 'en';
export const locales: Locale[] = ['en', 'pt'];

export function t(locale: Locale, key: string): string {
  const keys = key.split('.');
  let value: any = translations[locale];
  for (const k of keys) {
    value = value?.[k];
  }
  return (value as string) ?? key;
}

export function getLocaleFromUrl(url: URL): Locale {
  const [, , locale] = url.pathname.split('/');
  if (locale && locales.includes(locale as Locale)) {
    return locale as Locale;
  }
  return defaultLocale;
}

export function getLocalizedPath(path: string, locale: Locale): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${locale}${path}`;
}
