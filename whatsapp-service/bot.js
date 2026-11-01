const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');

const app = express();
app.use(express.json());

const INVITE_LINK = "https://chat.whatsapp.com/my-invite-link";

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ]
    }
});

let isReady = false;

client.on('qr', (qr) => {
    console.log('\n--------------------------------------------------');
    console.log('SCAN THIS QR CODE WITH YOUR WHATSAPP PHONE:');
    qrcode.generate(qr, { small: true });
    console.log('--------------------------------------------------\n');
});

client.on('ready', () => {
    console.log('\n==================================================');
    console.log('WhatsApp Engine is connected and ready!');
    console.log('==================================================\n');
    isReady = true;
});

app.post('/add-member', async (req, res) => {
    const { phoneNumber } = req.body;
    console.log(`\n[API REQUEST] Processing phone: ${phoneNumber}`);

    if (!isReady) {
        return res.status(503).json({ error: 'WhatsApp engine is still starting up.' });
    }

    const cleanPhone = phoneNumber.replace(/[^0-9]/g, '');
    const participantId = `${cleanPhone}@c.us`;

    try {
        console.log(`[ACTION] Bypassing group sync. Sending DM invite directly...`);
        
        await client.sendMessage(
            participantId,
            `Hello! Your student verification for NSUT onboarding is successful.\n\nClick the link below to join your official college group:\n${INVITE_LINK}`
        );

        console.log(`[SUCCESS] Sent DM invite link to ${cleanPhone}`);
        return res.json({ status: 'dm_fallback_sent' });

    } catch (error) {
        console.error(`[ERROR] System fault:`, error.message || error);
        return res.status(500).json({ error: 'Internal WhatsApp error' });
    }
});
client.initialize();
app.listen(3000, () => console.log('WhatsApp Microservice listening on port 3000'));