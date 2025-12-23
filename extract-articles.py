#!/usr/bin/env python3
"""
Digital360 Article Extractor
Extract articles from digital360.id using WordPress REST API + Sitemap
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from urllib.parse import urlparse
import os
from pathlib import Path
import time

class Digital360Extractor:
    def __init__(self):
        self.base_url = "https://digital360.id"
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.sitemap_file = "d360-sitemap-post.xml"
        self.output_dir = Path("src/content/blog")
        self.public_dir = Path("public/blog")
        self.session = requests.Session()

    def extract_urls_from_sitemap(self):
        """Extract all article URLs from sitemap XML"""
        print("🔍 Extracting URLs from sitemap...")

        try:
            with open(self.sitemap_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove leading whitespace/empty lines
            content = content.strip()

            # Parse XML
            root = ET.fromstring(content)
            urls = []

            # Extract URLs from sitemap
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    urls.append(loc.text)

            print(f"✅ Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            print(f"❌ Error parsing sitemap: {e}")
            return []

    def get_post_by_slug(self, slug):
        """Get post data from WordPress REST API by slug"""
        try:
            # Try multiple endpoints to find the post
            endpoints = [
                f"{self.api_url}/posts?slug={slug}",
                f"{self.api_url}/posts?search={slug}",
            ]

            for endpoint in endpoints:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        post_data = data[0]

                        # Fetch tags data if post has tags
                        if post_data.get('tags') and len(post_data['tags']) > 0:
                            try:
                                tag_ids = ','.join(map(str, post_data['tags']))
                                tags_response = self.session.get(
                                    f"{self.api_url}/tags?include={tag_ids}",
                                    timeout=10
                                )
                                if tags_response.status_code == 200:
                                    tags_data = tags_response.json()
                                    post_data['tags'] = tags_data
                                else:
                                    post_data['tags'] = []
                            except Exception as e:
                                print(f"  ⚠️  Warning: Could not fetch tags for {slug}: {e}")
                                post_data['tags'] = []

                        # Return the post object directly
                        return post_data

            return None

        except Exception as e:
            print(f"  ❌ Error fetching post {slug}: {e}")
            return None

    def download_content_image(self, image_url, slug, date_str):
        """Download content image and return local path"""
        if not image_url or image_url.startswith('data:'):
            return image_url

        try:
            # Generate date-based folder structure
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    year = date_obj.strftime('%Y')
                    month = date_obj.strftime('%m')
                except:
                    year = '2025'
                    month = '12'
            else:
                year = '2025'
                month = '12'

            # Generate filename from URL or use slug-based naming
            parsed_url = urlparse(image_url)
            original_filename = os.path.basename(parsed_url.path)

            if not original_filename or '.' not in original_filename:
                # Generate a unique filename based on slug and counter
                import hashlib
                url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
                original_filename = f"{slug}-{url_hash}.jpg"

            # Clean filename
            original_filename = re.sub(r'[^\w\-_.]', '', original_filename)
            if not original_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                original_filename += '.jpg'

            image_path = self.public_dir / year / month / original_filename

            # Download image if not already exists
            if not image_path.exists():
                if self.download_image(image_url, image_path):
                    local_path = f"/blog/{year}/{month}/{original_filename}"
                    print(f"  📥 Downloaded content image: {original_filename}")
                    return local_path
                else:
                    print(f"  ❌ Failed to download content image: {image_url}")
                    return image_url
            else:
                local_path = f"/blog/{year}/{month}/{original_filename}"
                print(f"  ✅ Using existing content image: {original_filename}")
                return local_path

        except Exception as e:
            print(f"  ❌ Error processing content image {image_url}: {e}")
            return image_url

    def html_to_markdown(self, html_content, slug="", date_str=""):
        """Convert HTML content to Markdown format and download images"""
        if not html_content:
            return ""

        # Basic HTML to Markdown conversion
        markdown = html_content

        # Process images first - find and download all images
        def process_image(match):
            img_src = match.group(1)
            img_alt = match.group(2) if match.group(2) else ""

            # Download image locally
            local_path = self.download_content_image(img_src, slug, date_str)

            # Return markdown with local path
            alt_text = img_alt if img_alt else "Image"
            return f"![{alt_text}]({local_path})"

        # Convert images and download them
        markdown = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>', process_image, markdown)
        markdown = re.sub(r'<img[^>]*src="([^"]*)"[^>]*>', lambda m: process_image((m.group(0), m.group(1), "")), markdown)

        # Convert headings
        markdown = re.sub(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', lambda m: f"{'#' * int(m.group(1))} {m.group(2).strip()}\n\n", markdown)

        # Convert paragraphs
        markdown = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: f"{m.group(1).strip()}\n\n", markdown)

        # Convert bold
        markdown = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', markdown)
        markdown = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', markdown)

        # Convert italic
        markdown = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', markdown)
        markdown = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', markdown)

        # Convert links
        markdown = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', markdown)

        # Convert lists
        markdown = re.sub(r'<ul[^>]*>(.*?)</ul>', lambda m: self._convert_list(m.group(1), 'ul'), markdown)
        markdown = re.sub(r'<ol[^>]*>(.*?)</ol>', lambda m: self._convert_list(m.group(1), 'ol'), markdown)

        # Convert line breaks
        markdown = re.sub(r'<br[^>]*>', '\n', markdown)

        # Remove remaining HTML tags
        markdown = re.sub(r'<[^>]+>', '', markdown)

        # Clean up multiple newlines
        markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)

        return markdown.strip()

    def _convert_list(self, content, list_type):
        """Convert HTML lists to Markdown"""
        items = re.findall(r'<li[^>]*>(.*?)</li>', content)
        if not items:
            return ""

        result = []
        for i, item in enumerate(items):
            if list_type == 'ul':
                prefix = "-"
            else:
                prefix = f"{i+1}."
            result.append(f"{prefix} {item.strip()}")

        return "\n".join(result) + "\n\n"

    def extract_featured_image(self, post_data):
        """Extract featured image URL from post data"""
        if 'featured_media' in post_data and post_data['featured_media']:
            media_id = post_data['featured_media']
            try:
                media_response = self.session.get(f"{self.api_url}/media/{media_id}", timeout=10)
                if media_response.status_code == 200:
                    media_data = media_response.json()
                    return media_data.get('source_url', '')
            except:
                pass

        return ""

    def download_image(self, image_url, save_path):
        """Download image from URL and save to local path"""
        if not image_url:
            return False

        try:
            response = self.session.get(image_url, timeout=30)
            if response.status_code == 200:
                # Create directory if it doesn't exist
                save_path.parent.mkdir(parents=True, exist_ok=True)

                with open(save_path, 'wb') as f:
                    f.write(response.content)

                print(f"  📥 Downloaded image: {save_path}")
                return True
            return False
        except Exception as e:
            print(f"  ❌ Error downloading image {image_url}: {e}")
            return False

    def generate_frontmatter(self, post_data, featured_image_path):
        """Generate Astro frontmatter from WordPress post data"""
        title = post_data.get('title', {}).get('rendered', '')
        content = post_data.get('content', {}).get('rendered', '')
        excerpt = post_data.get('excerpt', {}).get('rendered', '')

        # Clean HTML from title
        title = re.sub(r'<[^>]+>', '', title)
        excerpt = re.sub(r'<[^>]+>', '', excerpt)

        # Parse date
        date_str = post_data.get('date', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except:
                formatted_date = date_str[:10]
        else:
            formatted_date = '2025-12-18'

        # Get categories
        categories = []
        post_categories = post_data.get('categories', [])
        if isinstance(post_categories, list):
            for category in post_categories:
                if isinstance(category, dict):
                    cat_name = category.get('name', '')
                    if cat_name:
                        categories.append(cat_name)

        # Get tags
        tags = []
        post_tags = post_data.get('tags', [])
        if isinstance(post_tags, list):
            for tag in post_tags:
                if isinstance(tag, dict):
                    tag_name = tag.get('name', '')
                    if tag_name:
                        # Clean tag name - remove all hashes and split by # delimiter
                        cleaned_tag = tag_name.strip().lower()

                        # Remove leading hashes
                        cleaned_tag = cleaned_tag.lstrip('#')

                        # If tag contains # in the middle, split by # and process each part
                        if '#' in cleaned_tag:
                            # Split by # and take meaningful parts
                            parts = cleaned_tag.split('#')
                            for part in parts:
                                part = part.strip('-').strip()
                                # Only add if it's a meaningful tag (3+ chars)
                                if part and len(part) >= 3 and not part.isdigit():
                                    tags.append(part)
                        else:
                            # Normal tag - just clean it up
                            cleaned_tag = cleaned_tag.replace('#', '').strip()
                            if len(cleaned_tag) >= 3 and not cleaned_tag.isdigit():
                                tags.append(cleaned_tag)

        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        tags = unique_tags

        # Generate frontmatter
        frontmatter = f"""---
title: "{title.replace('"', '\\"')}"
excerpt: "{excerpt.replace('"', '\\"')[:150]}..."
category: "{categories[0] if categories else 'Blog'}"
date: "{formatted_date}"
readTime: "5 menit"
author: "syanampro"
image: "{featured_image_path if featured_image_path else ''}"
tags: {json.dumps(tags, ensure_ascii=False)}
published: true
---"""

        return frontmatter

    def create_markdown_file(self, slug, post_data):
        """Create markdown file from WordPress post data"""
        print(f"📝 Processing: {slug}")

        # Extract featured image
        featured_image_url = self.extract_featured_image(post_data)
        featured_image_path = ""

        if featured_image_url:
            # Generate date-based folder structure
            date_str = post_data.get('date', '')
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    year = date_obj.strftime('%Y')
                    month = date_obj.strftime('%m')

                    # Download image
                    image_filename = f"{slug}.jpg"
                    image_path = self.public_dir / year / month / image_filename

                    if self.download_image(featured_image_url, image_path):
                        featured_image_path = f"/blog/{year}/{month}/{image_filename}"
                except:
                    pass

        # Convert content to markdown
        content = post_data.get('content', {}).get('rendered', '')
        date_str = post_data.get('date', '')
        markdown_content = self.html_to_markdown(content, slug, date_str)

        # Generate frontmatter
        frontmatter = self.generate_frontmatter(post_data, featured_image_path)

        # Combine frontmatter and content
        markdown_content = frontmatter + "\n\n" + markdown_content

        # Create markdown file
        output_file = self.output_dir / f"{slug}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"  ✅ Created: {output_file}")
        return output_file

    def process_articles(self, limit=None):
        """Process articles from sitemap"""
        urls = self.extract_urls_from_sitemap()

        # Don't limit URLs here, let the processing loop handle it
# if limit:
#     urls = urls[:limit]

        processed = 0
        errors = 0

        print(f"📊 Processing limit: {limit} articles")
        print(f"🔍 Total URLs found: {len(urls)}")
        print(f"🎯 Will process up to limit URLs or until valid posts found")

        processed = 0
        errors = 0
        actual_processed = 0

        for i, url in enumerate(urls):
            if limit and actual_processed >= limit:
                print(f"\n🛑 Reached limit of {limit} articles")
                break

            # Skip first 5 URLs which are existing articles
            if i < 5:
                continue

            try:
                # Extract slug from URL
                slug = url.rstrip('/').split('/')[-1]

                # Skip non-post URLs and category/tag pages
                if not slug or slug in ['berita', 'tentang-kami', 'kontak-kami', 'portofolio', 'get-started', 'author', 'page', 'wp-content', 'wp-admin', 'wp-json', 'xmlrpc.php']:
                    continue

                # Skip if URL doesn't look like a post slug (too short or contains digits that look like IDs)
                if len(slug) < 3 or slug.replace('-', '').replace('_', '').isnumeric():
                    continue

                # Skip existing articles
                existing_articles = ['5-strategi-media-sosial-untuk-meningkatkan-bisnis', 'apa-itu-chronotype-kenali-tipe-produktivitasmu', 'apa-itu-threads-kenali-aplikasi-pesaing-twitter', '10-anak-indonesia-berprestasi', 'apa-itu-dns-pengertian-fungsi-cara-kerja', 'panduan-penulisan-artikel']
                if slug in existing_articles:
                    print(f"  ⏭ Skipping existing article: {slug}")
                    continue

                print(f"\n[{actual_processed+1}/{min(limit, len(urls))} Processing: {url}")
                print(f"   📝 Slug: {slug}")
                actual_processed += 1

                # Get post data via REST API
                post_data = self.get_post_by_slug(slug)

                if post_data:
                    print(f"  📋 Found post: {post_data.get('title', {}).get('rendered', 'N/A')[:50]}...")

                    # Only process published posts
                    if post_data.get('status') == 'publish':
                        try:
                            self.create_markdown_file(slug, post_data)
                            processed += 1
                            print(f"  ✅ Successfully processed: {slug}")
                        except Exception as e:
                            print(f"  ❌ Error creating file: {e}")
                            errors += 1
                    else:
                        print(f"  ⏭ Skipped (not published): {slug}")
                else:
                    print(f"  ❌ Post not found via API: {slug}")
                    errors += 1

                # Rate limiting
                if i < len(urls) - 1:
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\n⏹ Process interrupted by user")
                break
            except Exception as e:
                print(f"  ❌ Error processing {slug}: {e}")
                errors += 1
                continue

        print(f"\n✅ Processing complete!")
        print(f"📊 Processed: {processed} articles")
        print(f"❌ Errors: {errors} articles")
        print(f"📁 Output directory: {self.output_dir}")

        return processed, errors

def main():
    import sys

    extractor = Digital360Extractor()

    print("🚀 Digital360 Article Extractor")
    print("=" * 40)

    # For debugging: just show first 10 URLs
    print("🔍 Debug: First 10 URLs from sitemap:")
    urls = extractor.extract_urls_from_sitemap()
    for i, url in enumerate(urls[:10]):
        print(f"{i+1}. {url}")
    print(f"\n📊 Total URLs found: {len(urls)}")
    print("=" * 40)

    # Get limit from command line arguments
    limit = 5  # default
    if len(sys.argv) > 1:
        try:
            arg = sys.argv[1].lower()
            if arg == 'all':
                limit = len(urls)
            else:
                limit = int(arg)
        except ValueError:
            print(f"Invalid argument '{sys.argv[1]}', using default of 5 articles")
            limit = 5
    else:
        print("Usage: python3 extract-articles.py [number|all]")
        print("Processing with default limit of 5 articles...")

    print(f"📊 Processing limit: {limit} articles")

    # Process articles
    processed, errors = extractor.process_articles(limit=limit)

    if processed > 0:
        print(f"\n🎉 Successfully processed {processed} articles!")
        print("You can now run 'npm run dev' to see your blog with the new articles.")
        print("\nTo process all articles, run: python3 extract-articles.py all")
    else:
        print("\n❌ No articles were processed. Check the error messages above.")

if __name__ == "__main__":
    main()