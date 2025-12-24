import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  schema: z.object({
    title: z.string(),
    excerpt: z.string(),
    category: z.string(),
    date: z.string(),
    readTime: z.string(),
    author: z.string(),
    image: z.string().optional(),
    tags: z.array(z.string()).optional(),
    published: z.boolean().default(true),
  }),
});

const customerStories = defineCollection({
  schema: z.object({
    company: z.string(),
    title: z.string(),
    excerpt: z.string(),
    industry: z.enum(['dental', 'pharmacy', 'manufacture', 'outsourcing', 'logistic', 'others']),
    product: z.string(),
    logo: z.string(),
    coverImage: z.string(),
    stats: z.object({
      metric1: z.string().optional(),
      metric2: z.string().optional(),
      metric3: z.string().optional(),
    }).optional(),
    overview: z.string(),
    problem: z.string(),
    solution: z.string(),
    images: z.array(z.string()).optional(),
    published: z.boolean().default(true),
    date: z.string(),
  }),
});

export const collections = {
  blog,
  customerStories,
};