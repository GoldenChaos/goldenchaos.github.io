// Sends a OneSignal push notification for the latest comic
// Requires repo secrets: ONESIGNAL_APP_ID, ONESIGNAL_REST_API_KEY
// Optional: derives base URL from CNAME, else falls back to GitHub Pages URL

const fs = require('fs');
const path = require('path');

async function main() {
  const appId = process.env.ONESIGNAL_APP_ID;
  const apiKey = process.env.ONESIGNAL_REST_API_KEY;

  if (!appId || !apiKey) {
    console.error('Missing ONESIGNAL_APP_ID or ONESIGNAL_REST_API_KEY env vars.');
    process.exit(1);
  }

  const comicsPath = path.join(__dirname, '..', 'src', '_data', 'comics.json');
  const cnamePath = path.join(__dirname, '..', 'CNAME');

  if (!fs.existsSync(comicsPath)) {
    console.error('comics.json not found at', comicsPath);
    process.exit(1);
  }

  const comics = JSON.parse(fs.readFileSync(comicsPath, 'utf-8'));
  if (!Array.isArray(comics) || comics.length === 0) {
    console.error('comics.json is empty or invalid');
    process.exit(1);
  }

  const latest = comics[comics.length - 1];
  const slug = latest.slug || String(latest.number);
  let baseUrl = 'https://goldenchaos.github.io';
  if (fs.existsSync(cnamePath)) {
    const domain = fs.readFileSync(cnamePath, 'utf-8').trim();
    if (domain) baseUrl = `https://${domain}`;
  }
  const url = `${baseUrl}/comics/${slug}/`;

  // Use TEST_PLAYER_ID for testing, otherwise broadcast to all subscribers
  const testPlayerId = process.env.TEST_PLAYER_ID;
  
  const payload = {
    app_id: appId,
    ...(testPlayerId 
      ? { include_player_ids: [testPlayerId] }
      : { included_segments: ['Subscribed Users'] }
    ),
    headings: { en: 'New comic!' },
    contents: { en: `#${latest.number} - ${latest.title || 'Untitled'}` },
    url
  };

  console.log('Sending OneSignal notification:', {
    title: payload.headings.en,
    content: payload.contents.en,
    url
  });

  const res = await fetch('https://api.onesignal.com/notifications', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${apiKey}`
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    const text = await res.text();
    console.error('OneSignal API error:', res.status, text);
    process.exit(1);
  }

  const json = await res.json();
  console.log('OneSignal response:', json);
}

main().catch(err => {
  console.error('Notify latest comic failed:', err);
  process.exit(1);
});
