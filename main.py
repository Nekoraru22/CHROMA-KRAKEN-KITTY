from Chroma import *
from LoL import *

def test(driver: Driver) -> None:
    """Tests if the color driver works
    Hexadecimal colors - https://htmlcolorcodes.com"""

    driver.effectNone(2)
    driver.effectStatic("FF00C1", 2)
    driver.effectCustom("00FFBD", "00FFBD", "1D6E01", "1D6E01", 5) # 4 slots max


def main(testing: bool =False) -> None:
    """
    {FB357780-4617-43A7-960F-D1190ED54806}
    static const GUID KRAKEN_KITTY=
    { 0xfb357780, 0x4617, 0x43a7,{ 0x96, 0xf, 0xd1, 0x19, 0xe, 0xd5, 0x48, 0x6 } };

    All devices: https://assets.razerzone.com/dev_portal/REST/html/_rz_chroma_s_d_k_defines_8h_source.html
    """
    driver = Driver("devid=FB357780-4617-43A7-960F-D1190ED54806") # Krakken kitty ID

    if testing:
        test(driver)
        return

    game = Partida('127.0.0.1', driver)

    print(driver, end="\n\n")
    game.connet()


if __name__ == "__main__":
    main()