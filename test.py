from Chroma import *
from LoL import *

def main():
    """
    {FB357780-4617-43A7-960F-D1190ED54806}
    static const GUID KRAKEN_KITTY=
    { 0xfb357780, 0x4617, 0x43a7,{ 0x96, 0xf, 0xd1, 0x19, 0xe, 0xd5, 0x48, 0x6 } };

    All devices: https://assets.razerzone.com/dev_portal/REST/html/_rz_chroma_s_d_k_defines_8h_source.html
    """

    driver = Driver("devid=FB357780-4617-43A7-960F-D1190ED54806") # Krakken kitty ID
    game = Partida(driver)

    print(driver, end="\n\n")
    game.connet()

    # Hexadecimal colors (https://htmlcolorcodes.com)
    driver.effectNone()
    time.sleep(3)
    driver.effectStatic("FF00C1")
    time.sleep(3)
    driver.effectCustom("FF0000", "00FF0F", "2700FF", "FF00D4") # 4 slots max
    time.sleep(3)

if __name__ == "__main__":
    main()