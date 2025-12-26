import { getCollection } from 'astro:content';

export interface BlogPost {
  title: string;
  excerpt: string;
  category: string;
  date: string;
  readTime: string;
  author: string;
  image: string;
  slug: string;
  tags: string[];
}

export interface BlogPaginationParams {
  offset: number;
  limit: number;
  category?: string;
  search?: string;
}

export interface BlogPaginationResult {
  posts: BlogPost[];
  total: number;
  hasMore: boolean;
}

export async function getAllBlogPosts(): Promise<BlogPost[]> {
  try {
    const allBlogPosts = await getCollection('blog', ({ data }) => {
      return data.published;
    });

    return allBlogPosts
      .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime())
      .map((post) => ({
        title: post.data.title,
        excerpt: post.data.excerpt,
        category: post.data.category,
        date: new Date(post.data.date).toLocaleDateString('id-ID', {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        }),
        readTime: post.data.readTime,
        author: post.data.author,
        image: post.data.image || 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1200&h=715&fit=crop',
        slug: post.slug,
        tags: post.data.tags || []
      }));
  } catch (error) {
    console.error('Error reading blog posts:', error);
    return [];
  }
}

export async function getBlogCategories(): Promise<string[]> {
  try {
    const posts = await getAllBlogPosts();
    const categories = Array.from(new Set(posts.map(post => post.category)));
    return categories.sort();
  } catch (error) {
    console.error('Error getting categories:', error);
    return [];
  }
}

export async function getBlogPostsPaginated(params: BlogPaginationParams): Promise<BlogPaginationResult> {
  try {
    const { offset, limit, category, search } = params;

    let posts = await getAllBlogPosts();

    // Apply category filter
    if (category && category !== 'Semua' && category !== 'all') {
      posts = posts.filter(post => post.category === category);
    }

    // Apply search filter
    if (search) {
      const searchLower = search.toLowerCase();
      posts = posts.filter(post => {
        const title = post.title.toLowerCase();
        const excerpt = (post.excerpt || '').toLowerCase();
        const tags = (post.tags || []).join(' ').toLowerCase();
        const categoryName = post.category.toLowerCase();
        return title.includes(searchLower) ||
               excerpt.includes(searchLower) ||
               tags.includes(searchLower) ||
               categoryName.includes(searchLower);
      });
    }

    const total = posts.length;
    const hasMore = offset + limit < total;

    // Apply pagination
    const paginatedPosts = posts.slice(offset, offset + limit);

    return {
      posts: paginatedPosts,
      total,
      hasMore
    };
  } catch (error) {
    console.error('Error getting paginated blog posts:', error);
    return {
      posts: [],
      total: 0,
      hasMore: false
    };
  }
}

export async function getBlogPostBySlug(slug: string): Promise<BlogPost | null> {
  try {
    const posts = await getAllBlogPosts();
    return posts.find(post => post.slug === slug) || null;
  } catch (error) {
    console.error(`Error reading blog post ${slug}:`, error);
    return null;
  }
}

export async function getAllBlogPostsWithDate(): Promise<Array<{ slug: string; date: string }>> {
  try {
    const allBlogPosts = await getCollection('blog', ({ data }) => {
      return data.published;
    });

    return allBlogPosts
      .sort((a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime())
      .map((post) => ({
        slug: post.slug,
        date: post.data.date
      }));
  } catch (error) {
    console.error('Error reading blog posts:', error);
    return [];
  }
}
