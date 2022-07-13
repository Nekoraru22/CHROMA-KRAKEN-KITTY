from Chroma import *

def main():
    """
    {FB357780-4617-43A7-960F-D1190ED54806}
    static const GUID KRAKEN_KITTY=
    { 0xfb357780, 0x4617, 0x43a7,{ 0x96, 0xf, 0xd1, 0x19, 0xe, 0xd5, 0x48, 0x6 } };
    """

    driver = Driver("devid=FB357780-4617-43A7-960F-D1190ED54806") # Krakken kitty ID
    print(driver, end="\n\n")

    # Hexadecimal colors
    delay = 0.2
    for i in range(10):
        driver.change("FF0000")
        time.sleep(delay)
        driver.change("FFFF00")
        time.sleep(delay)
        driver.change("00FF00")
        time.sleep(delay)
        driver.change("00FFFF")
        time.sleep(delay)
        driver.change("000FFF")
        time.sleep(delay)
        driver.change("8700FF")
        time.sleep(delay)
        driver.change("FF00C1")
        time.sleep(delay)

    input(f"{YELLOW}[{WHITE}·{YELLOW}] Enter to close...")
    driver.remove()

if __name__ == "__main__":
    main()