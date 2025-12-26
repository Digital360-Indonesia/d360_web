<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
	xmlns:xhtml="http://www.w3.org/1999/xhtml">
<xsl:output method="html" indent="yes"/>

<xsl:template match="/">
	<html lang="en">
	<head>
		<meta charset="UTF-8"/>
		<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
		<title>Sitemap - Digital360</title>
		<style>
			:root {
				--bg: #0a0a0a;
				--surface: #18181b;
				--border: #27272a;
				--text: #fafafa;
				--text-muted: #a1a1aa;
				--accent: #e4e4e7;
				--accent-bg: #27272a;
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
				max-width: 900px;
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

			.stats {
				display: flex;
				gap: 2rem;
				justify-content: center;
				margin-top: 1rem;
				flex-wrap: wrap;
			}

			.stat {
				background: var(--surface);
				padding: 0.5rem 1rem;
				border-radius: 6px;
				font-size: 0.875rem;
				border: 1px solid var(--border);
			}

			.stat-label {
				color: var(--text-muted);
				font-size: 0.75rem;
				text-transform: uppercase;
				letter-spacing: 0.05em;
			}

			.stat-value {
				font-weight: 600;
				color: var(--accent);
			}

			.url-list {
				display: flex;
				flex-direction: column;
				gap: 0.75rem;
			}

			.url-item {
				background: var(--surface);
				border: 1px solid var(--border);
				border-radius: 8px;
				padding: 1rem 1.25rem;
				transition: border-color 0.2s ease;
			}

			.url-item:hover {
				border-color: var(--accent);
			}

			.url-loc {
				font-size: 1rem;
				font-weight: 500;
				margin-bottom: 0.5rem;
			}

			.url-loc a {
				color: var(--accent);
				text-decoration: none;
			}

			.url-loc a:hover {
				text-decoration: underline;
			}

			.url-meta {
				display: flex;
				gap: 1.5rem;
				flex-wrap: wrap;
				font-size: 0.8125rem;
			}

			.meta-item {
				display: flex;
				align-items: center;
				gap: 0.375rem;
			}

			.meta-label {
				color: var(--text-muted);
			}

			.meta-value {
				color: var(--text-muted);
			}

			.priority-high {
				color: #22c55e;
			}

			.priority-medium {
				color: #eab308;
			}

			.priority-low {
				color: #6b7280;
			}

			.lang-badge {
				display: inline-block;
				padding: 0.125rem 0.5rem;
				background: var(--accent-bg);
				border-radius: 4px;
				font-size: 0.75rem;
				font-weight: 500;
				margin-left: 0.5rem;
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

				.stats {
					flex-direction: column;
					gap: 0.75rem;
				}

				.url-meta {
					flex-direction: column;
					gap: 0.5rem;
				}
			}
		</style>
	</head>
	<body>
		<div class="container">
			<header>
				<h1>Sitemap</h1>
				<p class="subtitle">digital360.id — XML Sitemap</p>
				<div class="stats">
					<div class="stat">
						<div class="stat-label">Total URLs</div>
						<div class="stat-value"><xsl:value-of select="count(//sitemap:url)"/></div>
					</div>
					<div class="stat">
						<div class="stat-label">Languages</div>
						<div class="stat-value">EN, ID</div>
					</div>
				</div>
			</header>

			<main class="url-list">
				<xsl:for-each select="//sitemap:url">
					<xsl:sort select="sitemap:priority" order="descending"/>
					<xsl:sort select="sitemap:loc"/>
					<article class="url-item">
						<div class="url-loc">
							<a>
								<xsl:attribute name="href">
									<xsl:value-of select="sitemap:loc"/>
								</xsl:attribute>
								<xsl:value-of select="sitemap:loc"/>
							</a>
							<xsl:if test="contains(sitemap:loc, '/blog/')">
								<span class="lang-badge">ID</span>
							</xsl:if>
							<xsl:if test="contains(sitemap:loc, '/customer-stories/')">
								<span class="lang-badge">EN/ID</span>
							</xsl:if>
						</div>
						<div class="url-meta">
							<div class="meta-item">
								<span class="meta-label">Priority:</span>
								<span class="meta-value">
									<xsl:attribute name="class">
										meta-value
										<xsl:choose>
											<xsl:when test="sitemap:priority &gt;= 0.8"> priority-high</xsl:when>
											<xsl:when test="sitemap:priority &gt;= 0.5"> priority-medium</xsl:when>
											<xsl:otherwise> priority-low</xsl:otherwise>
										</xsl:choose>
									</xsl:attribute>
									<xsl:value-of select="sitemap:priority"/>
								</span>
							</div>
							<div class="meta-item">
								<span class="meta-label">Updated:</span>
								<span class="meta-value"><xsl:value-of select="sitemap:lastmod"/></span>
							</div>
							<div class="meta-item">
								<span class="meta-label">Change freq:</span>
								<span class="meta-value"><xsl:value-of select="sitemap:changefreq"/></span>
							</div>
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
