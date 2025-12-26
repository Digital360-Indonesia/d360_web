import type { APIRoute } from 'astro';
import { getAllCustomerStoriesWithDate } from '../lib/customer-stories';

export const prerender = false;

export const GET: APIRoute = async (context) => {
  const siteUrl = context.site?.toString().replace(/\/$/, '') || 'https://digital360.id';

  // Get all customer stories with dates
  const stories = await getAllCustomerStoriesWithDate();

  const urls = stories.map((story) => {
    return `
  <url>
    <loc>${siteUrl}/customer-stories/${story.slug}</loc>
    <lastmod>${story.date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
    <xhtml:link rel="alternate" hreflang="en" href="${siteUrl}/customer-stories/${story.slug}"/>
    <xhtml:link rel="alternate" hreflang="id" href="${siteUrl}/customer-stories/${story.slug}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${siteUrl}/customer-stories/${story.slug}"/>
  </url>`;
  }).join('');

  // Add customer stories index page (bilingual)
  const indexPages = `
  <url>
    <loc>${siteUrl}/customer-stories</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="en" href="${siteUrl}/customer-stories"/>
    <xhtml:link rel="alternate" hreflang="id" href="${siteUrl}/customer-stories"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="${siteUrl}/customer-stories"/>
  </url>`;

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${indexPages}${urls}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
