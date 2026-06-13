import os
import random
import time
import winsound
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service

load_dotenv()

USER = os.getenv("PUSAK_USER")
PASS = os.getenv("PUSAK_PASS")
GECKO = os.getenv("GECKODRIVER_PATH")

maintenance_active = False
maintenance_cycles = 0
unknown_cycles = 0
server_down_cycles = 0
not_found_cycles = 0
stuck_cycles = 0
browser_restarts = 0
attempts = 0
last_log_time = 0.0
last_stats_time = 0.0
last_logged_message = ""
last_logged_state = None
start_time = time.time()

URL = "https://pusak.fomentoacademico.gob.ec/"


def beep_short():
    winsound.Beep(1000, 300)


def beep_success():
    for f in [800, 1000, 1300]:
        winsound.Beep(f, 250)


def beep_maintenance_over():
    for f in [600, 800, 1000, 1200]:
        winsound.Beep(f, 200)


def wait_random(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))


def log_status(message, page_state=None, force=False):
    global last_log_time, last_logged_message, last_logged_state
    now = time.time()
    if force or page_state != last_logged_state or message != last_logged_message or now - last_log_time >= 45:
        print(message)
        last_log_time = now
        last_logged_message = message
        last_logged_state = page_state


def print_stats(force=False):
    global last_stats_time
    now = time.time()
    if force or now - last_stats_time >= 60:
        elapsed = int(now - start_time)
        print(f"📈 Stats: tiempo={elapsed}s | intentos={attempts} | reinicios={browser_restarts} | mantenimiento={maintenance_cycles}")
        last_stats_time = now


def reset_state_counters():
    global unknown_cycles, server_down_cycles, not_found_cycles, stuck_cycles
    unknown_cycles = 0
    server_down_cycles = 0
    not_found_cycles = 0
    stuck_cycles = 0


def create_login_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=1100")
    options.add_argument("--height=800")

    service = Service(GECKO)

    return webdriver.Firefox(
        service=service,
        options=options
    )


def open_url(url):
    global driver
    try:
        driver.get(url)
        return True
    except Exception as exc:
        print(f"⚠️ Error cargando {url}: {exc}")
        return False


def restart_browser():
    global driver, browser_restarts, maintenance_active, maintenance_cycles, unknown_cycles, server_down_cycles, not_found_cycles, stuck_cycles, state
    browser_restarts += 1
    print("🔄 Reiniciando navegador por recuperación automática...")

    try:
        if driver is not None:
            driver.quit()
    except Exception as exc:
        print(f"⚠️ Error cerrando Firefox: {exc}")

    try:
        driver = create_login_driver()
        if not open_url(URL):
            return False
    except Exception as exc:
        print(f"⚠️ Error creando Firefox: {exc}")
        return False

    maintenance_active = False
    maintenance_cycles = 0
    unknown_cycles = 0
    server_down_cycles = 0
    not_found_cycles = 0
    stuck_cycles = 0
    state = "WAIT_LOGIN"
    print("✅ Navegador reiniciado y listo.")
    return True


def get_page_state(driver):
    try:
        current = driver.current_url.lower()
    except Exception as exc:
        current = ""
        print(f"⚠️ Error leyendo URL: {exc}")

    try:
        source = driver.page_source.lower()
    except Exception as exc:
        source = ""
        print(f"⚠️ Error leyendo fuente: {exc}")

    try:
        title = driver.title.lower()
    except Exception:
        title = ""

    if (
        "sitio en mantenimiento" in source
        or "estamos realizando mejoras" in source
        or "volveremos pronto" in source
        or "mantenimiento" in title
        or "mejoras" in title
        or "volveremos pronto" in title
    ):
        return "MAINTENANCE"

    if (
        "service temporarily unavailable" in source
        or "apache/2.2.15" in source
        or "service temporarily unavailable" in title
    ):
        return "SERVER_DOWN"

    if "not found" in source or "404" in title:
        return "NOT_FOUND"

    try:
        driver.find_element(By.ID, "username")
        return "LOGIN_PAGE"
    except Exception:
        pass

    app_assets = "/apps" in current or "/apps/" in source or "/apps" in source
    looks_like_app = (
        "service temporarily unavailable" not in source
        and "not found" not in source
        and "sitio en mantenimiento" not in source
        and title.strip()
        and (
            app_assets
            or any(token in source for token in ["dashboard", "home", "logout", "usuario", "menú de servicios"])
        )
    )

    if looks_like_app:
        return "POSSIBLE_APP"

    return "UNKNOWN"


driver = create_login_driver()
if not open_url(URL):
    raise RuntimeError("No se pudo abrir la URL inicial")

state = "WAIT_LOGIN"
print("🔎 Monitor iniciado...")
print_stats(force=True)

try:
    while True:
        attempts += 1
        print_stats()

        try:
            page = get_page_state(driver)
        except Exception as exc:
            print(f"⚠️ Error consultando estado: {exc}")
            page = "UNKNOWN"

        if state == "WAIT_LOGIN":
            if page == "MAINTENANCE":
                if not maintenance_active:
                    log_status("🛠️ Entró mantenimiento.", page, force=True)
                    beep_short()
                    maintenance_active = True

                maintenance_cycles += 1
                if maintenance_cycles >= 10:
                    log_status("🔄 Reinicio automático por mantenimiento prolongado.", page, force=True)
                    if not restart_browser():
                        break
                    continue

                wait_random(25, 35)
                open_url(URL)
                continue

            if page == "SERVER_DOWN":
                server_down_cycles += 1
                if server_down_cycles >= 8:
                    log_status("🔄 Reinicio automático por servidor caído repetido.", page, force=True)
                    if not restart_browser():
                        break
                    continue

                log_status("⚠️ Servidor no disponible.", page)
                wait_random(4, 7)
                open_url(URL)
                continue

            if page == "NOT_FOUND":
                not_found_cycles += 1
                if not_found_cycles >= 8:
                    log_status("🔄 Reinicio automático por errores 404 repetidos.", page, force=True)
                    if not restart_browser():
                        break
                    continue

                log_status("⚠️ Ruta inválida.", page)
                wait_random(4, 7)
                open_url(URL)
                continue

            if page == "UNKNOWN":
                unknown_cycles += 1
                stuck_cycles += 1
                if unknown_cycles >= 8 or stuck_cycles >= 20:
                    log_status("🔄 Reinicio automático por estado anómalo prolongado.", page, force=True)
                    if not restart_browser():
                        break
                    continue

                log_status("❓ Estado desconocido.", page)
                wait_random(2, 4)
                open_url(URL)
                continue

            if maintenance_active:
                log_status("🎉 EL MANTENIMIENTO TERMINÓ", page, force=True)
                beep_maintenance_over()
                maintenance_active = False
                maintenance_cycles = 0
                reset_state_counters()

            if page == "LOGIN_PAGE":
                log_status("⚡ LOGIN DETECTADO", page, force=True)
                beep_short()
                try:
                    user = driver.find_element(By.ID, "username")
                    pwd = driver.find_element(By.ID, "password")

                    user.clear()
                    user.send_keys(USER)

                    pwd.clear()
                    pwd.send_keys(PASS)
                    pwd.send_keys(Keys.ENTER)

                    log_status("🚀 Login enviado", page, force=True)
                    reset_state_counters()
                    state = "WAIT_APPS"

                except Exception as exc:
                    log_status(f"⚠️ Error enviando login: {exc}", page, force=True)
                    wait_random(2, 4)
                    open_url(URL)

                continue

        elif state == "WAIT_APPS":
            wait_random(1.5, 2.5)

            try:
                page = get_page_state(driver)
            except Exception as exc:
                print(f"⚠️ Error consultando estado: {exc}")
                page = "UNKNOWN"

            if page == "MAINTENANCE":
                log_status("🛠️ Entró mantenimiento.", page, force=True)
                maintenance_cycles += 1
                if maintenance_cycles >= 10:
                    log_status("🔄 Reinicio automático por mantenimiento prolongado.", page, force=True)
                    if not restart_browser():
                        break
                    state = "WAIT_LOGIN"
                    continue

                open_url(URL)
                state = "WAIT_LOGIN"
                continue

            if page == "SERVER_DOWN":
                server_down_cycles += 1
                if server_down_cycles >= 8:
                    log_status("🔄 Reinicio automático por servidor caído repetido.", page, force=True)
                    if not restart_browser():
                        break
                    state = "WAIT_LOGIN"
                    continue

                log_status("⚠️ Backend caído.", page)
                wait_random(4, 7)
                open_url(URL)
                state = "WAIT_LOGIN"
                continue

            if page == "NOT_FOUND":
                not_found_cycles += 1
                if not_found_cycles >= 8:
                    log_status("🔄 Reinicio automático por errores 404 repetidos.", page, force=True)
                    if not restart_browser():
                        break
                    state = "WAIT_LOGIN"
                    continue

                log_status("⚠️ Página inválida.", page)
                open_url(URL)
                state = "WAIT_LOGIN"
                continue

            if page == "LOGIN_PAGE":
                log_status("🔁 Volvió al login.", page, force=True)
                state = "WAIT_LOGIN"
                continue

            if page == "UNKNOWN":
                unknown_cycles += 1
                stuck_cycles += 1
                if unknown_cycles >= 8 or stuck_cycles >= 20:
                    log_status("🔄 Reinicio automático por estado anómalo prolongado.", page, force=True)
                    if not restart_browser():
                        break
                    state = "WAIT_LOGIN"
                    continue

                log_status("⏳ Esperando aplicación...", page)
                continue

            if page == "POSSIBLE_APP":
                beep_success()
                log_status("✅ POSIBLE APP DETECTADA", page, force=True)
                print("🎉 Ya puedes usar PUSAK.")
                input("\nPresiona ENTER cuando quieras cerrar Firefox...")
                break

            log_status("⏳ Esperando aplicación...", page)

except KeyboardInterrupt:
    print("\n🛑 Detenido por usuario.")

finally:
    print("🧹 Cerrando Firefox...")
    try:
        driver.quit()
    except Exception as exc:
        print(f"⚠️ Error cerrando Firefox: {exc}")