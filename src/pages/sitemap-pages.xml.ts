import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = (context) => {
  const siteUrl = context.site?.toString().replace(/\/$/, '') || 'https://digital360.id';
  const today = new Date().toISOString().split('T')[0];

  // Static pages with bilingual support
  const pages = [
    { path: '', priority: '1.0', changefreq: 'daily' },
    { path: '/en', priority: '1.0', changefreq: 'daily' },
    { path: '/id', priority: '1.0', changefreq: 'daily' },
  ];

  const urls = pages.map((page) => {
    return `
  <url>
    <loc>${siteUrl}${page.path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>`;
  }).join('');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
