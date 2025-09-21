import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------- Bot Token ----------------
# Example token (replace with real token for your bot)
TELEGRAM_BOT_TOKEN = "8316425707:AAF6AdFvaFtzagGEkDJGkNLOOBL3KhS6mS4"

# ---------------- Flipkart API Config ----------------
FLIPKART_AFFILIATE_ID = "YOUR_FLIPKART_ID"
FLIPKART_AFFILIATE_TOKEN = "YOUR_FLIPKART_TOKEN"

# ---------------- Flipkart API Function ----------------
def get_flipkart_price(product_name: str):
    headers = {
        "Fk-Affiliate-Id": FLIPKART_AFFILIATE_ID,
        "Fk-Affiliate-Token": FLIPKART_AFFILIATE_TOKEN,
    }
    url = f"https://affiliate-api.flipkart.net/affiliate/1.0/search.json?query={product_name}&resultCount=1"
    
    try:
        response = requests.get(url, headers=headers).json()
        product = response["products"][0]["productBaseInfoV1"]

        return {
            "site": "Flipkart",
            "title": product["title"],
            "price": product["flipkartSellingPrice"]["amount"],
            "mrp": product["maximumRetailPrice"]["amount"],
            "link": product["productUrl"]
        }
    except Exception:
        return None

# ---------------- Compare Function ----------------
def get_best_deal(product_name: str) -> str:
    results = []

    flipkart = get_flipkart_price(product_name)
    if flipkart: results.append(flipkart)

    if not results:
        return f"❌ No results found for '{product_name}'."

    # Find lowest price & highest discount
    lowest = min(results, key=lambda x: x["price"])
    highest_discount = max(results, key=lambda x: (x["mrp"] - x["price"]) / x["mrp"])

    discount_percent = round(((highest_discount["mrp"] - highest_discount["price"]) / highest_discount["mrp"]) * 100, 2)

    return (f"📱 {product_name.title()}\n\n"
            f"💰 Lowest Price: ₹{lowest['price']} ({lowest['site']})\n"
            f"🔗 {lowest['link']}\n\n"
            f"🔥 Highest Discount: {discount_percent}% ({highest_discount['site']})\n"
            f"🔗 {highest_discount['link']}")

# ---------------- Telegram Bot ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Send /deal <product_name> to find the best price.\n"
        "Example: /deal iPhone 14"
    )

async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Please provide a product name. Example: /deal iPhone 14")
        return
    
    product_name = " ".join(context.args)
    result = get_best_deal(product_name)
    await update.message.reply_text(result)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deal", deal))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
