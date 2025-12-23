import re
import os
from pathlib import Path

def extract_urls_from_xml(xml_file):
    """Extract all URLs from sitemap XML file"""
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        urls = re.findall(r'<loc><!\[CDATA\[https://digital360\.id/([^]]+)\]\]></loc>', content)
        return [url.rstrip('/') for url in urls]
    except Exception as e:
        print(f"Error reading {xml_file}: {e}")
        return []

def check_page_exists(url_path):
    """Check if page exists in Astro project"""
    # Remove trailing slash
    url_path = url_path.rstrip('/')
    
    # Homepage
    if url_path == '':
        return True, 'src/pages/index.astro'
    
    # Blog posts
    if url_path.startswith('blog/'):
        slug = url_path.replace('blog/', '')
        blog_file = f"src/content/blog/{slug}.md"
        exists = os.path.exists(blog_file)
        return exists, blog_file if exists else f"MISSING: {blog_file}"
    
    # Check Astro pages
    page_mappings = {
        'tentang-kami': 'src/pages/tentang-kami.astro',
        'kontak-kami': 'src/pages/kontak-kami.astro',
        'portofolio': 'src/pages/portofolio.astro',
    }
    
    # Direct page match
    if url_path in page_mappings:
        exists = os.path.exists(page_mappings[url_path])
        return exists, page_mappings[url_path] if exists else f"MISSING: {page_mappings[url_path]}"
    
    # Portfolio pages
    if url_path.startswith('portfolio/'):
        # These don't exist as separate pages in Astro
        return False, "Portfolio pages not implemented yet"
    
    # Service pages
    service_pages = [
        'iliki-tim-sosial-media-anda',  # missing 'm'
        'get-started', 'get-started/step2', 'get-started/step3',
        'ramadhan-telah-tiba',
        'jasa-social-media-management',
        'garment360', 'ai-try-on-model', 'dental-management-system', 'ai-services',
        'creative-branding-design', 'ads-solution-management',
        'social-media-marketing-content-creation', 'web-app-development',
        'dental-care-app', 'lead-generation',
        'commercial-photography-videography', 'copywriting-seo-optimization',
        'integrated-digital-marketing-project'
    ]
    
    if url_path in service_pages:
        return False, f"Service page: {url_path}.astro"
    
    # Tag pages (not implemented in Astro)
    if url_path.startswith('tag/'):
        return False, "Tag pages not implemented (intentionally)"
    
    # Category pages (not implemented in Astro)
    if url_path.startswith('category/'):
        return False, "Category pages not implemented (intentionally)"
    
    # Everything else is likely a blog post
    blog_file = f"src/content/blog/{url_path}.md"
    if os.path.exists(blog_file):
        return True, blog_file
    return False, f"MISSING: {blog_file}"

# Process all sitemaps
files = {
    'Pages': 'd360-sitemap-page.xml',
    'Posts': 'd360-sitemap-post.xml',
    'Projects': 'd360-sitemap-project.xml',
    'Tags': 'd360-sitemap-post_tag.xml'
}

print("=" * 80)
print("MISSING PAGES ANALYSIS")
print("=" * 80)
print("\n")

all_missing = {}

for name, file in files.items():
    urls = extract_urls_from_xml(file)
    print(f"\n{'='*80}")
    print(f"{name.upper()}: {len(urls)} URLs")
    print(f"{'='*80}")
    
    missing_pages = []
    existing_pages = []
    
    for url in urls:
        exists, location = check_page_exists(url)
        if not exists:
            # Skip tag/category pages (intentionally not implemented)
            if not url.startswith('tag/') and not url.startswith('category/'):
                missing_pages.append({'url': url, 'expected': location})
        else:
            existing_pages.append({'url': url, 'location': location})
    
    all_missing[name] = missing_pages
    
    print(f"\n✅ Existing: {len(existing_pages)} pages")
    print(f"❌ Missing: {len(missing_pages)} pages")
    
    if missing_pages:
        print(f"\n📋 Missing {name.lower()} list:")
        for i, page in enumerate(missing_pages[:20], 1):  # Show first 20
            print(f"   {i}. /{page['url']}")
            print(f"      Expected: {page['expected']}")
        
        if len(missing_pages) > 20:
            print(f"   ... and {len(missing_pages) - 20} more")

print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_missing = sum(len(pages) for pages in all_missing.values())
print(f"\nTotal missing pages: {total_missing}")
print(f"\nBreakdown:")
for name, pages in all_missing.items():
    print(f"  - {name}: {len(pages)} missing")

# Group by type
print("\n\n" + "=" * 80)
print("DETAILED MISSING PAGES BY TYPE")
print("=" * 80)

for name, pages in all_missing.items():
    if pages:
        print(f"\n## {name.upper()} ({len(pages)} missing)")
        print("-" * 80)
        
        # Group by pattern
        service_pages = [p for p in pages if any(x in p['expected'] for x in ['Service page', 'MISSING: src/pages'])]
        portfolio_pages = [p for p in pages if 'portfolio' in p['expected'].lower()]
        blog_posts = [p for p in pages if 'blog' in p['expected'].lower()]
        
        if service_pages:
            print(f"\n📄 Service/Pages ({len(service_pages)}):")
            for p in service_pages[:10]:
                print(f"  - /{p['url']}")
            if len(service_pages) > 10:
                print(f"  ... and {len(service_pages) - 10} more")
        
        if portfolio_pages:
            print(f"\n💼 Portfolio Pages ({len(portfolio_pages)}):")
            for p in portfolio_pages[:10]:
                print(f"  - /{p['url']}")
            if len(portfolio_pages) > 10:
                print(f"  ... and {len(portfolio_pages) - 10} more")
        
        if blog_posts:
            print(f"\n📝 Blog Posts ({len(blog_posts)}):")
            for p in blog_posts[:10]:
                print(f"  - /{p['url']}")
            if len(blog_posts) > 10:
                print(f"  ... and {len(blog_posts) - 10} more")

