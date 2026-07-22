// Bridge WhatsApp <-> Orchestrator (FastAPI en :8000)
// Escanea QR con el celular y reenvía mensajes por POST /webhook.
const { Client, LocalAuth } = require("whatsapp-web.js");
const axios = require("axios");

const PORT = process.env.PORT || 8000;
const ORCH_URL = `http://localhost:${PORT}/webhook`;

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./session" }),
  puppeteer: { headless: true, args: ["--no-sandbox", "--disable-setuid-sandbox"] },
});

client.on("qr", (qr) => console.log("Escanea este QR con tu WhatsApp:\n" + qr));
client.on("ready", () => console.log("✅ Bridge WhatsApp listo."));

client.on("message", async (msg) => {
  // Ignora grupos y mensajes propios
  if (msg.from.endsWith("@g.us") || msg.fromMe) return;
  try {
    const { data } = await axios.post(ORCH_URL, {
      from: msg.from,
      name: msg._data?.notifyName || msg.from,
      body: msg.body,
      message_id: msg.id._serialized,
    });
    if (data.reply) await msg.reply(data.reply);
  } catch (err) {
    console.error("❌ Error hablando con el orchestrator:", err.message);
    await msg.reply("Lo siento, tuve un error interno. Intenta de nuevo.");
  }
});

client.initialize();
