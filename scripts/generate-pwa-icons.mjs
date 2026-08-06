/**
 * PWA 아이콘 생성기
 *
 * assets/favicon.svg 의 파랑→초록 그라데이션 + 'r' 정체성을 유지한 채
 * 홈화면 설치에 필요한 PNG 아이콘들을 만들어 assets/icons/ 에 넣는다.
 *
 * 생성물은 저장소에 커밋되므로 평소에는 실행할 필요가 없다.
 * 아이콘 디자인을 바꿀 때만 다시 돌리면 된다.
 *
 *   node scripts/generate-pwa-icons.mjs
 *
 * 필요 조건: playwright (Chromium 으로 SVG 를 PNG 로 렌더링한다)
 *   npx playwright install chromium
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, '../assets/icons');

const GRADIENT = `
  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#4285f4" />
    <stop offset="100%" style="stop-color:#34a853" />
  </linearGradient>`;

/**
 * @param {object} opts
 * @param {number} opts.radius   모서리 둥글기 (0~50, viewBox 100 기준)
 * @param {number} opts.fontSize 글자 크기 (viewBox 100 기준)
 */
function iconSvg({ radius, fontSize }) {
  // 글자를 세로 중앙에 놓기 위한 baseline 보정 (대략 글자 높이의 35%)
  const baseline = 50 + fontSize * 0.35;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>${GRADIENT}</defs>
  <rect width="100" height="100" rx="${radius}" fill="url(#grad)"/>
  <text x="50" y="${baseline}" font-family="Arial, Helvetica, sans-serif" font-size="${fontSize}"
        font-weight="bold" fill="white" text-anchor="middle">r</text>
</svg>`;
}

const ICONS = [
  // 일반 아이콘: favicon 과 같은 둥근 사각형
  { file: 'icon-192.png', size: 192, svg: iconSvg({ radius: 20, fontSize: 60 }) },
  { file: 'icon-512.png', size: 512, svg: iconSvg({ radius: 20, fontSize: 60 }) },

  // maskable: 런처가 원/스퀘어클로 잘라내므로 모서리를 직접 둥글리지 않고
  // 배경을 꽉 채운다. 글자는 안전영역(가운데 80%) 안에 들어오도록 축소한다.
  { file: 'icon-maskable-512.png', size: 512, svg: iconSvg({ radius: 0, fontSize: 46 }) },

  // iOS 는 자체적으로 모서리를 둥글리므로 꽉 찬 사각형을 준다.
  { file: 'apple-touch-icon.png', size: 180, svg: iconSvg({ radius: 0, fontSize: 60 }) },
];

const { chromium } = await import('playwright');
const browser = await chromium.launch();

await mkdir(OUT_DIR, { recursive: true });

for (const { file, size, svg } of ICONS) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  await page.setContent(
    `<style>html,body{margin:0;padding:0}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`
  );
  const buf = await page.locator('svg').screenshot({ omitBackground: true });
  await writeFile(resolve(OUT_DIR, file), buf);
  await page.close();
  console.log(`생성: assets/icons/${file} (${size}x${size})`);
}

await browser.close();
console.log('\n완료.');
