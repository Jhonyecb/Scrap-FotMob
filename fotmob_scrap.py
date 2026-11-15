#%%
import csv
import re
import time
from selenium import webdriver  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unicodedata

# ==================== CONFIGURAÇÃO ====================
ID_JOGADOR = 263937
NOME_JOGADOR = "everton-ribeiro"
NOME_ARQUIVO = "csv/everton-ribeiro.csv"
COMPETICAO = "Brasileiro Série A 2025"
COMPETICAO_SITE = "Serie A"
TEMPORADA = "2025"

URL = f"https://www.fotmob.com/players/{ID_JOGADOR}/{NOME_JOGADOR}"
# =======================================================


EXTRAIR_JS = """
const nome = document.querySelector('h1')?.innerText?.trim() ?? null;
const sub = document.querySelector("[class*='SeasonPerformanceSubtitle']");
const textos = sub ? [...sub.querySelectorAll('span')].map(s => s.innerText.trim()) : [];
const numeros = textos.filter(t => /^\\d{1,3}(,\\d{3})*$/.test(t));
const minutos = numeros.length ? numeros[numeros.length - 1] : null;
return { nome, minutos };
"""

def criar_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=opts)



def _normalizar(texto):
    """Remove NBSP, acentos e espaços extras, e deixa tudo em minúsculas."""
    texto = (texto or "").replace("\xa0", " ")
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", texto).strip().lower()

def selecionar_temporada(driver, ano, competicao):
    """Procura em todos os <select> da página a opção dentro do grupo do ano."""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "select"))
        )
    except TimeoutException:
        print("Nenhum <select> encontrado na página.")
        return False

    seletores = driver.find_elements(By.TAG_NAME, "select")
    alvo_ano, alvo_comp = _normalizar(ano), _normalizar(competicao)

    seletor, opcao = None, None
    for s in seletores:
        for og in s.find_elements(By.TAG_NAME, "optgroup"):
            if _normalizar(og.get_attribute("label")) != alvo_ano:
                continue
            for op in og.find_elements(By.TAG_NAME, "option"):
                if _normalizar(op.get_attribute("textContent")) == alvo_comp:
                    seletor, opcao = s, op
                    break
            if opcao:
                break
        if opcao:
            break

    if opcao is None:
        print(f"'{competicao}' do ano {ano} não encontrado.")
        print(f"Selects na página: {len(seletores)}")
        for s in seletores:
            print("aria-label:", s.get_attribute("aria-label"))
            for og in s.find_elements(By.TAG_NAME, "optgroup"):
                nomes = [o.get_attribute("textContent") for o in og.find_elements(By.TAG_NAME, "option")]
                print("  ", og.get_attribute("label"), nomes)
        return False

    Select(seletor).select_by_value(opcao.get_attribute("value"))
    time.sleep(2)
    print("Temporada selecionada:", opcao.get_attribute("textContent").strip(), "| grupo:", ano)
    return True

def ativar_per_90(driver):
    botao = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "(//*[normalize-space()='Per 90'])[last()]"))
    )
    botao.click()
    time.sleep(1.5)

def ler_percentil(driver, wrapper):
    # Move o mouse para fora e depois para a barra, para evitar ler um tooltip antigo
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", wrapper)
    ActionChains(driver).move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    time.sleep(0.2)
    ActionChains(driver).move_to_element(wrapper).perform()
    try:
        tip = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='tooltip']"))
        )
        texto = tip.text
    except TimeoutException:
        return None, ""
    m = re.search(r"\d+(?:[.,]\d+)?", texto)
    valor = float(m.group(0).replace(",", ".")) if m else None
    return valor, texto

def extrair_stats(driver):
    stats = []
    grupo = None
    elementos = driver.find_elements(
        By.CSS_SELECTOR, "[class*='StatGroupTitle'], [class*='StatItemCSS']"
    )
    for el in elementos:
        if "StatGroupTitle" in el.get_attribute("class"):
            grupo = el.text.strip()
            continue
        stat = el.find_element(By.CSS_SELECTOR, "[class*='StatTitle']").text.strip()
        valor = el.find_element(By.CSS_SELECTOR, "[class*='StatValue']").text.strip()
        wrapper = el.find_element(By.CSS_SELECTOR, "[class*='StatPercentileWrapper']")
        percentil, texto = ler_percentil(driver, wrapper)
        print(f"{stat:30} {valor:>8} -> {percentil} | tooltip: {texto!r}")
        stats.append({"grupo": grupo, "stat": stat, "valor": valor, "percentil": percentil})
    return stats

def scrape(url):
    driver = criar_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='StatItemCSS']"))
        )
        if not selecionar_temporada(driver, TEMPORADA, COMPETICAO_SITE):
            raise RuntimeError("Temporada não selecionada. Veja a saída acima.")
        ativar_per_90(driver)
        dados = driver.execute_script(EXTRAIR_JS)
        dados["stats"] = extrair_stats(driver)
    finally:
        driver.quit()
    return dados

def salvar_csv(dados, caminho=NOME_ARQUIVO):
    minutos = int(dados["minutos"].replace(",", "")) if dados["minutos"] else None
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["atleta", "competicao", "minutos", "grupo", "stat", "valor", "percentil"])
        for s in dados["stats"]:
            w.writerow([dados["nome"], COMPETICAO, minutos,
                        s["grupo"], s["stat"], s["valor"], s["percentil"]])

if __name__ == "__main__":
    dados = scrape(URL)
    salvar_csv(dados)
    print(f"{dados['nome']}: {len(dados['stats'])} stats extraídas")
# %%