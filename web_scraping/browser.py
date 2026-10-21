from playwright.async_api import async_playwright
import asyncio
import os
import json
import base64

async def scrape_url(i, url, navigator, semaphore):
    async with semaphore:

        print(f"Je commence {url}")
        os.makedirs(f"output/url_{i}", exist_ok=True)

        context = await navigator.new_context()
        page = await context.new_page()

        # recupere les sources etape2
        # faire avant etape1 pour recuperer des le chargement
        resources = []

        def collect_request(request):
            resources.append(request.url)

        page.on("request", collect_request)

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        # prends une capture d'ecran etape3
        screenshot = await page.screenshot(path=f"output/url_{i}/screenshot.png")
        # encode la photo (screenshot est en binaire, image en photo)
        img_in_str = base64.b64encode(screenshot).decode("utf-8")

        # recupere l'html etape1
        html = await page.content()

        # cree la data du fichier json
        data = {
            "html": html,
            "resources": resources,
            "screenshot": img_in_str
        }

        # cree le fichier json
        with open(f"output/url_{i}/browse.json", "w", encoding="utf-8") as file:
            json.dump(data, file)

        print(url, ":", len(resources), "ressources")
        print(resources[:5])
        await context.close()




async def main():

    # ouvrir un "compte" sur chrome
    play = await async_playwright().start()
    navigator = await play.chromium.launch(headless=False)

    # mettre tous les liens du fichier dans une liste
    with open("input/urls.input", "r") as file:
        content = file.readlines()
    urls = []
    for line in content:
        line = line.strip()
        if (line != ""):
            urls.append(line)

    semaphore = asyncio.Semaphore(5)

    # pour chaque lien faire les etapes
    tasks = []
    for i, url in enumerate(urls, start=1):
        tasks.append(scrape_url(i, url, navigator, semaphore))
    await asyncio.gather(*tasks)

    await navigator.close()
    await play.stop()


asyncio.run(main())
