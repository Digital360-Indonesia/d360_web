import sharp from 'sharp';
import { readdir, stat } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SOURCE_DIR = join(__dirname, '../public/assets/images');
const QUALITY = 85;

// Supported formats
const SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.gif'];

async function getFiles(dir) {
  const files = await readdir(dir, { withFileTypes: true });
  const results = [];

  for (const file of files) {
    if (file.isDirectory()) {
      const subPath = join(dir, file.name);
      const subFiles = await getFiles(subPath);
      results.push(...subFiles);
    } else if (file.isFile()) {
      const ext = file.name.toLowerCase();
      if (SUPPORTED_FORMATS.some(format => ext.endsWith(format))) {
        results.push(join(dir, file.name));
      }
    }
  }

  return results;
}

async function convertToWebP(inputPath) {
  const webpPath = inputPath.replace(/\.(png|jpg|jpeg|gif)$/i, '.webp');

  try {
    await sharp(inputPath)
      .webp({ quality: QUALITY })
      .toFile(webpPath);
    console.log(`✅ Created: ${webpPath}`);
    return true;
  } catch (error) {
    console.error(`❌ Error converting ${inputPath}:`, error.message);
    return false;
  }
}

async function convertToAVIF(inputPath) {
  const avifPath = inputPath.replace(/\.(png|jpg|jpeg|gif)$/i, '.avif');

  try {
    await sharp(inputPath)
      .avif({ quality: QUALITY, effort: 4 })
      .toFile(avifPath);
    console.log(`✅ Created: ${avifPath}`);
    return true;
  } catch (error) {
    console.error(`❌ Error converting ${inputPath}:`, error.message);
    return false;
  }
}

async function main() {
  console.log('🚀 Starting image optimization...\n');
  console.log(`📁 Source directory: ${SOURCE_DIR}\n`);

  const files = await getFiles(SOURCE_DIR);
  console.log(`📊 Found ${files.length} images to convert\n`);

  let webpCount = 0;
  let avifCount = 0;

  for (const file of files) {
    console.log(`\n🔄 Processing: ${file}`);

    // Convert to WebP
    const webpSuccess = await convertToWebP(file);
    if (webpSuccess) webpCount++;

    // Convert to AVIF (optional - slower but better compression)
    // Uncomment to enable AVIF conversion
    // const avifSuccess = await convertToAVIF(file);
    // if (avifSuccess) avifCount++;
  }

  console.log('\n' + '='.repeat(50));
  console.log('✨ Optimization complete!');
  console.log(`📈 WebP images created: ${webpCount}`);
  console.log(`📈 AVIF images created: ${avifCount}`);
  console.log('='.repeat(50));
}

main().catch(console.error);
