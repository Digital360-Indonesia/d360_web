<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9">
<xsl:output method="html" indent="yes"/>

<xsl:template match="/">
	<html lang="en">
	<head>
		<meta charset="UTF-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
		<title>Sitemap Index - Digital360</title>
		<style>
			:root {
				--bg: #0a0a0a;
				--surface: #18181b;
				--border: #27272a;
				--text: #fafafa;
				--text-muted: #a1a1aa;
				--accent: #e4e4e7;
			}

			* {
				margin: 0;
				padding: 0;
				box-sizing: border-box;
			}

			body {
				font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
				background: var(--bg);
				color: var(--text);
				line-height: 1.6;
				padding: 2rem 1rem;
			}

			.container {
				max-width: 700px;
				margin: 0 auto;
			}

			header {
				text-align: center;
				margin-bottom: 3rem;
				padding-bottom: 2rem;
				border-bottom: 1px solid var(--border);
			}

			h1 {
				font-size: 2rem;
				font-weight: 600;
				margin-bottom: 0.5rem;
			}

			.subtitle {
				color: var(--text-muted);
				font-size: 0.9375rem;
			}

			.sitemap-list {
				display: flex;
				flex-direction: column;
				gap: 0.75rem;
			}

			.sitemap-item {
				background: var(--surface);
				border: 1px solid var(--border);
				border-radius: 8px;
				padding: 1rem 1.25rem;
				transition: border-color 0.2s ease;
			}

			.sitemap-item:hover {
				border-color: var(--accent);
			}

			.sitemap-name {
				font-weight: 500;
				margin-bottom: 0.25rem;
			}

			.sitemap-name a {
				color: var(--accent);
				text-decoration: none;
			}

			.sitemap-name a:hover {
				text-decoration: underline;
			}

			.sitemap-meta {
				font-size: 0.8125rem;
				color: var(--text-muted);
			}

			footer {
				text-align: center;
				margin-top: 3rem;
				padding-top: 2rem;
				border-top: 1px solid var(--border);
				color: var(--text-muted);
				font-size: 0.875rem;
			}

			footer a {
				color: var(--accent);
				text-decoration: none;
			}

			@media (max-width: 640px) {
				h1 {
					font-size: 1.5rem;
				}
			}
		</style>
	</head>
	<body>
		<div class="container">
			<header>
				<h1>Sitemap Index</h1>
				<p class="subtitle">digital360.id — XML Sitemap Index</p>
			</header>

			<main class="sitemap-list">
				<xsl:for-each select="//sitemap:sitemap">
					<article class="sitemap-item">
						<div class="sitemap-name">
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="sitemap:loc"/>
								</xsl:attribute>
								<xsl:choose>
									<xsl:when test="contains(sitemap:loc, 'pages')">
										📄 Pages Sitemap
									</xsl:when>
									<xsl:when test="contains(sitemap:loc, 'blog')">
										📝 Blog Sitemap
									</xsl:when>
									<xsl:when test="contains(sitemap:loc, 'customer-stories')">
										🏢 Customer Stories Sitemap
									</xsl:when>
									<xsl:otherwise>
										<xsl:value-of select="sitemap:loc"/>
									</xsl:otherwise>
								</xsl:choose>
							</a>
						</div>
						<div class="sitemap-meta">
							Last updated: <xsl:value-of select="sitemap:lastmod"/>
						</div>
					</article>
				</xsl:for-each>
			</main>

			<footer>
				<p><a href="/">← Back to digital360.id</a></p>
			</footer>
		</div>
	</body>
	</html>
</xsl:template>

</xsl:stylesheet>
