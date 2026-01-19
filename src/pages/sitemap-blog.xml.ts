import type { APIRoute } from 'astro';
import { getAllBlogPostsWithDate } from '../lib/blog';

export const prerender = false;

export const GET: APIRoute = async (context) => {
  const siteUrl = context.site?.toString().replace(/\/$/, '') || 'https://digital360.id';

  // Get all blog posts with dates
  const blogPosts = await getAllBlogPostsWithDate();

  const urls = blogPosts.map((post) => {
    return `
  <url>
    <loc>${siteUrl}/blog/${post.slug}</loc>
    <lastmod>${post.date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="id" href="${siteUrl}/blog/${post.slug}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${siteUrl}/blog/${post.slug}"/>
  </url>`;
  }).join('');

  // Add blog index page
  const blogIndex = `
  <url>
    <loc>${siteUrl}/blog</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="id" href="${siteUrl}/blog"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${siteUrl}/blog"/>
  </url>`;

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${blogIndex}${urls}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
