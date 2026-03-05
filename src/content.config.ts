import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const events = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/events' }),
  schema: z.object({
    title: z.string(),
    date: z.string(),
    category: z.enum(['sampling', 'experiment', 'dissemination', 'conference', 'workshop']),
    locale: z.enum(['en', 'pt']),
    description: z.string(),
    image: z.string().optional(),
    lat: z.number().optional(),
    lng: z.number().optional(),
    siteLabel: z.string().optional(),
  }),
});

export const collections = { events };
