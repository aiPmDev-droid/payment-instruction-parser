const { chromium } = require('playwright');
const path = require('path');

const FRAMES_DIR = path.join(__dirname, 'frames');
const SAMPLE_FILE = path.join(__dirname, '..', 'tests', 'fixtures', 'emails', 'sample_02.txt');
const BASE_URL = 'http://localhost:3000';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  // Frame 1: Landing page
  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(FRAMES_DIR, '01-landing.png') });

  // Frame 2: File selected
  const fileInput = page.locator('input[type="file"]');
  await fileInput.setInputFiles(SAMPLE_FILE);
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(FRAMES_DIR, '02-file-selected.png') });

  // Frame 3: Click Extract button
  const extractBtn = page.locator('button.primary-button');
  await extractBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(FRAMES_DIR, '03-loading.png') });

  // Frame 4: Extraction results loaded
  await page.waitForTimeout(5000); // Wait for Gemini API to respond
  await page.waitForSelector('.payment-card', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(FRAMES_DIR, '04-results.png') });

  // Frame 5: Scroll to history section
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(FRAMES_DIR, '05-history.png') });

  await browser.close();
  console.log('Demo frames captured successfully.');
})();