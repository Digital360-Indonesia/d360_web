import { getCollection } from 'astro:content';

export interface CustomerStory {
  company: string;
  title: string;
  excerpt: string;
  industry: string;
  product: string;
  logo: string;
  coverImage: string;
  slug: string;
  date: string;
}

export async function getAllCustomerStories(): Promise<CustomerStory[]> {
  try {
    const allStories = await getCollection('customerStories', ({ data }) => {
      return data.published;
    });

    return allStories
      .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime())
      .map((story) => ({
        company: story.data.company,
        title: story.data.title,
        excerpt: story.data.excerpt,
        industry: story.data.industry,
        product: story.data.product,
        logo: story.data.logo,
        coverImage: story.data.coverImage,
        slug: story.slug,
        date: story.data.date
      }));
  } catch (error) {
    console.error('Error reading customer stories:', error);
    return [];
  }
}

export async function getAllCustomerStoriesWithDate(): Promise<Array<{ slug: string; date: string }>> {
  try {
    const allStories = await getCollection('customerStories', ({ data }) => {
      return data.published;
    });

    return allStories
      .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime())
      .map((story) => ({
        slug: story.slug,
        date: story.data.date
      }));
  } catch (error) {
    console.error('Error reading customer stories:', error);
    return [];
  }
}
